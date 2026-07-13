# Tarefas - bonder-src (PMM - TASKS.md)

> **Memoria ativa - Nivel 1.** Estados: IN_PROGRESS - TODO - BLOCKED - DONE.
> Formato do item: `- [x] (T-0001) AAAA-MM-DD - descricao`.
> `[ ]` TODO, `[~]` IN_PROGRESS, `[!]` BLOCKED, `[x]` DONE.
> Quando DONE crescer, arquivar com `pmm.py archive-tasks` ->
> `archive/completed_tasks/`.

## IN_PROGRESS
- [~] (T-0002) 2026-07-11 - Revisar e ENVIAR o e-mail a plataforma de MS
  (`formularios/EMAIL_plataforma.md`). Rascunho AFIADO p/ DIA. Falta revisar, custo
  externo (IFRJ) e enviar.
- [~] (T-0003) 2026-07-11 - Finalizar campos pendentes dos formularios
  (`formularios/PENDENCIAS_preenchimento.md`). Feito: aquisicao = DIA confirmada. Faltam:
  dosagem de proteina, tampao lise/eluicao compativel c/ MS, acondicionamento, riscos, datas.

## TODO
- [ ] (T-0007) 2026-07-11 - [depende de dados reais] Rodar `NSs_vs_CTRL` e
  `LGALS3_vs_CTRL` pelo dashboard, revisar relatorio (tabela/volcano/rede) e preparar
  deposito PRIDE.

## BLOCKED

## DONE
- [x] (T-0013) 2026-07-13 - Exportador de resultados como HTML estatico (hPanel/Hostinger).
  Novo `web/export.py` (`export_run`): 1 arquivo .html auto-contido por corrida (resumo/QC +
  tabela + volcano data-URI + rede cytoscape embutido), sem servidor/CDN. CLI `bonder export
  --run <id>` + endpoint `/api/runs/<id>/export` + link no dashboard. Testado em corrida
  sintetica (484 KB, self-contained; volcano so com R/container).
- [x] (T-0009) 2026-07-13 - cRAP resolvido. Fonte GPM original fora do ar -> mirror
  **Zenodo** (DOI 10.5281/zenodo.15115102, Gatto/camprotR, CC-BY): `crap_gpm.fasta` (116
  seqs: BSA/queratinas/tripsina). URL + sha256 travados em `databases.yaml`. `search_db.fasta`
  regenerado COM contaminantes (17385 seqs); `build_search_fasta` agora PREFIXA os
  contaminantes com `CON__` (o cRAP GPM nao traz prefixo e a deteccao em `io/contaminants`
  e por prefixo). `db sync` offline 6/6.
- [x] (T-0012) 2026-07-13 - Seletor de arquivos no dashboard (`/api/inputs` + `inputs_dir`
  na config + seletores no HTML); pasta `E:\data\proteome_murine\inputs` em `/data/inputs`.
  Dashboard 100% offline (cytoscape/marked vendorizados). Commit e93d80e.
- [x] (T-0006) 2026-07-12 - SAINTexpress-int OK no CONTAINER (compilou no build); SAINT +
  Rscript + R (DEP/limma/MSstats) presentes.
- [x] (T-0011) 2026-07-12 - STRING/BioGRID conectados a rede (`orchestrator`
  `_load_reference_edges` + filtro `keep`). Validado: 367752 arestas p/ keep=1500.
- [x] (T-0010) 2026-07-12 - BioGRID no `bonder db sync` (baixa `.zip` + extrai tab3 do
  camundongo, 92134 arestas). sha256 travado.
- [x] (T-0005) 2026-07-12 - sha256 dos bancos travados em `databases.yaml` (uniprot, string,
  biogrid, e agora cRAP). Validado offline (6/6).
- [x] (T-0004) 2026-07-12 - Iscas + `search_db.fasta` (NSs 275 aa s/ `*`; LGALS3 P17931;
  P16110 distinto). Cache em `E:\data\proteome_murine`.
- [x] (T-0001) 2026-07-11 - Preencher a memoria do projeto com conteudo real.
- [x] (T-0008) 2026-07-11 - Desacoplar do `docking_suite`; resetar `luizdione/bonder`
  (commit `adc37a3`). Bonder = PPI por espectrometria de massas.
