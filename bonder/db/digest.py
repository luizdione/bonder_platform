#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""digest.py - digestao enzimatica IN SILICO do proteoma murino de referencia.

Gera o ESPACO PEPTIDICO TEORICO de um proteoma (o mesmo conjunto de peptideos que
um motor de busca consideraria): dado um FASTA, aplica a regra de clivagem de uma
protease (por padrao tripsina) com um numero maximo de missed cleavages, filtra por
comprimento/massa e devolve, para cada peptideo, a massa monoisotopica, quantas
proteinas o contem e se ele e PROTEOTIPICO (unico de uma unica proteina).

Por que isto entra no bonder (metodologia SUBTRATIVA):
  - A isca viral NSs e estudada por PROTEOMA SUBTRATIVO: macrofagos murinos
    superexpressando NSs (teste) contra macrofagos wild-type (WT, threshold
    negativo). O parceiro candidato e o que sobe no teste e nao no WT.
  - Para interpretar esse delta com rigor precisamos do "universo" de peptideos
    murinos esperados: quais peptideos sao detectaveis, quais sao proteotipicos
    (atribuiveis a UMA proteina) e como se distribuem em massa/comprimento. Essa
    base (peptideo -> proteina) sustenta o mapeamento peptideo->proteina, a
    razor/unique do SAINT e a leitura de background do WT.

Filosofia (ver docs/METODOLOGIA.md): a digestao in silico e uma OPERACAO
DETERMINISTICA e padronizada (nao um algoritmo de escore reimplementado). As
regras de clivagem seguem as expressoes canonicas usadas por ferramentas
consagradas (pyteomics.parser); quando o pyteomics esta instalado, o resultado
pode ser cruzado com ele via `cleave(..., prefer_pyteomics=True)`.

Saidas de digest_proteome() (gravadas em out_dir, ex.: E:/data/proteome_murine):
  peptides.tsv          peptideo, comprimento, massa_monoisotopica, n_missed,
                        n_proteinas, proteotipico, proteinas (lista ';')
  protein_index.tsv     accession, gene, comprimento, n_peptideos, n_proteotipicos
  digest_profile.json   perfil resumido (contagens, fracao proteotipica, hist.)
  digest_manifest.json  parametros + proveniencia (sha256 da fonte, versao, data)
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from bonder.db.uniprot import iter_fasta

# ---------------------------------------------------------------------------
# Massas monoisotopicas dos residuos (Da) e constantes. Fonte: Unimod/IUPAC.
# ---------------------------------------------------------------------------
MONO_MASS: Dict[str, float] = {
    "G": 57.02146, "A": 71.03711, "S": 87.03203, "P": 97.05276,
    "V": 99.06841, "T": 101.04768, "C": 103.00919, "L": 113.08406,
    "I": 113.08406, "N": 114.04293, "D": 115.02694, "Q": 128.05858,
    "K": 128.09496, "E": 129.04259, "M": 131.04049, "H": 137.05891,
    "F": 147.06841, "R": 156.10111, "Y": 163.06333, "W": 186.07931,
    # ambiguidades: usa a menor massa plausivel (nao contam para proteotipia)
    "U": 150.95364,  # selenocisteina
    "O": 237.14773,  # pirrolisina
}
WATER = 18.010565            # H2O (massa monoisotopica)
CARBAMIDOMETHYL = 57.02146   # +CH2CONH2 em cisteina (iodoacetamida) - mod fixa padrao

# Regras de clivagem canonicas (regex sobre a sequencia; a posicao APOS o match
# e um sitio de corte). Espelham as expressoes de pyteomics.parser.expasy_rules.
ENZYME_RULES: Dict[str, str] = {
    "trypsin": r"[KR](?!P)",       # corta apos K/R, exceto se seguido de P
    "trypsin/p": r"[KR]",          # tripsina sem a excecao da prolina
    "lys-c": r"K(?!P)",
    "arg-c": r"R(?!P)",
    "chymotrypsin": r"[FYWL](?!P)",
    "glu-c": r"[DE](?!P)",
    "asp-n": r"(?=[BD])",          # corta ANTES de D (lookahead) - caso especial
}


