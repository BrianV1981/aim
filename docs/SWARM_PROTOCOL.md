# SWARM_PROTOCOL.md — A.I.M. Co-Agent Communication

> Canonical reference for inter-agent communication in the A.I.M. Swarm ecosystem.  
> Source: patterns extracted from `aim-swarm/docs/TMUX_AIM_SWARM.md`,  
> `benchmark_results/runners/`, and operational experience.

## Co-Agent vs. Sub-Agent

| | Co-Agent | Sub-Agent |
|---|---|---|
| **Lifetime** | Persistent — survives across tasks | Fleeting — killed after one response |
| **Workspace** | Own directory, AGENTS.md, git history | Shared with parent |
| **Communication** | tmux buffer paste, chalkboard files | stdin/stdout or subprocess pipe |
| **Identity** | Sovereign — its own persona and mandates | Anonymous — just a function call |
| **Spawn** | `tmux new-session -d -s <name> -c <dir> opencode` | `opencode run "prompt"` or `Popen` |

## TUI Mode vs. Run Mode

```
TUI MODE (co-agent):        RUN MODE (single-shot):
┌─────────────────────┐      ┌──────────────────┐
│ tmux session         │      │ opencode run "x"  │
│ ├── opencode (TUI)   │      │ stdout → captured │
│ │   └── waits idle   │      │ process → exits   │
│ │       for prompts  │      └──────────────────┘
│ └── agent answers    │
│     and waits again   │
└─────────────────────┘
```

**When to use TUI Mode:**
- The co-agent needs to answer multiple prompts over time
- The co-agent needs to run long searches or reasoning chains
- You're benchmarking and need to monitor progress
- The co-agent maintains state (conversation history, tool results)

**When to use Run Mode:**
- Single question, single answer
- The agent doesn't need to maintain context between calls
- Scripted pipelines where you just need the output
- Quick lookups: `opencode run "search for X" --json`

## The Buffer Injection Protocol

The universal pattern. Works identically for `opencode` and `gemini`:

```bash
# 1. SPAWN (TUI mode, detached)
tmux new-session -d -s agent_name -c /path/to/project opencode
sleep 5  # Wait for TUI boot

# 2. INJECT (write prompt to temp file, load into tmux buffer, paste, send Enter)
cat > /tmp/prompt.txt << 'EOF'
Read AGENTS.md for your operational constraints.
Search the database for "Caroline support group".
Respond with [ANSWER] tag.
EOF
tmux load-buffer /tmp/prompt.txt
tmux paste-buffer -t agent_name
sleep 0.5
tmux send-keys -t agent_name Enter   # MUST be separate from paste-buffer

# 3. MONITOR (capture pane output)
sleep 30  # Wait for agent to process
tmux capture-pane -t agent_name -p -S -1000 | grep "\[ANSWER\]"

# 4. CLEANUP
tmux kill-session -t agent_name
```

**Why the Enter must be separate:** Interactive TUI prompts (like confirmations) can consume the Enter key if it's sent in the same buffer as the paste. Separating them guarantees the Enter hits the chat input.

## The Chalkboard Protocol (File-Based Messaging)

For coordination between long-lived co-agents that need to exchange tasks and results asynchronously:

```bash
# Directory structure
workspace/aim-chalkboard/
├── inbox/      # Agent reads tasks from here
├── outbox/     # Agent writes results here
└── shared/     # Shared reference files (datasets, manifests)
```

**Sending a task to a co-agent:**
```bash
echo "# Task: Audit LanceDB Schema\n\nCheck that the fragments table has the correct 768-dim vector field." \
  > /path/to/coagent/workspace/aim-chalkboard/inbox/task_$(date +%s).md
```

**Co-agent checking its inbox:**
```bash
for task in workspace/aim-chalkboard/inbox/*.md; do
    echo "Processing: $(basename $task)"
    # ... process task ...
    mv "$task" workspace/aim-chalkboard/outbox/
done
```

## The Ghost Operator Protocol (Benchmark Runner Pattern)

Full Python implementation pattern — used by all benchmark runners:

```python
import subprocess, time, os, json

class GhostOperator:
    def __init__(self, session_name, project_dir, agent_binary="opencode"):
        self.session = session_name
        self.project = project_dir
        self.binary = agent_binary

    def spawn(self, primer_prompt=None):
        """Spawn the agent in a detached tmux session."""
        subprocess.run(["tmux", "new-session", "-d", "-s", self.session,
                       "-c", self.project, self.binary], check=True)
        time.sleep(5)
        if primer_prompt:
            self.inject(primer_prompt)

    def inject(self, message, wait=30):
        """Inject a message and wait for response."""
        tmp = f"/tmp/ghost_{self.session}_{int(time.time())}.txt"
        with open(tmp, "w") as f:
            f.write(message)
        subprocess.run(["tmux", "load-buffer", tmp], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", self.session], check=True)
        time.sleep(0.5)
        subprocess.run(["tmux", "send-keys", "-t", self.session, "Enter"], check=True)
        os.remove(tmp)
        time.sleep(wait)

    def capture(self, lines=500):
        """Capture pane output."""
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", self.session, "-p", "-S", f"-{lines}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout

    def kill(self):
        subprocess.run(["tmux", "kill-session", "-t", self.session], check=False)

    def is_alive(self):
        result = subprocess.run(["tmux", "has-session", "-t", self.session], capture_output=True)
        return result.returncode == 0
```

## Session Management Reference

```bash
# List sessions
tmux list-sessions

# Attach to a session (Ctrl+B, D to detach)
tmux attach-session -t agent_name

# Send Ctrl+C (interrupt)
tmux send-keys -t agent_name C-c

# Send Ctrl+D (EOF / exit)
tmux send-keys -t agent_name C-d

# Kill a specific session
tmux kill-session -t agent_name

# Kill all sessions except current
tmux kill-session -a
```

## Cross-Ecosystem Compatibility

The buffer injection protocol works identically across:

| Agent CLI | TUI Spawn Command | Notes |
|---|---|---|
| **OpenCode** | `tmux new-session -d -s <name> -c <dir> opencode` | Uses `opencode.json` config |
| **Gemini CLI** | `tmux new-session -d -s <name> -c <dir> gemini --yolo` | Uses `.gemini/settings.json` |
| **A.I.M. (scripts)** | `tmux new-session -d -s <name> -c <dir> <project-alias>` | Uses venv/bin/python aim_cli.py |

The buffer injection (`load-buffer` → `paste-buffer` → `send-keys Enter`) is tmux-native and works with any TUI application.

## Common Pitfalls

| Problem | Cause | Fix |
|---|---|---|
| Agent ignores first prompt | TUI hasn't finished booting | Increase sleep to 5-8 seconds |
| Prompt truncated mid-line | Special characters in prompt | Write to temp file, use `load-buffer` not `send-keys` |
| Enter key swallowed | Interactive confirmation prompt consumed it | Always send Enter as separate command |
| Can't capture output | Pane history too short | Use `-S -2000` to capture scrollback |
| `tmux kill-server` kills everything | Misunderstanding scope | NEVER use kill-server. Use `kill-session -t <name>` |
| Agent tool call fails on `gemini` binary | Gemini CLI not in PATH | Use full path or ensure `which gemini` works |
| Agent tool call fails on `opencode` binary | OpenCode not authenticated | Run `opencode connect` first |
