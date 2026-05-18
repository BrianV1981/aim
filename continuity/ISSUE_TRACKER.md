# A.I.M. Issue Ledger

*Last Synchronized: 2026-05-15 10:50 PM*
*This file serves as the local, zero-latency index of all active project tasks.*

## 🟢 OPEN ISSUES (Actionable)

* **#36** - Fix: OpenCode runner — drain SQLite pipe, prevent answer-shift bug *(Created: 2026-05-16)*
* **#37** - Fix: RAG 5.2 recall failures — top_k=5 (reduced from 10) cuts off correct fragments outside top-5 window. Switch back to top_k=10 in retriever.py and mcp_server.py. *(Created: 2026-05-16)*
* **#39** - Enhancement: Simplify reincarnation protocol — eliminate REINCARNATION_CONNECT.md redundancy
  - **Context:** Reincarnation Pipeline
  - **Failure:** REINCARNATION_CONNECT.md is a redundant file. aim_reincarnate.py already prints the tmux session link to stdout (lines 185-198). The connect file duplicates this output and adds an unnecessary file to the pipeline. When not in tmux, the agent just needs to relay the stdout output to the operator.
  - **Intent:** 1. Remove REINCARNATION_CONNECT.md writing from aim_reincarnate.py (lines 156-198, keep the stdout print only). 2. Update AGENTS.md step 10c from 'read REINCARNATION_CONNECT.md' to 'extract the tmux session name from the script stdout output and display the link'. 3. Remove REINCARNATION_CONNECT.md reference from wake-up prompt in aim_reincarnate.py.
  - *(Created: 2026-05-18)*
* **#38** - Fix: Reincarnation protocol fails to display tmux session link to operator in OpenCode
  - **Context:** Reincarnation Pipeline
  - **Failure:** When triggered via opencode's run_shell_command, aim_reincarnate.py correctly spawns the new tmux session and writes REINCARNATION_CONNECT.md, but the agent never displays the session link to the operator. The script outputs to stdout which is captured silently. Additionally, the agent doesn't self-terminate after the handoff — it just continues running in the old session. The wake-up prompt also omits REINCARNATION_CONNECT.md from the reading list.
  - **Intent:** Update AGENTS.md step 10 (Agentic Reincarnation Protocol) to: after executing aim_reincarnate.py, read continuity/REINCARNATION_CONNECT.md and output its contents to the operator, then exit. Also add REINCARNATION_CONNECT.md to the wake-up prompt reading list in aim_reincarnate.py.
  - *(Created: 2026-05-18)*
