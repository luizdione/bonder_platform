# Estado do Projeto - bonder-src (PMM - PROJECT_STATE.md)

> **Memoria ativa - Nivel 1.** Reflete **somente o estado atual**. **Sempre
> reescrever**, nunca acumular historico. Manter enxuto (alvo < ~4k tokens).
> Ultima atualizacao: 2026-07-13

## Objetivo atual
Plataforma **rodando localmente em container** (http://localhost:8080, healthy) e com
**seletor de arquivos** pronto para receber os dados; o gargalo agora e **gerar os dados
experimentais**. Aquisicao **confirmada = DIA (DIA-NN)** pelo colaborador, que entregara
os `.raw`. O bonder ingere a **saida do DIA-NN** (`report.pg_matrix.tsv` + `report.tsv`),
nao o `.raw` -> pedir o report ja processado ao laboratorio.

## Funcionalidades prontas
- Ingesta unificada (`bonder.io`): MaxQuant/DIA-NN/FragPipe/generico -> MSDataset.
- Especificidade (SAINTexpress + MiST) e quantitativo (wrappers R DEP/limma/MSstats).
- **Container local no ar** (`docker compose` + override `docker-compose.local.yml`):
  web healthy em **http://localhost:8080**, worker + redis up. SAINT + R OK; bancos de E:
  montados em `/data`.
- **Dashboard com seletor de inputs**: aba "Nova corrida" lista os arquivos da pasta de
  inputs (`GET /api/inputs`; `BONDER_INPUTS_DIR=/data/inputs` = `E:\data\proteome_murine\inputs`),
  seletor do `report.tsv` (DIA-NN) e botao atualizar. Basta soltar o arquivo na pasta.
- **`search_db.fasta`** validado (17269 seqs: murino + NSs 275 aa + LGALS3 P17931).
- **Bancos em cache** (`E:\data\proteome_murine`): UniProt fasta+idmap, STRING v12.0,
  BioGRID 4.4.235 - sha256 travados. STRING/BioGRID entram na rede (T-0011).

## Em desenvolvimento
- Submissao a plataforma de MS: e-mail (`EMAIL_plataforma.md`) afiado p/ DIA e
  `PENDENCIAS_preenchimento.md` com aquisicao=DIA. Falta revisar/enviar e preencher.

## Proximos passos
- Revisar e **enviar o e-mail** e entregar o `search_db.fasta` ao laboratorio.
- **Quando o report DIA-NN chegar:** soltar `report.pg_matrix.tsv` (+ `report.tsv`) em
  `E:\data\proteome_murine\inputs`, abrir localhost:8080, selecionar no dashboard e rodar
  `NSs_vs_CTRL` / `LGALS3_vs_CTRL`; relatorio + deposito PRIDE (T-0007).
- Resolver a fonte do **cRAP** (T-0009); regenerar o `search_db.fasta` com contaminantes.

## Riscos atuais
- **Sem dados reais ainda** (`runs/` vazio); pipeline so exercitado em sinteticos.
- **cRAP indisponivel** na fonte fixada (404/DNS-fail); `search_db.fasta` sem contaminantes.
- **`.raw` nao entra direto**: depende da busca DIA-NN a montante. Instrumento (HF-X) a confirmar.

## Resumo da ultima sessao
- **Data:** 2026-07-13
- **Seletor de arquivos no dashboard (T-0012):** endpoint `/api/inputs` + `inputs_dir` na
  config + seletor no HTML; pasta `E:\data\proteome_murine\inputs` montada em `/data/inputs`.
  Validado E2E (endpoint lista o arquivo, seletores presentes, mount ok). Ha um
  `EXEMPLO_report.pg_matrix.tsv` na pasta (o usuario pode apagar).
- **Dashboard 100% offline:** cytoscape 3.30.2 e marked vendorizados em
  `bonder/web/static/vendor/` (servidos em `/static/vendor`); removida a dependencia de CDN.
- **Container BONDER no ar** (localhost:8080, healthy) via override `docker-compose.local.yml`
  (bind de E: em /data). SAINT/R/bancos OK (T-0006). T-0010/T-0011/T-0005 fechadas.
- **Setup do autor no CLAUDE.md:** GPU=cerebro (GPU sob demanda), E:=dados, Docker/conda
  `datascience`, Hostinger=so visualizacao, analises em localhost:8080.
- Mudancas de codigo (cli/orchestrator/string_biogrid/config/web/app + dashboard.html) +
  configs no checkout principal, **prontas para commit** (sem trailer de IA).
