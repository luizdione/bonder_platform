# Tarefas - bonder-src (PMM - TASKS.md)

> **Memoria ativa - Nivel 1.** Estados: IN_PROGRESS - TODO - BLOCKED - DONE.
> Formato do item: `- [x] (T-0001) AAAA-MM-DD - descricao`.
> `[ ]` TODO, `[~]` IN_PROGRESS, `[!]` BLOCKED, `[x]` DONE.
> Quando DONE crescer, arquivar com `pmm.py archive-tasks` ->
> `archive/completed_tasks/`.

## IN_PROGRESS
- [~] (T-0002) 2026-07-11 - Revisar e ENVIAR o e-mail a plataforma de MS
  (`formularios/EMAIL_plataforma.md`). Rascunho AFIADO p/ DIA (itens 2-4): DIA
  confirmado; perguntar se o lab entrega o report do DIA-NN (`report.pg_matrix.tsv`
  + `report.tsv`) OU todos os `.raw`; oferta de fornecer o `search_db.fasta` com as
  iscas + caveat peptideos P17931/P16110 + FDR. Falta revisar, custo externo (IFRJ)
  e enviar.
- [~] (T-0003) 2026-07-11 - Finalizar campos pendentes dos formularios
  (`formularios/PENDENCIAS_preenchimento.md`). Feito: aquisicao = DIA (DIA-NN)
  confirmada. Faltam: dosagem de proteina, tampao de lise/eluicao compativel com MS,
  acondicionamento, riscos, datas.
- [~] (T-0010) 2026-07-12 - BioGRID no `bonder db sync`. IMPLEMENTADO em
  `cli.py::cmd_db_sync`: baixa o `.zip` multi-organismo (`biogrid_mouse.url`) e extrai o
  `organism_file` (Mus musculus tab3) para `cache_path("biogrid", ...)`. Validado offline
  (plan agora 4/6). Download+extracao reais em teste (background); falta travar o sha256
  do zip apos baixar.

## TODO
- [ ] (T-0006) 2026-07-11 - Garantir SAINTexpress-int disponivel (checar autoteste;
  se `saint: pulado`, compilar e colocar em `vendor/bin/`).
- [ ] (T-0007) 2026-07-11 - [depende de dados reais] Rodar `NSs_vs_CTRL` e
  `LGALS3_vs_CTRL`, revisar relatorio (tabela/volcano/rede) e preparar deposito PRIDE.
- [ ] (T-0009) 2026-07-12 - Corrigir a fonte do cRAP em `config/databases.yaml`: a URL
  fixada (`www.thegpm.org/crap/crap.fasta`) da 404/DNS-fail. Achar uma fonte de cRAP
  valida, baixar, travar o sha256 e regenerar o `search_db.fasta` (hoje SEM contaminantes).
- [ ] (T-0011) 2026-07-12 - Conectar STRING/BioGRID ao pipeline: `orchestrator.py:142`
  chama `build_interactome(bait_id, top)` com `edges=None`, entao as arestas presa-presa
  de referencia (STRING/BioGRID) NAO entram na rede. Carregar via
  `string_biogrid.load_string_edges` + `load_biogrid_edges` (dos caminhos do cache) e
  passar `edges` ao `build_interactome`.

## BLOCKED

## DONE
- [x] (T-0005) 2026-07-12 - sha256 dos bancos travados em `config/databases.yaml` apos o
  1o `bonder db sync` (data_root `E:\data\proteome_murine`): uniprot_fasta (reusado),
  uniprot_tsv (idmap), string_links, string_aliases. Validado por `db sync` OFFLINE
  (4/4 reusados, checksums batem). cRAP e BioGRID nao baixados -> sha seguem null (T-0009/T-0010).
- [x] (T-0004) 2026-07-12 - Iscas fornecidas e FASTA de busca montado. NSs do isolado
  (`config/sequences/NSs_Icoaraci.fasta`, 275 aa) corrigido (removido `*` do stop codon;
  cabecalho alinhado ao search_db_header); LGALS3 humana P17931 baixada. `bonder baits
  check` gerou e validou `search_db.fasta` (17269 seqs = 17267 murino + 2 iscas; P17931
  e P16110 distintos; 0 asteriscos). Proteoma murino REUSADO; cache consolidado em
  `E:\data\proteome_murine` (BONDER_DATA_ROOT).
- [x] (T-0001) 2026-07-11 - Preencher a memoria do projeto (CLAUDE, PROJECT_STATE,
  CONTEXT, TASKS + Nivel 2) com conteudo real; migrar changelog sem duplicar.
- [x] (T-0008) 2026-07-11 - Desacoplar do `docking_suite`: purgar mirror/upstream da
  memoria, remover `sync.ps1`, **resetar `luizdione/bonder` do zero** (1 commit
  `adc37a3`) e **limpar o `docking_suite`** (branch bonder deletado, PR #1 fechado;
  main/docking intacto). Bonder = PPI por espectrometria de massas.
