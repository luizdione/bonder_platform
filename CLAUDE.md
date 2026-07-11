<!-- PMM:BEGIN (gerente_memoria_projeto) -->
## Memoria do Projeto (PMM)
Este projeto usa **Project Memory Manager**. A **fonte da verdade** e a pasta
`.project-memory/` - nao dependa do historico de conversa.

**Ao iniciar a sessao, leia a memoria ativa (Nivel 1):**
`.project-memory/CLAUDE.md`, `.project-memory/PROJECT_STATE.md`,
`.project-memory/TASKS.md`, `.project-memory/CONTEXT.md`.

Nivel 2 (`DECISIONS/KNOWLEDGE/ROADMAP/CHANGELOG/ISSUES.md`) so quando a tarefa
exigir. `archive/` nunca e carregado sem pedido. Ao concluir tarefas, sincronize
com a skill `gerente_memoria_projeto`.

**Ao compactar/limpar a sessao (`/compact`, `/clear`, `/branch`):** preserve o
objetivo, as decisoes e as pendencias; ao retomar, releia a memoria ativa acima.
(A skill `salvar_contexto` grava o resumo da sessao aqui, no PMM.)
@.project-memory/CLAUDE.md
@.project-memory/PROJECT_STATE.md
@.project-memory/TASKS.md
@.project-memory/CONTEXT.md
<!-- PMM:END -->