@dataclass
class DigestParams:
    """Parametros da digestao (tudo que precisa ir para o manifesto)."""
    enzyme: str = "trypsin"
    missed_cleavages: int = 2
    min_length: int = 7
    max_length: int = 50
    min_mass: Optional[float] = None
    max_mass: Optional[float] = None
    fixed_cys_carbamidomethyl: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enzyme": self.enzyme,
            "missed_cleavages": self.missed_cleavages,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "min_mass": self.min_mass,
            "max_mass": self.max_mass,
            "fixed_cys_carbamidomethyl": self.fixed_cys_carbamidomethyl,
        }


# ---------------------------------------------------------------------------
# Clivagem
# ---------------------------------------------------------------------------
def _rule_regex(enzyme: str) -> str:
    key = enzyme.strip().lower()
    if key not in ENZYME_RULES:
        raise ValueError(
            "Enzima desconhecida: %r. Disponiveis: %s"
            % (enzyme, ", ".join(sorted(ENZYME_RULES)))
        )
    return ENZYME_RULES[key]


def _cut_sites(sequence: str, regex: str) -> List[int]:
    """Fronteiras de corte (inclui 0 e len(seq)); posicao = indice APOS o residuo."""
    sites = [0]
    for m in re.finditer(regex, sequence):
        # lookahead puro (asp-n) casa comprimento 0: o corte fica ANTES do residuo
        pos = m.start() if m.end() == m.start() else m.end()
        if 0 < pos < len(sequence):
            sites.append(pos)
    if sites[-1] != len(sequence):
        sites.append(len(sequence))
    return sites


def cleave(
    sequence: str,
    enzyme: str = "trypsin",
    missed_cleavages: int = 2,
    min_length: int = 7,
    max_length: int = 50,
    prefer_pyteomics: bool = False,
) -> List[str]:
    """Peptideos teoricos de uma sequencia (0..missed_cleavages missed cleavages).

    Deterministico e independente da ordem. Filtra por comprimento (residuos).
    Com prefer_pyteomics=True e pyteomics instalado, delega para
    pyteomics.parser.cleave (cross-check). O resultado e o mesmo conjunto.
    """
    seq = re.sub(r"[^A-Z]", "", (sequence or "").upper())
    if not seq:
        return []

    if prefer_pyteomics:
        try:
            from pyteomics import parser as _pp  # type: ignore
            rule = _rule_regex(enzyme)
            peps = _pp.cleave(seq, rule, missed_cleavages=missed_cleavages)
            return sorted(p for p in peps if min_length <= len(p) <= max_length)
        except Exception:
            pass  # sem pyteomics -> cai no interno

    sites = _cut_sites(seq, _rule_regex(enzyme))
    out: List[str] = []
    seen: set = set()
    n = len(sites)
    for i in range(n - 1):
        # j-i-1 sitios internos pulados == missed cleavages
        for j in range(i + 1, min(i + 1 + missed_cleavages + 1, n)):
            pep = seq[sites[i]:sites[j]]
            length = len(pep)
            if min_length <= length <= max_length and pep not in seen:
                seen.add(pep)
                out.append(pep)
    return out


def peptide_mass(peptide: str, fixed_cys_carbamidomethyl: bool = True) -> float:
    """Massa monoisotopica neutra do peptideo (soma dos residuos + agua).

    Residuos desconhecidos sao ignorados na soma (retornam massa parcial); use
    is_canonical() para excluir peptideos com residuos ambiguos quando necessario.
    """
    total = WATER
    for aa in peptide:
        total += MONO_MASS.get(aa, 0.0)
        if aa == "C" and fixed_cys_carbamidomethyl:
            total += CARBAMIDOMETHYL
    return round(total, 5)


