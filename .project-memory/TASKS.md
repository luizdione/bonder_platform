# Tarefas - bonder-src (PMM - TASKS.md)

> **Memoria ativa - Nivel 1.** Estados: IN_PROGRESS - TODO - BLOCKED - DONE.
> Formato do item: `- [x] (T-0001) AAAA-MM-DD - descricao`.
> `[ ]` TODO, `[~]` IN_PROGRESS, `[!]` BLOCKED, `[x]` DONE.
> Quando DONE crescer, arquivar com `pmm.py archive-tasks` ->
> `archive/completed_tasks/`.

## IN_PROGRESS
- [~] (T-0002) 2026-07-11 - Revisar e ENVIAR o e-mail a plataforma de MS
  (`formularios/EMAIL_plataforma.md`). Rascunho AFIADO p/ DIA (itens 2-4). Falta
  revisar, custo externo (IFRJ) e enviar.
- [~] (T-0003) 2026-07-11 - Finalizar campos pendentes dos formularios
  (`formularios/PENDENCIAS_preenchimento.md`). Feito: aquisicao = DIA confirmada.
  Faltam: dosagem de proteina, tampao lise/eluicao compativel c/ MS, acondicionamento,
  riscos, datas.

## TODO
- [ ] (T-0007) 2026-07-11 - [depende de dados reais] Rodar `NSs_vs_CTRL` e
  `LGALS3_vs_CTRL` pelo dashboard, revisar relatorio (tabela/volcano/rede) e preparar
  deposito PRIDE.
- [ ] (T-0009) 2026-07-12 - Corrigir a fonte do cRAP em `config/databases.yaml`: a URL
  fixada da 404/DNS-fail. Achar fonte valida, baixar, travar sha256 e regenerar o
  `search_db.fasta` (hoje SEM contaminantes).

## BLOCKED

## DONE
- [x] (T-0012) 2026-07-13 - Seletor de arquivos no dashboard. Endpoint `GET /api/inputs`
  (`web/app.py`) lista as saidas de busca (.tsv/.txt/.csv) da pasta de inputs (filtra
  README/LEIA-ME); `inputs_dir` na config (env `BONDER_INPUTS_DIR`); dashboard ganhou
  seletor "Arquivo de entrada" + seletor opcional do `report.tsv` + botao atualizar.
  Pasta = `E:\data\proteome_murine\inputs` (montada em `/data/inputs` no container via
  `docker-compose.local.yml`). Validado E2E: endpoint lista, seletores presentes, mount ok.
- [x] (T-0006) 2026-07-12 - SAINTexpress-int disponivel no CONTAINER (compilou no build
  do `Dockerfile.analysis`); `/api/health/full`: SAINT + Rscript + R (DEP/limma/MSstats) OK.
- [x] (T-0011) 2026-07-12 - STRING/BioGRID conectados a rede (`orchestrator.py`
  `_load_reference_edges` + filtro `keep` em `string_biogrid.load_string_edges`). Validado:
  selftest PASSOU; E: real 367752 arestas (STRING 275618 + BioGRID 92134) p/ keep=1500.
- [x] (T-0010) 2026-07-12 - BioGRID no `bonder db sync` (baixa `.zip` 165 MB + extrai o
  tab3 do camundongo). sha256 travado; `load_biogrid_edges` = 92134 arestas; db sync 5/6.
- [x] (T-0005) 2026-07-12 - sha256 dos bancos travados em `databases.yaml` (uniprot
  fasta+tsv, string links+aliases, biogrid). Validado offline. So cRAP falta (T-0009).
- [x] (T-0004) 2026-07-12 - Iscas + `search_db.fasta` montado (17269 seqs; NSs 275 aa
  corrigido s/ `*`; LGALS3 P17931; P16110 distinto). Cache em `E:\data\proteome_murine`.
- [x] (T-0001) 2026-07-11 - Preencher a memoria do projeto com conteudo real.
- [x] (T-0008) 2026-07-11 - Desacoplar do `docking_suite`; resetar `luizdione/bonder`
  do zero (commit `adc37a3`). Bonder = PPI por espectrometria de massas.
