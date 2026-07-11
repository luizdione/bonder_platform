# .project-memory - Memoria Persistente do Projeto (PMM)

Este diretorio e a **fonte da verdade** do projeto para agentes de IA e humanos.
Torna o projeto **recuperavel sem depender do historico de conversa** de nenhum
assistente. Funciona com qualquer ferramenta (Claude Code, ChatGPT, Gemini,
Codex): tudo e **Markdown + um `config.yaml`**, versionavel em Git.

## Como ler (ordem por custo de contexto)
- **Nivel 1 - Memoria Ativa (ler sempre):** `CLAUDE.md`, `PROJECT_STATE.md`,
  `TASKS.md`, `CONTEXT.md`. Pequenos por design.
- **Nivel 2 - Memoria do Projeto (so quando a tarefa exigir):** `DECISIONS.md`,
  `KNOWLEDGE.md`, `ROADMAP.md`, `CHANGELOG.md`, `ISSUES.md`.
- **Nivel 3 - Arquivo (nunca carregar sem pedido explicito):** `archive/`.

## Regras
1. Contexto ativo pequeno; detalhe -> Nivel 2; historico -> `archive/`.
2. Nunca duplicar informacao: cada fato mora em **um** arquivo.
3. Compressao semantica: resumir/consolidar preservando o significado tecnico.
4. O repositorio e a verdade; a conversa e temporaria.

## Ferramenta
`pmm.py` (skill `gerente_memoria_projeto`) automatiza scaffold, medicao de tokens,
arquivamento e indice. Veja `config.yaml` para orcamentos e limiares. O formato e
estavel: integracoes futuras (RAG, bancos vetoriais, MCP) podem indexar estes
`.md` sem altera-los.
