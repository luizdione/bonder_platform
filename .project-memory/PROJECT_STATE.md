# Estado do Projeto - bonder-src (PMM - PROJECT_STATE.md)

> **Memoria ativa - Nivel 1.** Reflete **somente o estado atual**. **Sempre
> reescrever**, nunca acumular historico. Manter enxuto (alvo < ~4k tokens).
> Ultima atualizacao: 2026-07-12

## Objetivo atual
Plataforma de codigo **pronta em v0.1.0**; o gargalo agora e **gerar os dados
experimentais**. Aquisicao **confirmada = DIA (DIA-NN)** pelo colaborador, que
entregara os `.raw`. Como o bonder ingere a **saida do DIA-NN** (`report.pg_matrix.tsv`
+ `report.tsv`) e **nao le `.raw` direto**, a estrategia e **pedir o report ja
processado ao laboratorio** (alternativa: rodar o DIA-NN localmente na RTX 3060). O
**FASTA de busca e os bancos ja estao prontos** (falta so o cRAP).

## Funcionalidades prontas
- Ingesta unificada (`bonder.io`): MaxQuant/DIA-NN/FragPipe/generico -> MSDataset;
  deteccao automatica de motor e aquisicao; ausente=NaN.
- Especificidade (SAINTexpress + MiST) e quantitativo (wrappers R DEP/limma/MSstats).
- Bancos murinos fixados por versao + montagem do `search_db.fasta`; CLI completa
  (`db sync`, `baits check`, `qc`, `run`, `list-contrasts`, `selftest`).
- Dashboard Flask (localhost:8080) + fila RQ/Redis; abas Manutencao/autoteste e
  Ajuda e Tutoriais. Docker CPU + overlay GPU. Testes do nucleo CPU passando.
- Autoteste do pipeline validado em **dados sinteticos**.
- **`search_db.fasta` montado e validado** (17269 seqs: 17267 murino + NSs 275 aa +
  LGALS3 P17931; P16110 murino distinto).
- **Bancos de referencia em cache** (`E:\data\proteome_murine`, BONDER_DATA_ROOT):
  proteoma UniProt (2024_06), idmap TSV, STRING v12.0 (links+aliases) - todos com
  **sha256 travado** em `databases.yaml` e validados offline. Falta cRAP e BioGRID.

## Em desenvolvimento
- Submissao a plataforma de MS: e-mail (`EMAIL_plataforma.md`) afiado p/ DIA e
  `PENDENCIAS_preenchimento.md` com aquisicao=DIA. Falta revisar/enviar o e-mail e
  preencher os campos restantes.

## Proximos passos
- Revisar e **enviar o e-mail** (`formularios/EMAIL_plataforma.md`): confirmar quem
  roda o DIA-NN, custo externo (IFRJ) e o uso do FASTA com as iscas. Entregar o
  `search_db.fasta` ao laboratorio.
- Resolver a fonte do **cRAP** (T-0009) e o **BioGRID** (T-0010); depois regenerar o
  `search_db.fasta` com contaminantes.
- Garantir o **SAINTexpress-int** (T-0006).
- Quando o report DIA-NN chegar em `./inputs/`: `bonder qc` e depois `bonder run`
  para `NSs_vs_CTRL` e `LGALS3_vs_CTRL`; relatorio e deposito PRIDE/ProteomeXchange.

## Riscos atuais
- **Sem dados reais ainda** (`runs/` vazio); pipeline so exercitado em sinteticos.
- **cRAP indisponivel** na fonte fixada (404/DNS-fail); `search_db.fasta` **sem
  contaminantes** ate resolver T-0009.
- **BioGRID nao entra no `db sync`** (T-0010): a rede so tera STRING ate incluir/extrair.
- **SAINTexpress** compila best-effort/nao-fatal; pode faltar o binario -> passo
  `saint` "pulado" ate colocar `vendor/bin/SAINTexpress-int` (T-0006).
- **`.raw` nao entra direto no bonder**: depende de uma busca DIA-NN a montante.
  Instrumento (HF-X) ainda a confirmar.

## Resumo da ultima sessao
- **Data:** 2026-07-12
- **DIA confirmado**; bonder ingere a saida do DIA-NN, nao o `.raw`. Decisao: pedir o
  report ao lab. E-mail afiado + `PENDENCIAS` com DIA -> T-0002/T-0003 IN_PROGRESS.
- **Iscas + `search_db.fasta` (T-0004 DONE):** NSs corrigido (removido `*`; 275 aa);
  LGALS3 P17931 baixada; proteoma reusado; validado (17269 seqs).
- **Taxonomia corrigida:** Icoaraci -> **phlebovirus (grupo Bujaru)** em 11 lugares.
- **Bancos consolidados em `E:\data\proteome_murine`** (BONDER_DATA_ROOT); `db sync`
  concluido (4/5): UniProt fasta+idmap + STRING links+aliases, **sha256 travados** e
  validados offline (T-0005 DONE). cRAP 404 (T-0009); BioGRID fora do db sync (T-0010).
- `E:\data\bonder` antigo pode ser removido manualmente (sandbox nao deleta em E:).
