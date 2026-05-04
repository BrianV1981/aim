#!/usr/bin/env python3
"""
coagent-swarm skill executor — spawn, message, and manage OpenCode co-agents via tmux.

Usage:
  python3 scripts/run.py '{"action":"spawn","name":"auditor","project":"/path/to/dir","prompt":"your prompt"}'
  python3 scripts/run.py '{"action":"send","name":"auditor","message":"hello"}'
  python3 scripts/run.py '{"action":"check","name":"auditor"}'
  python3 scripts/run.py '{"action":"capture","name":"auditor","lines":500}'
  python3 scripts/run.py '{"action":"kill","name":"auditor"}'
  python3 scripts/run.py '{"action":"list"}'
"""
import sys
import json
import subprocess
import time
import os


def spawn_coagent(name, project_dir, prompt, model=None):
    """Spawn a persistent co-agent in a detached tmux session (TUI mode)."""
    if not os.path.isdir(project_dir):
        return {"error": f"Project directory not found: {project_dir}"}

    # Check if session already exists
    result = subprocess.run(["tmux", "has-session", "-t", name],
                          capture_output=True)
    if result.returncode == 0:
        return {"error": f"Session '{name}' already exists. Use kill first or choose a different name."}

    # Spawn in TUI mode
    cmd = ["tmux", "new-session", "-d", "-s", name, "-c", project_dir, "opencode"]
    subprocess.run(cmd, check=True)
    time.sleep(3)  # Wait for TUI to render

    # Inject prompt if provided
    if prompt:
        send_message(name, prompt)

    return {"status": "spawned", "session": name, "cwd": project_dir}


def send_message(session_name, message):
    """Send a message to a running co-agent via tmux buffer paste."""
    tmpfile = f"/tmp/coagent_{session_name}_{int(time.time())}.txt"
    with open(tmpfile, "w") as f:
        f.write(message)

    subprocess.run(["tmux", "load-buffer", tmpfile], check=True)
    subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)

    os.remove(tmpfile)
    return {"status": "sent", "session": session_name, "length": len(message)}


def capture_output(session_name, lines=500):
    """Capture the visible pane content from a co-agent."""
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"],
        capture_output=True, text=True
    )
    return {"session": session_name, "output": result.stdout}


def check_coagent(session_name):
    """Check if a co-agent session exists and return its status."""
    result = subprocess.run(["tmux", "has-session", "-t", session_name],
                          capture_output=True)
    alive = result.returncode == 0
    return {"session": session_name, "alive": alive}


def kill_coagent(session_name):
    """Kill a co-agent's tmux session."""
    result = subprocess.run(["tmux", "has-session", "-t", session_name],
                          capture_output=True)
    if result.returncode != 0:
        return {"error": f"Session '{session_name}' does not exist."}

    subprocess.run(["tmux", "kill-session", "-t", session_name], check=True)
    return {"status": "killed", "session": session_name}


def list_sessions():
    """List all running tmux sessions."""
    result = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"],
                          capture_output=True, text=True)
    sessions = [s for s in result.stdout.strip().split("\n") if s]
    return {"sessions": sessions}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: run.py '<json_args>'"}, indent=2))
        return

    try:
        args = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}, indent=2))
        return

    action = args.get("action", "list")

    try:
        if action == "spawn":
            name = args.get("name", "coagent")
            project = args.get("project", os.getcwd())
            prompt = args.get("prompt", "")
            result = spawn_coagent(name, project, prompt)

        elif action == "send":
            name = args["name"]
            message = args["message"]
            result = send_message(name, message)

        elif action == "capture":
            name = args["name"]
            lines = int(args.get("lines", 500))
            result = capture_output(name, lines)

        elif action == "check":
            name = args["name"]
            result = check_coagent(name)

        elif action == "kill":
            name = args["name"]
            result = kill_coagent(name)

        elif action == "list":
            result = list_sessions()

        else:
            result = {"error": f"Unknown action: {action}. Valid: spawn, send, capture, check, kill, list"}

    except subprocess.CalledProcessError as e:
        result = {"error": f"tmux command failed: {e}"}
    except KeyError as e:
        result = {"error": f"Missing required argument: {e}"}
    except Exception as e:
        result = {"error": str(e)}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
