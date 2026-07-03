# Changelog - bonder

Todas as mudancas relevantes da plataforma. Formato baseado em
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versionamento
[SemVer](https://semver.org/lang/pt-BR/).

## [Nao lancado]

## [0.3.0] - 2026-07-02

Versao **hospedada** e leve (Bonder Viewer): publica os resultados num site
estatico (ex.: Hostinger, atras de senha) para **visualizacao e edicao/curadoria**,
sem levar a analise pesada (pipeline/R/GPU/Redis) para o servidor.

### Adicionado
- **Bonder Viewer** (`bonder/web/viewer/index.html`): dashboard estatico (HTML/JS
  puro) que le os resultados como **arquivos estaticos** (sem API/Flask). Abas
  Resumo/QC, Interatores, Volcano, Rede (Cytoscape) e Ajuda. Libs **vendorizadas**
  (`cytoscape`, `marked` em `viewer/lib/`) — self-contained, sem CDN, funciona
  atras de Basic Auth/offline. Rede renderizada de forma **lazy** (so na aba Rede).
- **Camada de edicao/curadoria** no viewer: por interator, marcar *validado*,
  definir *confianca curada* e *nota*; persistido no navegador (localStorage),
  com **exportar/importar JSON** e **baixar TSV** (interatores + curadoria).
- **Exportador de bundle** (`bonder.web.export.export_bundle`) + CLI
  **`bonder export --out DIR`**: empacota o viewer + `runs/` (results/interactors/
  network/volcano) + `docs/` + `config.json` num diretorio publicavel. Flags
  `--run` (subset) e `--no-viewer` (so dados).
- **Assets de deploy Hostinger**: `.htaccess` (MIME + no-indexes + cache; bloco de
  Basic Auth comentado, seguro por padrao) e `README_DEPLOY.md` (subdominio,
  document root, protecao por senha via hPanel, upload, atualizacao).
- Empacotamento: `package-data` inclui `web/viewer/*` e `web/templates/*`.
- **Testes** `tests/test_web_export.py` (bundle completo, filtro `--run`, `--no-viewer`).

## [0.2.0] - 2026-07-02

Metodologia **subtrativa** para a isca viral NSs e base de **digestao in silico**
murina (espaco peptidico teorico peptideo -> proteina).

### Adicionado
- **Digestao in silico (`bonder.db.digest`)**: gera o espaco peptidico teorico do
  proteoma murino (regras de protease canonicas — tripsina por padrao, corta apos
  K/R exceto antes de P), com missed cleavages, filtros de comprimento/massa,
  **massa monoisotopica** (Unimod/IUPAC, carbamidometilacao fixa em C) e deteccao
  de peptideos **proteotipicos** (unicos de UMA proteina). API: `cleave`,
  `peptide_mass`, `digest_proteome`, `write_digest`, `profile`.
- **CLI `bonder db digest`**: baixa o proteoma murino (reusa o cache ou verifica
  por sha256) e grava `peptides.tsv`, `protein_index.tsv`, `digest_profile.json` e
  `digest_manifest.json` em `proteome_murine.out_root` (default `E:/data/proteome_murine`;
  sobrescrevivel por `--out` ou `BONDER_PROTEOME_MURINE`). Flags `--max-proteins`.
- **Config `proteome_murine`** em `config/databases.yaml`: raiz de saida, fonte do
  proteoma e parametros de digestao (enzima, missed cleavages, comprimento, massa,
  mod fixa de cisteina).
- **Desenho por isca declarativo**: `config/baits.yaml` ganha `design.strategy`
  (`subtractive` para NSs — macrofagos superexpressando NSs vs WILD-TYPE como
  threshold negativo; `ap_ms_specificity` para LGALS3, host murino) e
  `config/samples.yaml` ganha o bloco `design` + `contrasts[].strategy`.
- **Auditoria**: `bonder.web.health.check_digest` reporta a base de digestao
  (existencia, n_proteinas, n_peptideos, fracao proteotipica) na aba Manutencao.
- **Testes** `tests/test_digest.py` (clivagem, excecao da prolina, missed
  cleavages, filtros, proteotipia, massa monoisotopica, gravacao ponta-a-ponta).

### Alterado
- `docs/METODOLOGIA.md`: desenho **subtrativo** de NSs (macrofagos superexpressando
  vs WT) e a secao 2b da base de digestao murina; `docs/COMO_RODAR.md`: comando
  `db digest`.

## [0.1.1] - 2026-07-02

Sincronizacao pos-0.1.0 com o upstream `docking_suite` (convencoes Flask v2,
`gpu_gate`, PowerShell helpers), sem quebra de API.

### Adicionado
- **Escotilha `vendor/`**: `docker-compose.yml` monta `./vendor/bin` em
  `/opt/bonder/bin` (PATH do conteiner de analise). Basta colocar um binario
  Linux `SAINTexpress-int` em `vendor/bin/` quando o compile no build ficar
  `pulado`, sem rebuild da imagem. Ver `vendor/README.md`.
- **Helpers PowerShell (Windows 11):** `iniciar_bonder.ps1` (sobe o dashboard),
  `criar_atalho.ps1` (atalho de menu iniciar), `sync.ps1` (sincroniza com o
  upstream). Complementam `run.ps1`, `run-gpu.ps1` e `stop.ps1`.
- **CLI:** novos comandos utilitarios em `bonder.cli` (herdados do docking_suite).
- **Auditoria (`bonder.web.health`)**: relatorio de sanidade ampliado (mais
  ferramentas, versao de R/Bioconductor, mais avisos de config).

### Corrigido
- **Parsers (`bonder.io.schema`)**: normalizacao e coercao de tipos mais estrita
  no `MSDataset`, coberta por novos casos em `tests/test_io_parsers.py`.
- **Dockerfile.analysis**: cadeia de build de R + SAINTexpress consolidada,
  reduzindo modos-fantasma de `saint: pulado` no autoteste.
- **`.gitignore`**: entradas do fluxo docking_suite portadas.
- **Documentacao (`docs/COMO_RODAR.md`)**: instrucoes atualizadas para o
  autoteste dentro do conteiner e uso do `vendor/bin/`.

## [0.1.0] - 2026-07-02

Primeira versao do subprojeto `bonder` (plataforma CoIP-MS / AP-MS para
identificacao de parceiros no proteoma murino).

### Adicionado
- **Ingesta (`bonder.io`)**: parsers MaxQuant/DIA-NN/FragPipe/generico para um
  `MSDataset` unificado; deteccao automatica de motor e aquisicao (DDA/DIA);
  ausente = NaN (nunca 0); chave por acesso UniProt lider; iscas exogenas
  marcadas e mantidas distintas do ortologo murino.
- **Especificidade (`bonder.scoring`)**: formatacao de entrada + wrappers de
  **SAINTexpress** (todas as iscas) e **MiST** (isca viral NSs, host-pathogen).
- **Quantitativo (`bonder.stats`)**: wrappers R para **DEP/limma/MSstats**
  (Bioconductor) via Rscript; QC em Python (sem valor inferencial). MaxLFQ do
  DIA-NN nunca e re-normalizado.
- **Bancos (`bonder.db`)**: UniProt/STRING/BioGRID/cRAP murinos com cache
  reproduzivel (checksum, modo offline) + montagem do `search_db.fasta`.
- **GPU (`bonder.gpu`)**: DIA-NN / MS2Rescore / AlphaPeptDeep / AlphaFold e ESM2
  (suplementar), com fallback CPU e `gpu_gate` cooperativo (compartilha a placa
  com o Ollama).
- **Pipeline + Web**: orquestrador, relatorio (tabela/volcano/rede), dashboard
  Flask + fila RQ/Redis (fallback thread).
- **Docker**: imagem de analise (Python + R + SAINT) e imagem GPU (CUDA 12.4 +
  torch); `docker compose` CPU por padrao + overlay de GPU (RTX 3060).
- **Aba Manutencao**: auditoria (deps, ferramentas, R, GPU, config, bancos,
  caminhos, corridas) + autoteste do pipeline em dados sinteticos.
- **Aba Ajuda e Tutoriais**: serve os documentos `.md` (tutoriais, metodologia,
  reprodutibilidade, versionamento) e a licenca, renderizados no navegador.
  Endpoints `GET /api/docs` e `GET /api/docs/<id>`.
- Documentacao PT-BR (metodologia com citacoes, como rodar, reprodutibilidade)
  e testes do nucleo (CPU, sem GPU/R).

### Corrigido
- `saint` nao existe como pacote conda: removido do env; SAINTexpress agora e
  compilado do codigo-fonte (SourceForge) no Dockerfile, best-effort e nao-fatal.
- Mapeamento de peptideos/q-value do DIA-NN pela `Protein.Group` original.
- Fallback de gene no SAINT gravava o literal `nan` (NaN e truthy) -> cai para o acesso.
- Dashboard: coluna log2fc vazia sem R -> usa `log2fc_descriptive`; o polling
  agora para em status terminal (done/error).
- CI: dependencia `requests` faltando no job de testes.
