# Sessao 2026-07-11 - desacoplamento-bonder

- **Projeto:** bonder (repositorio proprio `luizdione/bonder`, privado)
- **Data/hora:** 2026-07-11 14:50

## Objetivos atingidos
- Desacoplar o bonder do `docking_suite` em tres frentes (memoria, repo proprio e
  docking_suite), eliminando a interpretacao dubia "bonder espelha docking".
- Reafirmar o escopo: bonder e dedicado **SO a interacao proteina-proteina por
  espectrometria de massas** (CoIP-MS / AP-MS) — nao docking molecular.

## Decisoes
- Bonder e repositorio **proprio e independente** (`luizdione/bonder`), sem upstream
  nem sincronizacao externa; a fonte da verdade do codigo passa a ser este repo.
- Historico antigo (linhagem `docking_suite`) **descartado** via reset do zero
  (1 commit unico), a pedido do autor.
- No `docking_suite` o bonder estava isolado no branch
  `claude/bonder-proteome-platform-k8m6pa`; optou-se por **deletar o branch inteiro**
  (main/docking intacto) em vez de remover so a subpasta.

## Arquivos modificados
- **Memoria PMM** (`.project-memory/`): purga de docking/mirror/sync em CLAUDE,
  CONTEXT, ISSUES (I-0004 -> RESOLVIDO), KNOWLEDGE, PROJECT_STATE e ROADMAP (uma
  linha de plano editorial reescrita como "interatoma-alvo (analise)", para o gate
  `app`); TASKS (T-0008 -> DONE).
- **Raiz do repo:** `sync.ps1` **removido**; `.gitignore` passou a excluir
  `formularios/`; `CHANGELOG.md` canonico ganhou entradas Alterado/Removido.

## Tarefas concluidas
- T-0008 - Desacoplamento completo (memoria + reset do repo + limpeza do docking_suite).

## Git / GitHub (acoes externas realizadas)
- **`luizdione/bonder`** (privado): reset do zero -> **1 commit `adc37a3`**
  (force-push `d537168...adc37a3`). Gate `git_dione` (policy app) LIMPO. Commit
  **sem trailer de IA**. `formularios/` e dados fora do git.
- **`luizdione/docking_suite`** (privado): branch
  `claude/bonder-proteome-platform-k8m6pa` **DELETADO** (SHA recuperavel
  `e03d8d20787ab7c7747d960aa0c90e333a56f250`); **PR #1** "feat(bonder)..." fechado
  automaticamente. `main` (docking) e o branch `claude/fork-full-context-...` intactos.

## Proximas acoes
- (Opcional) commit+push desta sincronizacao de memoria PMM para `luizdione/bonder`.
- Retomar o gargalo real: submissao a plataforma de MS (`formularios/`) -> definir
  instrumento (HF-X) + aquisicao (DDA/DIA) -> obter `.raw` -> rodar `NSs_vs_CTRL` /
  `LGALS3_vs_CTRL`.
- No 1o `bonder db sync`, travar os sha256 dos bancos.
