# Tarefas - bonder-src (PMM - TASKS.md)

> **Memoria ativa - Nivel 1.** Estados: IN_PROGRESS - TODO - BLOCKED - DONE.
> Formato do item: `- [x] (T-0001) AAAA-MM-DD - descricao`.
> `[ ]` TODO, `[~]` IN_PROGRESS, `[!]` BLOCKED, `[x]` DONE.
> Quando DONE crescer, arquivar com `pmm.py archive-tasks` ->
> `archive/completed_tasks/`.

## IN_PROGRESS

## TODO
- [ ] (T-0002) 2026-07-11 - Revisar e enviar o e-mail a plataforma de MS
  (`formularios/EMAIL_plataforma.md`): confirmar instrumento (HF-X), aquisicao
  (DDA vs DIA), entrega de `.raw`, FASTA customizado com as iscas e custo externo.
- [ ] (T-0003) 2026-07-11 - Finalizar campos pendentes dos formularios
  (`formularios/PENDENCIAS_preenchimento.md`): dosagem de proteina, tampao de
  lise/eluicao compativel com MS, acondicionamento, riscos, datas.
- [ ] (T-0004) 2026-07-11 - Fornecer os FASTA das iscas em `config/sequences/`
  (NSs Icoaraci; LGALS3 humana P17931) e rodar `bonder baits check`.
- [ ] (T-0005) 2026-07-11 - No 1o `bonder db sync`, capturar os sha256 dos bancos
  (UniProt/STRING/BioGRID/cRAP) e commitar em `config/databases.yaml` (travar versoes).
- [ ] (T-0006) 2026-07-11 - Garantir SAINTexpress-int disponivel (checar autoteste;
  se `saint: pulado`, compilar e colocar em `vendor/bin/`).
- [ ] (T-0007) 2026-07-11 - [depende de dados reais] Rodar `NSs_vs_CTRL` e
  `LGALS3_vs_CTRL`, revisar relatorio (tabela/volcano/rede) e preparar deposito PRIDE.

## BLOCKED

## DONE
- [x] (T-0001) 2026-07-11 - Preencher a memoria do projeto (CLAUDE, PROJECT_STATE,
  CONTEXT, TASKS + Nivel 2) com conteudo real; migrar changelog sem duplicar.
- [x] (T-0008) 2026-07-11 - Desacoplar do `docking_suite`: remover `sync.ps1`, purgar
  mirror/upstream da memoria, e publicar em `luizdione/bonder` (privado, commit d537168).
  Bonder = PPI por espectrometria de massas.
