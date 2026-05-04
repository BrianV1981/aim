---
name: coagent-swarm
description: Teaches OpenCode agents the tmux co-agent protocols — spawning co-agents, inter-agent messaging via buffer paste, TUI vs Run mode, chalkboard file sharing, and Ghost Operator patterns from the A.I.M. Swarm ecosystem.
---

# coagent-swarm

Teaches OpenCode agents how to communicate with other co-agents using tmux sessions, buffer injection, chalkboard file sharing, and the Ghost Operator protocol.

## When to Use This Skill

- You need to spawn a co-agent in another tmux session to handle a parallel task
- You need to send a message or directive to a running co-agent
- You need to check on a co-agent's progress or read its output
- You're building a benchmark runner that needs to inject questions into a live agent
- You need to coordinate multiple agents working on different parts of a shared project

## Co-Agent vs. Run Mode

| | **TUI Mode (Co-Agent)** | **Run Mode (Single-Shot)** |
|---|---|---|
| Command | `tmux new-session -d -s <name> -c <dir> opencode` | `opencode run "prompt"` |
| Lifetime | Persistent — stays alive across prompts | One response, then exits |
| Communication | tmux buffer paste, chalkboard files | Command-line args only |
| Use case | Long-lived co-agent, benchmark testing | Quick one-off task |
| Response reading | `tmux capture-pane -t <session> -p` | stdout capture |

## Core Protocol: Tmux Buffer Injection

The universal pattern for sending messages to a co-agent in TUI mode:

```bash
# Step 1: Spawn the co-agent in a detached tmux session
tmux new-session -d -s coagent_name -c /path/to/project opencode

# Step 2: Write the prompt to a temp file (avoids shell escaping issues)
echo "Your directive here. Read AGENTS.md for context." > /tmp/coagent_prompt.txt

# Step 3: Inject via tmux buffer
tmux load-buffer /tmp/coagent_prompt.txt
tmux paste-buffer -t coagent_name

# Step 4: Send Enter as a SEPARATE command (prevents swallowing by interactive prompts)
tmux send-keys -t coagent_name Enter
```

**Critical:** Step 4 MUST be a separate command. Running `paste-buffer` followed by `send-keys Enter` in the same command can cause the Enter to be swallowed by an interactive TUI prompt.

## Reading Co-Agent Responses

```bash
# Capture the visible pane content
tmux capture-pane -t coagent_name -p

# Capture with scrollback history (last 2000 lines)
tmux capture-pane -t coagent_name -p -S -2000

# Monitor for a specific tag (e.g., [ANSWER] for benchmarks)
tmux capture-pane -t coagent_name -p | grep "\[ANSWER\]"
```

## The Chalkboard Protocol (File-Based Messaging)

For asynchronous message passing between co-agents:

```bash
# SENDING: Write a message to the co-agent's inbox
echo "Priority task: audit the LanceDB schema" > /path/to/coagent/workspace/aim-chalkboard/inbox/task_$(date +%s).md

# RECEIVING: Check your own inbox
ls workspace/aim-chalkboard/inbox/
cat workspace/aim-chalkboard/inbox/*.md
```

## Ghost Operator Protocol (Benchmark Testing)

The full pattern used by `benchmark_results/runners/locomo_ghost_operator_v2.py`:

```python
import subprocess, time, os

# 1. Spawn the agent in a detached tmux session
subprocess.run(["tmux", "new-session", "-d", "-s", "ghost_aim",
    "-c", "/home/kingb/aim-locomo", "opencode"])

# 2. Wait for TUI to boot
time.sleep(5)

# 3. Inject primer message
with open("/tmp/primer.txt", "w") as f:
    f.write("Read AGENTS.md. Answer benchmark questions with [ANSWER] tags.")
subprocess.run(["tmux", "load-buffer", "/tmp/primer.txt"])
subprocess.run(["tmux", "paste-buffer", "-t", "ghost_aim"])
subprocess.run(["tmux", "send-keys", "-t", "ghost_aim", "Enter"])

# 4. Loop: inject questions, monitor for [ANSWER], collect results
for question in questions:
    with open("/tmp/q.txt", "w") as f:
        f.write(question)
    subprocess.run(["tmux", "load-buffer", "/tmp/q.txt"])
    subprocess.run(["tmux", "paste-buffer", "-t", "ghost_aim"])
    subprocess.run(["tmux", "send-keys", "-t", "ghost_aim", "Enter"])

    # Wait and capture
    time.sleep(60)
    output = subprocess.check_output(
        ["tmux", "capture-pane", "-t", "ghost_aim", "-p", "-S", "-500"]
    ).decode()
    # Parse [ANSWER] from output...

# 5. Clean up
subprocess.run(["tmux", "kill-session", "-t", "ghost_aim"])
```

## Session Management

```bash
# List all running tmux sessions
tmux list-sessions

# Attach to a co-agent (view its screen live)
tmux attach-session -t coagent_name

# Kill a co-agent when done
tmux kill-session -t coagent_name

# Check if a session exists
tmux has-session -t coagent_name 2>/dev/null && echo "alive" || echo "dead"
```

## Safety Rules

1. **Never run `tmux kill-server`** — this kills ALL sessions including your own
2. **Use `tmux has-session` before spawning** — prevents duplicate sessions
3. **Always detach after attaching** — `Ctrl+B, D` to detach, never close the terminal
4. **Clean up sessions when done** — `tmux kill-session -t <name>` after task completion
5. **Temp files in /tmp** — write prompts to `/tmp/` not project directories to avoid git noise

## Co-Agent Directory Structure

When spawning a co-agent, give it its own isolated project:

```
/path/to/projects/
├── main_project/          # Your workspace
├── coagent_auditor/       # Co-agent's isolated workspace
│   ├── AGENTS.md          # Role-specific persona
│   ├── workspace/
│   │   └── aim-chalkboard/
│   │       ├── inbox/     # Receives tasks from you
│   │       └── outbox/    # Delivers results to you
│   └── ...
└── coagent_runner/        # Another co-agent
```

To execute this skill, run the included Python script with a JSON action:

```bash
python3 scripts/run.py '{"action":"spawn","name":"auditor","project":"/path/to/dir","prompt":"audit the retriever"}'
```

Or for checking a co-agent:

```bash
python3 scripts/run.py '{"action":"check","name":"auditor"}'
```
