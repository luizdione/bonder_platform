# Conhecimento do Projeto - bonder-src (PMM - KNOWLEDGE.md)

> **Nivel 2.** Conhecimento duravel: comportamento de APIs, limitacoes, boas
> praticas, solucoes de bugs recorrentes, links internos. **Nunca** registrar
> conversa. Consultar sob demanda.

## APIs / comportamento
- **SAINTexpress** nao existe como pacote conda: e **compilado do fonte**
  (SourceForge, requer g++ + libgsl-dev) no `docker/Dockerfile.analysis`,
  best-effort e **nao-fatal**. Fallback: binario Linux `SAINTexpress-int` em
  `vendor/bin/` (montado em `/opt/bonder/bin`, no PATH) - nao exige rebuild.
- **DIA-NN:** mapear peptideos/q-value pela coluna `Protein.Group` **original**;
  MaxLFQ nunca e re-normalizado.
- **UniProt/STRING/BioGRID:** baixados por stream REST fixado por versao; o
  downloader e content-addressed e **falha** se o sha256 divergir do esperado.
- **Redis/RQ:** se indisponivel, os jobs caem para execucao **em thread** (sem fila).

## Limitacoes conhecidas
- Sem SAINT-binario ou sem R, os passos `saint`/`dep` aparecem como **"pulado"** no
  autoteste/manifesto (comportamento esperado em CPU puro, nao e erro).
- `data/`, `runs/`, `inputs/` e `config/sequences/*.fasta` sao **ignorados no git**
  (`.gitignore`) e reproduzidos localmente; nao esperar dados versionados.

## Boas praticas (deste projeto)
- Alterar comportamento por **YAML** (`config/*.yaml`), nao por hardcode.
- Verificar ausencia com `pandas.isna`/checagem explicita - **NaN e "truthy"** em
  Python (ver bug abaixo). Nunca usar 0 para "ausente".
- Escopo: o bonder trata **exclusivamente PPI por espectrometria de massas**
  (CoIP-MS/AP-MS). Nao introduzir codigo/conceitos de docking molecular. Novo
  comportamento nasce e vive **neste repositorio** (`luizdione/bonder`).

## Solucoes para bugs recorrentes
- **Sintoma:** SAINT grava o literal `nan` no lugar do gene -> **Causa:** NaN e
  truthy, o fallback de gene nao disparava -> **Correcao:** testar NaN
  explicitamente e cair para o acesso UniProt.
- **Sintoma:** coluna `log2fc` vazia no dashboard -> **Causa:** R ausente (sem
  DEP/limma) -> **Correcao:** usar `log2fc_descriptive`; o polling para em status
  terminal (`done`/`error`).
- **Sintoma:** job de testes quebra por `requests` faltando -> **Correcao:** manter
  `requests` nas deps de CI.

## Referencias internas
- `docs/METODOLOGIA.md` (citacoes/licencas das ferramentas), `docs/REPRODUTIBILIDADE.md`,
  `docs/COMO_RODAR.md`.
- Changelog canonico: `../CHANGELOG.md` (raiz do repo).
- `vendor/README.md` (como obter/compilar o SAINTexpress-int).
