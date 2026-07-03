#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do modulo de digestao in silico (bonder.db.digest).

Nucleo CPU: sem rede, sem pyteomics, sem R. Fixa as invariantes da clivagem
triptica, dos filtros, da proteotipia e da massa monoisotopica.
"""
import json
from pathlib import Path

from bonder.db import digest


def test_trypsin_cleaves_after_k_and_r():
    # SAMPLER: cortes apos K(6) e R(?)... usamos uma sequencia controlada.
    # "AAAAKBBBBRCCCC" -> AAAAK | BBBBR | CCCC  (min_length=1 p/ ver todos)
    peps = digest.cleave("AAAAKBBBBRCCCC", missed_cleavages=0, min_length=1, max_length=100)
    assert "AAAAK" in peps
    assert "BBBBR" in peps
    assert "CCCC" in peps


def test_trypsin_no_cut_before_proline():
    # K seguido de P NAO deve cortar: "AAAAKPBBBR" -> AAAAKPBBBR | (nada apos K)
    peps = digest.cleave("AAAAKPBBBR", missed_cleavages=0, min_length=1, max_length=100)
    assert "AAAAKPBBBR" in peps
    assert "AAAAK" not in peps  # a excecao da prolina impede o corte


def test_missed_cleavages_generate_longer_peptides():
    seq = "AAAKBBBKCCCKDDD"
    zero = set(digest.cleave(seq, missed_cleavages=0, min_length=1, max_length=100))
    two = set(digest.cleave(seq, missed_cleavages=2, min_length=1, max_length=100))
    assert "AAAK" in zero
    # com 2 missed cleavages surge um peptideo que atravessa 2 sitios internos
    assert "AAAKBBBKCCCK" in two
    assert zero.issubset(two)


def test_length_filters_apply():
    peps = digest.cleave("AAAAKBBBBRCCCC", missed_cleavages=0, min_length=5, max_length=5)
    assert "AAAAK" in peps and "BBBBR" in peps
    assert "CCCC" not in peps  # comprimento 4 < min_length


def test_peptide_mass_water_and_residues():
    # Glicina isolada: massa = agua + residuo G
    m = digest.peptide_mass("G", fixed_cys_carbamidomethyl=False)
    assert abs(m - (digest.WATER + digest.MONO_MASS["G"])) < 1e-4
    # Carbamidometilacao fixa adiciona +57.02146 por cisteina
    m_noc = digest.peptide_mass("C", fixed_cys_carbamidomethyl=False)
    m_cam = digest.peptide_mass("C", fixed_cys_carbamidomethyl=True)
    assert abs((m_cam - m_noc) - digest.CARBAMIDOMETHYL) < 1e-4


def test_proteotypic_detection(tmp_path: Path):
    # Duas proteinas compartilham um peptideo triptico; a proteotipia deve refletir.
    # Peptideos escolhidos SEM K/R/P internos para clivar de forma limpa apos K.
    fasta = tmp_path / "toy.fasta"
    shared = "AAAADEFGHIK"   # comum as duas -> nao proteotipico
    uniq1 = "LMNQSTVWYK"     # so na P1 -> proteotipico
    uniq2 = "CDEFGHILMK"     # so na P2 -> proteotipico
    fasta.write_text(
        ">sp|P1|ONE GN=one\n%s%s\n" % (shared, uniq1) +
        ">sp|P2|TWO GN=two\n%s%s\n" % (shared, uniq2),
        encoding="utf-8",
    )
    params = digest.DigestParams(missed_cleavages=0, min_length=5, max_length=50)
    res = digest.digest_proteome(fasta, params=params)
    assert res.n_proteins == 2
    assert set(res.peptide_proteins[shared]) == {"P1", "P2"}  # compartilhado
    assert res.peptide_proteins[uniq1] == ["P1"]              # unico da P1
    assert res.peptide_proteins[uniq2] == ["P2"]              # unico da P2
    assert res.n_proteotypic() == 2


def test_digest_proteome_writes_artifacts(tmp_path: Path):
    fasta = tmp_path / "toy.fasta"
    fasta.write_text(
        ">sp|P1|ONE GN=alpha\nMKAAAAKBBBBRCCCCKDDDDR\n"
        ">sp|P2|TWO GN=beta\nSHAREDKMMMMMKR\n",
        encoding="utf-8",
    )
    params = digest.DigestParams(missed_cleavages=1, min_length=3, max_length=50)
    res = digest.digest_proteome(fasta, params=params)
    paths = digest.write_digest(res, tmp_path / "out", source_info={"test": True})
    for key in ("peptides", "protein_index", "profile", "manifest"):
        assert paths[key].exists(), key
    header = (tmp_path / "out" / "peptides.tsv").read_text(encoding="utf-8").splitlines()[0]
    assert header.split("\t") == ["peptide", "length", "mono_mass", "n_missed",
                                  "n_proteins", "proteotypic", "proteins"]
    prof = json.loads((tmp_path / "out" / "digest_profile.json").read_text(encoding="utf-8"))
    assert prof["n_proteins"] == 2
    assert prof["n_peptides_unique_sequences"] == res.n_peptides()
    assert 0.0 <= prof["proteotypic_fraction"] <= 1.0


def test_count_missed_internal_sites():
    # AAKBBR: K interno (missed=1) + R no C-terminal (nao conta)
    assert digest._count_missed("AAKBBR", "trypsin") == 1
    # AAR: apenas R no C-terminal -> 0 missed
    assert digest._count_missed("AAR", "trypsin") == 0
