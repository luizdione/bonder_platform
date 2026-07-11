# Decisoes Tecnicas - bonder-src (PMM - DECISIONS.md)

> **Nivel 2.** Apenas decisoes **relevantes** (ADR-lite). Mais recente no topo.
> Decisoes superadas podem ser consolidadas e movidas para `archive/decisions/`.

## 2026-07-03 - Instrumento Q Exactive HF-X + aquisicao DIA  [D-0005]
- **Status:** aceita (a confirmar com a plataforma de MS).
- **Contexto:** parceiros de CoIP sao sub-estequiometricos/baixa abundancia; o
  delta subtrativo NSs-vs-WT exige sensibilidade e boa quantificacao.
- **Alternativas:** Q Exactive Plus (2013, workhorse DDA) - menos IDs, mais valores
  ausentes; DDA (MaxQuant/FragPipe) como 2a opcao se a plataforma nao ofertar DIA.
- **Consequencias:** HF-X (fonte ion funnel, ~top-20-40) + **DIA-NN (GPU)** reduz
  NaN e melhora reprodutibilidade para SAINT/MiST e comparacao subtrativa.
- **Arquivos:** `formularios/RECOMENDACAO_instrumento.md`, `formularios/*895*`.

## 2026-07-02 - Iscas exogenas distintas do ortologo murino  [D-0004]
- **Status:** aceita.
- **Contexto:** as 2 iscas nao pertencem ao proteoma murino (host). Colapsar a
  isca humana LGALS3 (P17931) com o ortologo murino `Lgals3` (P16110) mascararia
  um achado legitimo (Lgals3 murino co-precipitado).
- **Consequencias:** iscas nunca entram como preys no denominador murino do
  scoring; peptideos compartilhados P17931/P16110 sao sinalizados.
- **Arquivos:** `config/baits.yaml`, `bonder/io/*`, `bonder/scoring/*`.

## 2026-07-02 - Quantificacao: ausente=NaN e MaxLFQ nao re-normalizado  [D-0003]
- **Status:** aceita.
- **Contexto:** zero-imputacao e re-normalizacao de MaxLFQ introduzem vies em AP-MS.
- **Consequencias:** ausencia = NaN (nunca 0); MaxLFQ do DIA-NN e usado como vem;
  QC em Python nao tem valor inferencial (inferencia so no R: DEP/limma/MSstats).

## 2026-07-02 - Nucleo cientifico testavel em CPU; etapas faltantes puladas  [D-0002]
- **Status:** aceita.
- **Contexto:** GPU (RTX 3060) e R/Bioconductor nem sempre presentes (CI, outras
  maquinas). Precisamos de reprodutibilidade honesta.
- **Consequencias:** io/scoring-formatacao/annotate/pipeline rodam sem GPU/R (o que
  a CI exercita); ferramenta ausente -> passo "pulado" **registrado no manifesto**,
  nunca fingido. GPU compartilha a placa com o Ollama via `gpu_gate` cooperativo.

## 2026-07-02 - Orquestrar ferramentas consagradas (nao reinventar)  [D-0001]
- **Status:** aceita.
- **Contexto:** publicabilidade vem de metodos validados/citaveis + FDR + replicas
  + deposito, nao de codigo proprio de scoring.
- **Consequencias:** bonder orquestra SAINTexpress/MiST/MSstats/DEP/limma/DIA-NN em
  conteineres; ESM2/embeddings so como priorizacao **suplementar**, nunca base do
  escore principal. Bancos fixados por versao + sha256.
- **Arquivos:** `README.md`, `bonder/__init__.py`, `docs/METODOLOGIA.md`.
