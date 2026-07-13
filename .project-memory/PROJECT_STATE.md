# Estado do Projeto - bonder-src (PMM - PROJECT_STATE.md)

> **Memoria ativa - Nivel 1.** Reflete **somente o estado atual**. **Sempre
> reescrever**, nunca acumular historico. Manter enxuto (alvo < ~4k tokens).
> Ultima atualizacao: 2026-07-13

## Objetivo atual
Plataforma **rodando localmente em container** (http://localhost:8080, healthy), com
**seletor de arquivos** e **bancos completos**; o gargalo agora e **gerar os dados
experimentais**. Aquisicao **confirmada = DIA (DIA-NN)** pelo colaborador, que entregara
os `.raw`. O bonder ingere a **saida do DIA-NN** (`report.pg_matrix.tsv` + `report.tsv`),
nao o `.raw` -> pedir o report ja processado ao laboratorio.

## Funcionalidades prontas
- Ingesta unificada (`bonder.io`): MaxQuant/DIA-NN/FragPipe/generico -> MSDataset.
- Especificidade (SAINTexpress + MiST) e quantitativo (wrappers R DEP/limma/MSstats).
- **Container local no ar** (`docker compose` + override `docker-compose.local.yml`):
  web healthy em **http://localhost:8080**, worker + redis up. SAINT + R OK; bancos de E:
  em `/data`. Dashboard 100% offline (cytoscape/marked vendorizados).
- **Dashboard com seletor de inputs**: lista a pasta via `/api/inputs`
  (`BONDER_INPUTS_DIR=/data/inputs` = `E:\data\proteome_murine\inputs`) + seletor do
  `report.tsv` (DIA-NN) + botao atualizar. Basta soltar o arquivo na pasta.
- **Exportador estatico** (`bonder export --run <id>` ou link no dashboard): 1 HTML
  auto-contido por corrida (resumo/QC + tabela + volcano + rede cytoscape), sem
  servidor/CDN, para publicar no hPanel/Hostinger.
- **`search_db.fasta`** completo (17385 seqs: proteoma murino + 116 contaminantes cRAP
  com prefixo `CON__` + NSs 275 aa + LGALS3 P17931).
- **Bancos em cache** (`E:\data\proteome_murine`, `db sync` 6/6, sha256 travados): UniProt
  fasta+idmap, STRING v12.0, BioGRID 4.4.235, cRAP (Zenodo/GPM). STRING/BioGRID na rede (T-0011).

## Em desenvolvimento
- Submissao a plataforma de MS: e-mail (`EMAIL_plataforma.md`) afiado p/ DIA e
  `PENDENCIAS_preenchimento.md` com aquisicao=DIA. Falta revisar/enviar e preencher.

## Proximos passos
- Revisar e **enviar o e-mail** e entregar o `search_db.fasta` ao laboratorio.
- **Quando o report DIA-NN chegar:** soltar `report.pg_matrix.tsv` (+ `report.tsv`) em
  `E:\data\proteome_murine\inputs`, abrir localhost:8080, selecionar e rodar
  `NSs_vs_CTRL` / `LGALS3_vs_CTRL`; relatorio + deposito PRIDE (T-0007).
- Commitar as mudancas do cRAP (databases.yaml, db/baits.py, io/contaminants.py) + PMM.

## Riscos atuais
- **Sem dados reais ainda** (`runs/` vazio); pipeline so exercitado em sinteticos.
- **`.raw` nao entra direto**: depende da busca DIA-NN a montante. Instrumento (HF-X) a confirmar.
- Deteccao de contaminantes `CON__` so validada de fato com dados reais (depende de como o
  DIA-NN reporta os IDs vindos do search_db).

## Resumo da ultima sessao
- **Data:** 2026-07-13
- **Exportador estatico (T-0013):** `web/export.py` gera 1 HTML auto-contido por corrida
  (tabela + volcano + rede) p/ publicar no hPanel; CLI + endpoint + link no dashboard.
  Testado (484 KB, sem recursos externos). Hostinger = so visualizacao, sem deploy auto.
- **cRAP resolvido (T-0009):** fonte GPM fora do ar -> mirror **Zenodo** (Gatto, DOI
  10.5281/zenodo.15115102, CC-BY); 116 seqs, sha256 travado; `search_db.fasta` regenerado
  (17385 seqs). `build_search_fasta` agora prefixa contaminantes com `CON__` (deteccao por
  prefixo em io/contaminants); `db sync` offline 6/6.
- **Seletor de inputs (T-0012) + dashboard offline** commitados (e93d80e) e pushados p/
  `luizdione/bonder`. Container BONDER no ar em localhost:8080.
- Mudancas do cRAP (databases.yaml, db/baits.py, io/contaminants.py) + PMM ainda NAO
  commitadas.