def is_canonical(peptide: str) -> bool:
    """True se todos os residuos sao aminoacidos padrao (sem X/B/Z/ambiguos)."""
    return all(aa in MONO_MASS and aa not in ("U", "O") for aa in peptide)


# ---------------------------------------------------------------------------
# Digestao de um proteoma inteiro (mapa peptideo -> proteinas)
# ---------------------------------------------------------------------------
@dataclass
class DigestResult:
    """Resultado agregado da digestao de um proteoma."""
    params: DigestParams
    peptide_proteins: Dict[str, List[str]] = field(default_factory=dict)  # peptideo -> [accessions]
    protein_peptides: Dict[str, int] = field(default_factory=dict)        # accession -> n peptideos
    protein_meta: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # accession -> {gene,length}
    n_proteins: int = 0

    def n_peptides(self) -> int:
        return len(self.peptide_proteins)

    def n_proteotypic(self) -> int:
        return sum(1 for accs in self.peptide_proteins.values() if len(accs) == 1)


def _header_gene(header: str) -> str:
    m = re.search(r"\bGN=(\S+)", header or "")
    return m.group(1) if m else ""


def digest_proteome(
    fasta_path,
    params: Optional[DigestParams] = None,
    max_proteins: Optional[int] = None,
) -> DigestResult:
    """Digere um FASTA inteiro na memoria, devolvendo o mapa peptideo->proteinas.

    max_proteins limita a leitura (util em teste). A proteotipia (peptideo unico
    de UMA proteina) so e correta apos ler o proteoma inteiro, entao e resolvida
    no fim, sobre o mapa completo.
    """
    params = params or DigestParams()
    res = DigestResult(params=params)
    pep_prot: Dict[str, set] = {}

    count = 0
    for acc, header, seq in iter_fasta(fasta_path):
        count += 1
        peps = cleave(
            seq, enzyme=params.enzyme, missed_cleavages=params.missed_cleavages,
            min_length=params.min_length, max_length=params.max_length,
        )
        kept = 0
        for pep in peps:
            if params.min_mass is not None or params.max_mass is not None:
                m = peptide_mass(pep, params.fixed_cys_carbamidomethyl)
                if params.min_mass is not None and m < params.min_mass:
                    continue
                if params.max_mass is not None and m > params.max_mass:
                    continue
            pep_prot.setdefault(pep, set()).add(acc)
            kept += 1
        res.protein_peptides[acc] = kept
        res.protein_meta[acc] = {"gene": _header_gene(header), "length": len(seq)}
        if max_proteins is not None and count >= max_proteins:
            break

    res.n_proteins = count
    # congela os sets em listas ordenadas (proveniencia estavel)
    res.peptide_proteins = {p: sorted(accs) for p, accs in pep_prot.items()}
    return res


