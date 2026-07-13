# bonder-src - Regras Permanentes (PMM - CLAUDE.md)

> **Memoria ativa - Nivel 1.** Apenas informacao **permanente**: padroes,
> convencoes, arquitetura estavel, regras e requisitos. **Nunca** registrar
> historico, progresso ou decisoes datadas aqui (isso vai para
> PROJECT_STATE / DECISIONS / CHANGELOG). Manter curto.

## Identidade do projeto
- **Nome:** bonder (pacote Python `bonder`; repositorio proprio `luizdione/bonder`, privado; pasta local de trabalho `bonder-src`).
- **Descricao (1 linha):** plataforma local (navegador + Docker) que ORQUESTRA
  ferramentas consagradas de proteomica para analisar CoIP-MS / AP-MS e
  identificar parceiros de interacao no proteoma de camundongo (*Mus musculus*,
  taxid 10090); dashboard Flask em `http://localhost:8080`.
- **Stack principal:** Python 3.10+ (alvo 3.11) + Flask/gunicorn + RQ/Redis;
  wrappers R/Bioconductor (MSstats/DEP/limma) via Rscript; Docker (CPU padrao +
  overlay GPU CUDA 12.4 p/ RTX 3060). Testes: pytest (nucleo CPU).
- **Projeto-piloto:** 2 iscas EXOGENAS ao camundongo, cada uma em uma Co-IP
  separada contra macrofagos murinos: **NSs** do phlebovirus Icoaraci (grupo Bujaru; viral,
  desenho subtrativo NSs-superexp vs WT) e **Galectina-3** humana (LGALS3,
  P17931). Os parceiros buscados sao proteinas de camundongo.

## Padroes de codigo e convencoes
- Config **declarativa** em `config/*.yaml` (baits, samples, databases, gpu) -
  mudar comportamento por YAML, nao por hardcode.
- Chave de proteina = **acesso UniProt lider**; ausente = **NaN, nunca 0**.
- Docs, docstrings e comentarios em **PT-BR**. Arquivos do PMM em **ASCII sem
  acento** (consistencia + encoding no OneDrive).
- Toda corrida grava `manifest.json` (versoes, ferramentas disponiveis, device,
  proveniencia, passos) + `results.json` em `runs/`.
- Entry point unico: `bonder` (console_script) -> `bonder.cli:main`.

## Arquitetura / regras invioaveis
- **Fluxo unidirecional:** `io -> db -> scoring/stats -> gpu -> pipeline -> web`.
  Nao criar dependencias reversas entre camadas.
- **Nao reinventar a roda:** orquestrar SAINTexpress/MiST (especificidade) e
  MSstats/DEP/limma (quantitativo). NAO reimplementar scoring/estatistica.
- **Nucleo cientifico roda em CPU**, sem GPU e sem R (io / scoring-formatacao /
  annotate / pipeline). E o que a CI exercita. GPU e R sao opcionais.
- **Iscas exogenas** (NSs, LGALS3 humana P17931) NUNCA entram como preys no
  denominador murino; manter DISTINTAS do ortologo murino `Lgals3` (P16110).
  Peptideos compartilhados P17931/P16110 devem ser sinalizados.
- **MaxLFQ do DIA-NN nunca e re-normalizado.**
- **ESM2/embeddings** so como priorizacao exploratoria **suplementar**, jamais
  base do escore de confianca que vai para a figura principal.
- **Bancos fixados por versao + sha256** (`config/databases.yaml`); nunca
  `latest`; o downloader FALHA se o checksum divergir.
- Etapa cuja ferramenta externa falta e **pulada com registro no manifesto** - o
  pipeline nunca finge cobertura que nao teve.
- **Escopo exclusivo:** o bonder e dedicado **SOMENTE a interacao proteina-proteina
  (PPI) por espectrometria de massas** (CoIP-MS / AP-MS). NAO e docking molecular e
  NAO e derivado nem espelho de nenhum projeto de docking/estrutura; nunca
  introduzir codigo ou conceitos de docking neste projeto.
- **Repositorio proprio e independente:** `luizdione/bonder` (branch `main`, privado).
  ESTE diretorio e a **fonte da verdade** do codigo; edite aqui e faca `git commit` +
  `git push origin main`. Nao ha upstream nem sincronizacao externa.

## Requisitos obrigatorios
- Reprodutibilidade compativel com publicacao: FDR adequado, replicas +
  controles pareados (alvo >= 3 replicas biologicas/grupo), deposito dos brutos
  em PRIDE/ProteomeXchange.
- Licenca MIT; ferramentas orquestradas mantem suas licencas (citar em
  `docs/METODOLOGIA.md`).
- Identidade do autor em manuscritos/metadados: Luiz Dione Barbosa de Melo -
  IFRJ - luiz.melo@ifrj.edu.br - ORCID 0000-0003-2445-9943.

## Ambiente de execucao (host do autor)
- **GPU RTX 3060 = "cerebro"**: etapas aceleradas (DIA-NN, ESM2, rescoring) via overlay
  `docker-compose.gpu.yml` (profile gpu, sob demanda). O NUCLEO cientifico roda em CPU.
- **Drive E: = dados pesados.** Cache do bonder em `E:\data\proteome_murine`
  (BONDER_DATA_ROOT = User env var): proteoma UniProt+idmap, STRING, BioGRID, search_db.
- **Runtime local**: container **Docker** (padrao) ou env conda miniforge **`datascience`**
  (`python -m bonder.web.app`). As ANALISES rodam LOCALMENTE em **http://localhost:8080**.
- **Hostinger = SO visualizacao** dos resultados (online); nao roda analise.
- Override local do compose: `docker/docker-compose.local.yml` (bind de E: em `/data`;
  gitignored). Subir: `docker compose -f docker/docker-compose.yml -f
  docker/docker-compose.local.yml up --build -d`.

## Comandos essenciais
- **Instalar:** `pip install -e ".[dev,web,ms,annotate]"`  (ou `make install`)
- **Testes:** `python -m pytest -q`  (ou `make test`) - nucleo CPU, sem GPU/R
- **Autoteste do pipeline:** `bonder selftest` (dados sinteticos)
- **Rodar (Docker CPU):** `docker compose -f docker/docker-compose.yml up --build`
  -> `http://localhost:8080`  (ou `make up`)
- **Rodar (Docker GPU):** `make up-gpu` (overlay `docker-compose.gpu.yml`, RTX 3060)
- **Rodar (sem Docker):** `python -m bonder.web.app` -> `127.0.0.1:8080`
- **CLI:** `bonder db sync` | `bonder baits check` | `bonder qc --input F` |
  `bonder run --input F --contrast NSs_vs_CTRL` | `bonder list-contrasts`
- **Publicar:** `git push origin main`  (repositorio privado `luizdione/bonder`)
