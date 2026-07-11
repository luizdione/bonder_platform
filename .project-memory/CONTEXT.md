# Contexto Tecnico - bonder-src (PMM - CONTEXT.md)

> **Memoria ativa - Nivel 1.** Resumo tecnico **sempre atualizado** (o "mapa" do
> sistema). Sem historico. Manter conciso.

## Arquitetura (visao geral)
Plataforma localhost containerizada. Navegador -> Flask (`web`, porta 8080) ->
fila **RQ/Redis** -> `worker` executa o pipeline. Fluxo de dados unidirecional:

```
io -> db -> scoring(SAINT/MiST) -> stats(DEP/limma/MSstats R) -> annotate -> pipeline -> relatorio/web
                                                                     |
                                    [gpu opcional] DIA-NN / rescoring / AlphaFold / ESM2
```

Nucleo cientifico (io/scoring-format/annotate/pipeline) roda em **CPU puro**;
etapas que dependem de SAINT-binario, R ou GPU sao **puladas e registradas no
manifesto** quando a ferramenta falta (nunca finge cobertura).

## Tecnologias / dependencias
- **Python 3.10+** (alvo 3.11): numpy, pandas, pyarrow, scipy, networkx, pyyaml,
  requests, matplotlib, flask. Extras: `web` (gunicorn, rq, redis), `ms`
  (pyteomics), `annotate` (gprofiler), `gpu` (torch, transformers, ms2rescore,
  peptdeep), `dev` (pytest).
- **R/Bioconductor** (fora do Python): MSstats/DEP/limma via `Rscript`
  (`R/run_dep_limma.R`, `R/run_msstats.R`). QC em Python (sem valor inferencial).
- **SAINTexpress-int**: compilado do fonte (SourceForge) no `Dockerfile.analysis`,
  best-effort/nao-fatal; fallback = binario manual em `vendor/bin/`.
- **Docker**: `Dockerfile.analysis` (Python+R+SAINT) e `Dockerfile.gpu`
  (CUDA 12.4 + torch). Compose CPU padrao + overlay `docker-compose.gpu.yml`.
- Motores de busca externos (fora do repo): MaxQuant/FragPipe (DDA), DIA-NN (DIA).

## Integracoes / servicos externos
- **Redis** (fila RQ) - URL por `BONDER_REDIS_URL` (default `redis://redis:6379/0`);
  fallback para execucao em thread se ausente.
- Downloads de bancos MURINOS fixados por versao (`config/databases.yaml`):
  UniProt (reviewed, taxid 10090, release 2024_06), STRING v12.0, BioGRID 4.4.235,
  contaminantes cRAP. Cache content-addressed + sha256 (preencher hashes no 1o `bonder db sync`).
- **g:Profiler** (GO/vias) na anotacao. Deposito alvo: PRIDE/ProteomeXchange.
- Iscas exogenas: FASTA em `config/sequences/*.fasta` (privado, nao versionado).

## Fluxos principais
- **Ingesta (`bonder.io`):** detecta motor + aquisicao (DDA/DIA) automaticamente;
  parseia MaxQuant/DIA-NN/FragPipe/generico -> `MSDataset` unificado; ausente=NaN.
- **Especificidade:** SAINTexpress (todas as iscas) + MiST (isca viral NSs,
  host-pathogen). **Quantitativo:** DEP/limma/MSstats por contraste isca-vs-controle.
- **Contrastes** (de `samples.yaml`): `NSs_vs_CTRL`, `LGALS3_vs_CTRL`.
- Relatorio: tabela + volcano + rede de interacao; `manifest.json` + `results.json`.

## Componentes / modulos (44 .py em bonder/ + tests/)
- `bonder/io/` - parsers, detect (motor/aquisicao), schema (MSDataset), contaminants.
- `bonder/db/` - downloader (cache+sha256), uniprot, string_biogrid, crapome, baits
  (valida iscas, monta `search_db.fasta`).
- `bonder/scoring/` - saint.py, mist.py (formatacao + execucao).
- `bonder/stats/` - prepare, qc, runner (chama Rscript).
- `bonder/annotate/` - annotate (gene/GO/via), network (rede).
- `bonder/gpu/` - detect, gpu_gate (compartilha placa c/ Ollama), tools (DIA-NN/
  rescoring/AlphaFold), esm2 (suplementar).
- `bonder/pipeline/` - orchestrator, report.
- `bonder/web/` - app (Flask create_app), jobs (RQ), health (self_test), docs
  (serve `.md` na aba Ajuda).
- `bonder/cli.py` - subcomandos db/baits/qc/run/list-contrasts/selftest.
- `config/` - baits.yaml, samples.yaml, databases.yaml, gpu.yaml, sequences/.
- `R/`, `docker/`, `docs/` (COMO_RODAR, METODOLOGIA, REPRODUTIBILIDADE), `tests/`.

## Como rodar / portas / endpoints
- Dashboard: `http://localhost:8080` (Docker) ou `127.0.0.1:8080`
  (`python -m bonder.web.app`). Healthcheck: `GET /api/health`.
- Docs no dashboard: `GET /api/docs`, `GET /api/docs/<id>` (aba Ajuda e Tutoriais).
- Entradas do usuario em `./inputs` (montado `/inputs`); saidas em `runs/`.
- Env vars: `BONDER_HOST`, `BONDER_DATA_ROOT`, `BONDER_RUNS_DIR`, `BONDER_REDIS_URL`.
- Scripts Windows: `iniciar_bonder.ps1`, `run.ps1`, `run-gpu.ps1`, `stop.ps1`,
  `criar_atalho.ps1`.
