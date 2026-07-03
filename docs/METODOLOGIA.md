# Metodologia cientifica e citacoes

Este documento descreve o metodo do `bonder` e as referencias das ferramentas
orquestradas. Todo escore que sustenta uma conclusao vem de uma ferramenta
**publicada e revisada por pares** — nada e reimplementado.

## 1. Desenho

- **Amostra:** *Mus musculus* (taxid 10090), macrofagos murinos in vitro.
- **Iscas (exogenas):** NSs do ortobunyavirus *Icoaraci* (viral) e Galectina-3
  humana (LGALS3, P17931). Parceiros = proteinas murinas (host).
- **NSs — PROTEOMA SUBTRATIVO:** o desenho da isca viral **nao** e uma co-IP com
  anticorpo anti-tag classica, e sim **subtrativo**: comparam-se **macrofagos
  murinos superexpressando NSs** (teste, `IP_NSs`) contra **macrofagos murinos
  wild-type (WT)** (`CTRL_NSs`), que definem o **threshold negativo** (background).
  O parceiro candidato de NSs e a proteina murina **enriquecida na superexpressao
  e ausente/reduzida no WT**. SAINT/MiST quantificam a especificidade sobre esse
  delta; DEP/limma dao o enriquecimento diferencial de suporte.
- **LGALS3:** co-IP de especificidade classica (isca vs controle pareado), **tambem
  em sistema murino** (host).
- **Controles:** para NSs, macrofagos WT (threshold subtrativo); para LGALS3,
  controle pareado (IgG/mock/parental) murino.
- **Replicas:** recomenda-se **>= 3 biologicas** por grupo. Com n=2-4, a decisao
  prioriza especificidade (SAINT/MiST) e presenca/ausencia vs controle, com o
  quantitativo (DEP/limma) como suporte.
- O desenho por isca esta declarado em `config/baits.yaml` (`design.strategy`) e
  `config/samples.yaml` (`design`, `contrasts[].strategy`).

## 2. Ingesta e QC

- Parsers por motor (MaxQuant/DIA-NN/FragPipe/generico) -> matriz unica
  (`MSDataset`), **chaveada pelo acesso UniProt lider**, com **ausente = NaN**
  (0 do MaxQuant/FragPipe convertido para NaN em DDA; MaxLFQ do DIA-NN **nao** e
  re-normalizado).
- Contaminantes/decoys sinalizados por coluna booleana **e** por prefixo
  (`CON__`/`REV__`/`contam_`); iscas nunca sao tratadas como contaminante.
- QC: valores validos por amostra/condicao, correlacao entre replicas, log2.

## 2b. Base de digestao in silico murina (peptideo -> proteina)

Para interpretar o delta subtrativo com rigor, o `bonder` mantem o **espaco
peptidico teorico murino** — os peptideos que um motor de busca consideraria a
partir do proteoma de referencia. E gerado por **digestao enzimatica in silico**
(`bonder/db/digest.py`; `bonder db digest`) e serve de referencia para:

- **mapeamento peptideo -> proteina** e a **razor/unique** do SAINT;
- **proteotipia** (peptideo atribuivel a **UMA** proteina) — essencial para
  distinguir a isca humana LGALS3 (P17931) do ortologo murino Lgals3 (P16110):
  peptideos compartilhados **nao** sao proteotipicos e sao sinalizados;
- leitura do **background/threshold** do desenho subtrativo (universo esperado no
  WT vs superexpressao).

Parametros (declarados em `config/databases.yaml -> proteome_murine.digestion`):
enzima **tripsina** (corta apos K/R, exceto antes de P), **2 missed cleavages**,
comprimento **7-50** residuos, **carbamidometilacao fixa** em cisteina (mod padrao
de iodoacetamida); massa **monoisotopica** por residuo (Unimod/IUPAC). A regra de
clivagem segue as expressoes canonicas de ferramentas consagradas
(`pyteomics.parser`); a digestao e uma operacao **deterministica**, nao um
algoritmo de escore reimplementado.

A base fica **fora do repositorio** (dado grande) em `proteome_murine.out_root`
(ambiente do autor: `E:/data/proteome_murine`), com `peptides.tsv`,
`protein_index.tsv`, `digest_profile.json` e `digest_manifest.json` (proveniencia:
sha256 da fonte, versao do proteoma, parametros).

## 3. Especificidade isca-presa (nucleo do CoIP)

- **SAINTexpress** (Teo et al., *J Proteomics* 2014; Choi et al., *Nat Methods*
  2011) — probabilidade SAINT + **BFDR** por prey vs controles. Padrao de fato
  em AP-MS. Iscas exogenas sao excluidas do conjunto de preys murinos.
- **MiST** (Verschueren et al., 2015; Jager et al., *Nature* 2011) — combina
  reprodutibilidade, abundancia e especificidade; recomendado para a **isca
  viral NSs** (paradigma host-pathogen, ex.: Gordon et al., *Nature* 2020).

## 4. Quantitativo diferencial

- **DEP** (Zhang et al., *Nat Protoc* 2018) — enriquecimento diferencial em
  nivel de proteina: filtragem, normalizacao **vsn**, imputacao MNAR
  (**MinProb**) e teste via **limma** (Ritchie et al., *NAR* 2015; teste-t
  moderado por Bayes empirico). Ideal para matrizes de proteinGroups.
- **MSstats** (Choi et al., *Bioinformatics* 2014) — quando ha dados em nivel de
  feature (evidence/report), usando os conversores oficiais.

## 5. Background / contaminantes

- **CRAPome** (Mellacheruvu et al., *Nat Methods* 2013) — frequencia de background;
  aqui priorizamos a frequencia observada nos **proprios controles** do usuario.

## 6. Anotacao e rede

- **UniProt** (proteoma murino), **STRING v12.0** (Szklarczyk et al.), **BioGRID**
  (Oughtred et al.), GO via **g:Profiler** (Kolberg et al.). Rede exportada em
  GraphML/Cytoscape (Shannon et al., *Genome Res* 2003).

## 7. GPU (opcional, RTX 3060)

- **DIA-NN** (Demichev et al., *Nat Methods* 2020) — busca DIA acelerada.
- **MS2Rescore** (Declercq et al.) + **AlphaPeptDeep** (Zeng et al., *Nat
  Commun* 2022) — rescoring por deep learning; +IDs a FDR fixo.
- **AlphaFold2-Multimer** (Evans et al.) / **ColabFold** (Mirdita et al., *Nat
  Methods* 2022) — validacao estrutural isca-presa dos melhores candidatos.
- **ESM2** (Lin et al., *Science* 2023) — priorizacao **exploratoria/suplementar**;
  nunca a base do escore de confianca.

## 8. Ranqueamento final

Interatores ordenados por **BFDR (SAINT)**, depois **FDR (DEP/limma)**; os
descritivos (fold change de medias, contagem de observados) entram apenas como
QC/desempate. Rotulo de confianca: alta (BFDR <= 0.05), media (<= 0.10), baixa.

## 9. Reporte para publicacao

Depositar dados brutos no **ProteomeXchange/PRIDE**; reportar versoes das
ferramentas (do `manifest.json`), parametros de busca, criterios de FDR e o
desenho de replicas/controles. Ver `docs/REPRODUTIBILIDADE.md`.
