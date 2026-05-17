# A.I.M. Plan Pinger (Watchdog)

The `aim-plan-pinger` is a task-specific sentinel tool designed to ensure A.I.M. agents remain aligned with their active "Plan" or "Roadmap" during complex, multi-session operations.

## Operational Philosophy
Unlike system daemons, the Plan Pinger is **agent-initiated** and **task-specific**. You deploy it at the start of a plan, and you terminate it when the plan concludes. Its primary purpose is to inject "Sovereign Nudges" (`User hint:` via `tmux`) to keep the agent focused on its goals, preventing drift or "amnesia" in long-running sequences (e.g., executing 10+ benchmark sessions).

## Usage Patterns

The pinger supports two primary modes: **Interval** (Time-based) and **Watcher** (Event-based).

### 1. Timer-Based Pinger (The "Nudge")
Best for long tasks where you need a periodic reminder to check progress against the plan.
```bash
# Example: Ping every 30 minutes (1800 seconds)
tmux new-session -d -s pinger_session "python scripts/aim_plan_pinger.py --session <your_session_name> --interval 1800 --msg 'Keep moving! Are we still on track with the benchmark sessions? If done, kill this session.'"
```

### 2. Log-Tail Pinger (The "Event Monitor")
Best for chaining dependent tasks where you want an immediate nudge the moment a preceding task completes.
```bash
# Example: Monitor a log file for a specific pattern
tmux new-session -d -s pinger_session "python scripts/aim_plan_pinger.py --session <your_session_name> --tail ./daemon.log --pattern 'Task Complete' --msg 'The task is finished! Continue to the next session.'"
```

## Deployment Protocol
1.  **Deployment:** When starting a multi-stage plan, launch the pinger in a detached `tmux` session.
2.  **Monitoring:** The pinger runs asynchronously, observing your criteria.
3.  **Action:** Upon trigger, it injects the message into your active session's `tmux` buffer as a `User hint:`.
4.  **Shutdown:** **CRITICAL:** When the plan is successfully completed, you must manually terminate the pinger session to avoid residual alerts:
    ```bash
    tmux kill-session -t pinger_session
    ```

## Implementation Details
The tool is located at `scripts/aim_plan_pinger.py`. It is a lightweight Python script that leverages `tmux` as its primary communication interface to the agent.
