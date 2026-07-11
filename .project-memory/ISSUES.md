# Issues - bonder-src (PMM - ISSUES.md)

> **Nivel 2.** Bugs conhecidos, limitacoes e melhorias futuras. Consultar sob demanda.

## Bugs conhecidos
- (nenhum aberto no momento; os bugs da v0.1.0 foram corrigidos - ver `../CHANGELOG.md`).

## Limitacoes
- [ ] (I-0001) `data/` e `runs/` vazios: **sem dados reais**; pipeline so validado
  em dados sinteticos (`bonder selftest`). Comportamento com dados reais nao verificado.
- [ ] (I-0002) `config/databases.yaml` com **sha256 = null** em todas as fontes:
  versoes ainda **nao travadas** (preencher no 1o `bonder db sync`).
- [ ] (I-0003) **SAINTexpress** best-effort/nao-fatal no build: pode faltar o binario
  -> passo `saint` pulado ate colocar `vendor/bin/SAINTexpress-int`.
- [x] (I-0004) RESOLVIDO 2026-07-11. Desacoplado do `docking_suite`: o bonder passa
  a ser repositorio proprio (`luizdione/bonder`), sem sync externo. Editar aqui e
  fazer commit/push normal.

## Melhorias futuras
- Preencher/integrar o background **CRAPome** murino (hoje `user-supplied`).
- Automatizar o empacotamento para deposito PRIDE/ProteomeXchange.
- Validacao estrutural dos hits por AlphaFold2-Multimer/ColabFold (GPU).
