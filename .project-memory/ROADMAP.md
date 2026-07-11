# Roadmap - bonder-src (PMM - ROADMAP.md)

> **Nivel 2.** Planejamento de **alto nivel** por versoes/fases. **Nao** listar
> tarefas detalhadas (isso e TASKS.md). Consultar sob demanda.

## Agora (v0.1.0 - plataforma pronta, gerando dados)
- Submeter as amostras de CoIP/AP-MS a uma plataforma de espectrometria de massas
  (confirmar HF-X + DIA); obter `.raw` + saidas de busca.
- Travar os bancos murinos por sha256 e fornecer os FASTA das iscas.

## Proxima versao (dados reais -> resultados)
- Rodar os contrastes `NSs_vs_CTRL` e `LGALS3_vs_CTRL` com dados reais;
  especificidade (SAINT/MiST) + quantitativo (MSstats/DEP/limma); relatorio final
  (tabela/volcano/rede) com controle de FDR.
- Deposito dos brutos em PRIDE/ProteomeXchange.

## Futuro / ideias
- Interatoma-alvo (analise): NSs Icoaraci (host-pathogen, viral) e Galectina-3
  (parceiros murinos), com validacao estrutural AlphaFold-Multimer dos hits.
- Integrar background CRAPome murino e priorizacao suplementar por ESM2.