def profile(res: DigestResult) -> Dict[str, Any]:
    """Perfil resumido da digestao (o 'perfil de digestao' do proteoma)."""
    n_pep = res.n_peptides()
    n_proteo = res.n_proteotypic()
    per_protein = sorted(res.protein_peptides.values())
    proteo_per_protein: Dict[str, int] = {}
    for accs in res.peptide_proteins.values():
        if len(accs) == 1:
            proteo_per_protein[accs[0]] = proteo_per_protein.get(accs[0], 0) + 1

    def _median(xs: List[int]) -> float:
        if not xs:
            return 0.0
        k = len(xs)
        mid = k // 2
        return float(xs[mid]) if k % 2 else (xs[mid - 1] + xs[mid]) / 2.0

    # histograma grosseiro de comprimento (para leitura rapida no dashboard)
    len_hist: Dict[str, int] = {}
    for pep in res.peptide_proteins:
        b = "%d-%d" % ((len(pep) // 5) * 5, (len(pep) // 5) * 5 + 4)
        len_hist[b] = len_hist.get(b, 0) + 1

    proteins_with_proteotypic = sum(1 for a in res.protein_peptides if proteo_per_protein.get(a, 0) > 0)
    return {
        "params": res.params.to_dict(),
        "n_proteins": res.n_proteins,
        "n_peptides_unique_sequences": n_pep,
        "n_proteotypic_peptides": n_proteo,
        "proteotypic_fraction": round(n_proteo / n_pep, 4) if n_pep else 0.0,
        "peptides_per_protein": {
            "min": per_protein[0] if per_protein else 0,
            "median": _median(per_protein),
            "max": per_protein[-1] if per_protein else 0,
        },
        "proteins_without_proteotypic_peptide": res.n_proteins - proteins_with_proteotypic,
        "length_histogram": dict(sorted(len_hist.items())),
    }


def write_digest(res: DigestResult, out_dir, source_info: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
    """Grava peptides.tsv, protein_index.tsv, digest_profile.json e manifest.

    Retorna dict com os caminhos escritos. peptides.tsv e escrito em streaming
    (pode ter centenas de milhares de linhas).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = res.params

    # --- peptides.tsv (streaming) ---
    peptides_path = out / "peptides.tsv"
    with open(peptides_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("peptide\tlength\tmono_mass\tn_missed\tn_proteins\tproteotypic\tproteins\n")
        for pep in sorted(res.peptide_proteins):
            accs = res.peptide_proteins[pep]
            mass = peptide_mass(pep, p.fixed_cys_carbamidomethyl)
            n_missed = _count_missed(pep, p.enzyme)
            proteotypic = "1" if len(accs) == 1 else "0"
            fh.write("%s\t%d\t%.5f\t%d\t%d\t%s\t%s\n"
                     % (pep, len(pep), mass, n_missed, len(accs), proteotypic, ";".join(accs)))

    # --- protein_index.tsv ---
    proteo_per_protein: Dict[str, int] = {}
    for accs in res.peptide_proteins.values():
        if len(accs) == 1:
            proteo_per_protein[accs[0]] = proteo_per_protein.get(accs[0], 0) + 1
    protein_index_path = out / "protein_index.tsv"
    with open(protein_index_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("accession\tgene\tlength\tn_peptides\tn_proteotypic\n")
        for acc in sorted(res.protein_peptides):
            meta = res.protein_meta.get(acc, {})
            fh.write("%s\t%s\t%d\t%d\t%d\n"
                     % (acc, meta.get("gene", ""), int(meta.get("length", 0)),
                        res.protein_peptides[acc], proteo_per_protein.get(acc, 0)))

    # --- profile + manifest ---
    prof = profile(res)
    profile_path = out / "digest_profile.json"
    profile_path.write_text(json.dumps(prof, indent=2, ensure_ascii=True), encoding="utf-8")

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "params": p.to_dict(),
        "source": source_info or {},
        "n_proteins": res.n_proteins,
        "n_peptides_unique_sequences": res.n_peptides(),
        "n_proteotypic_peptides": res.n_proteotypic(),
        "residue_mass_source": "monoisotopic (Unimod/IUPAC)",
        "cleavage_rule": ENZYME_RULES.get(p.enzyme.lower()),
        "note": "Espaco peptidico teorico (in silico). NAO substitui peptideos "
                "observados; serve de referencia para mapeamento e proteotipia.",
    }
    manifest_path = out / "digest_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")

    return {
        "peptides": peptides_path,
        "protein_index": protein_index_path,
        "profile": profile_path,
        "manifest": manifest_path,
    }


def _count_missed(peptide: str, enzyme: str) -> int:
    """Numero de missed cleavages internos de um peptideo (sitios nao no C-terminal)."""
    regex = _rule_regex(enzyme)
    internal = 0
    for m in re.finditer(regex, peptide):
        pos = m.start() if m.end() == m.start() else m.end()
        if 0 < pos < len(peptide):  # sitio de corte interno = missed
            internal += 1
    return internal
