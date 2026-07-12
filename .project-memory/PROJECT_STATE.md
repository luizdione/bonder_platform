# Estado do Projeto - bonder-src (PMM - PROJECT_STATE.md)

> **Memoria ativa - Nivel 1.** Reflete **somente o estado atual**. **Sempre
> reescrever**, nunca acumular historico. Manter enxuto (alvo < ~4k tokens).
> Ultima atualizacao: 2026-07-11

## Objetivo atual
Plataforma de codigo **pronta em v0.1.0**; o gargalo agora e **gerar os dados
experimentais**: submeter as amostras de CoIP/AP-MS (macrofagos murinos) a uma
plataforma de espectrometria de massas e obter as saidas de busca (.raw + tabelas)
para entao rodar o pipeline com dados reais.

## Funcionalidades prontas
- Ingesta unificada (`bonder.io`): MaxQuant/DIA-NN/FragPipe/generico -> MSDataset;
  deteccao automatica de motor e aquisicao; ausente=NaN.
- Especificidade (SAINTexpress + MiST) e quantitativo (wrappers R DEP/limma/MSstats).
- Bancos murinos fixados por versao + montagem do `search_db.fasta`; CLI completa
  (`db sync`, `baits check`, `qc`, `run`, `list-contrasts`, `selftest`).
- Dashboard Flask (localhost:8080) + fila RQ/Redis; abas Manutencao/autoteste e
  Ajuda e Tutoriais. Docker CPU + overlay GPU. Testes do nucleo CPU passando.
- Autoteste do pipeline validado em **dados sinteticos**.

## Em desenvolvimento
- Preparo da submissao a plataforma de MS: `formularios/` (3 formularios DOCX
  preenchidos + e-mail rascunho + recomendacao de instrumento + pendencias).

## Proximos passos
- Revisar e **enviar o e-mail** a plataforma (`formularios/EMAIL_plataforma.md`);
  com a resposta, definir **instrumento** (HF-X recomendado) e **aquisicao**
  (DDA vs DIA) e finalizar os campos pendentes (`formularios/PENDENCIAS_preenchimento.md`).
- Fornecer os FASTA das iscas em `config/sequences/` (NSs Icoaraci; LGALS3 P17931).
- No 1o `bonder db sync`, capturar os **sha256** dos bancos e commitar (travar versoes).
- Quando houver dados reais: rodar `NSs_vs_CTRL` e `LGALS3_vs_CTRL`, gerar relatorio
  e preparar deposito PRIDE/ProteomeXchange. Detalhe fino em TASKS.md.

## Riscos atuais
- **Sem dados reais ainda** (`data/` e `runs/` vazios); pipeline so exercitado em
  sinteticos - comportamento com dados reais nao verificado.
- **SAINTexpress** compila best-effort/nao-fatal; pode faltar o binario -> passo
  `saint` "pulado" ate colocar `vendor/bin/SAINTexpress-int`.
- **sha256 dos bancos ainda `null`** em `databases.yaml` (versoes nao travadas).
- Escolha instrumento/aquisicao depende de resposta da plataforma de MS.

## Resumo da ultima sessao
- **Data:** 2026-07-11
- **Desacoplamento do `docking_suite` concluido.** Memoria purgada de mirror/
  upstream/sync; bonder reafirmado como dedicado **SO a PPI por espectrometria de
  massas** (nao docking molecular).
- **Repositorio proprio resetado do zero:** historico antigo (linhagem
  docking_suite) descartado; `luizdione/bonder` (privado) agora tem **1 commit
  unico** `adc37a3` com a versao completa. `sync.ps1` removido; `formularios/` fora
  do git (gitignore); gate `git_dione` (app) limpo; commit sem trailer de IA.
- **`docking_suite` limpo do bonder:** branch `claude/bonder-proteome-platform-k8m6pa`
  (unico lugar com `bonder/`) deletado e PR #1 fechado; `main` (docking) intacto.
  SHA do branch recuperavel: `e03d8d2`.
- Detalhe completo desta sessao: `archive/sessions/`. Proximo gargalo real: gerar
  os dados de MS (ver `formularios/` e Proximos passos).
