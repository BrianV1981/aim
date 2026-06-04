import subprocess
import time
import os

def spawn_coagent(name, project_dir, prompt):
    if not os.path.isdir(project_dir):
        return {"error": f"Project directory not found: {project_dir}"}

    result = subprocess.run(["tmux", "has-session", "-t", name], capture_output=True)
    if result.returncode == 0:
        return {"error": f"Session '{name}' already exists."}

    cmd = ["tmux", "new-session", "-d", "-s", name, "-c", project_dir, "gemini", "--yolo"]
    subprocess.run(cmd, check=True)
    time.sleep(3)

    if prompt:
        send_message(name, prompt)

    return {"status": "spawned", "session": name, "cwd": project_dir}

def send_message(session_name, message):
    tmpfile = f"/tmp/coagent_{session_name}_{int(time.time())}.txt"
    with open(tmpfile, "w") as f:
        f.write(message)
    subprocess.run(["tmux", "load-buffer", tmpfile], check=True)
    subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
    try:
        os.remove(tmpfile)
    except:
        pass
    return {"status": "sent", "session": session_name, "length": len(message)}

def capture_output(session_name, lines=500):
    result = subprocess.run(["tmux", "capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"], capture_output=True, text=True)
    return {"session": session_name, "output": result.stdout}

def check_coagent(session_name):
    result = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    return {"session": session_name, "alive": result.returncode == 0}

def kill_coagent(session_name):
    result = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if result.returncode != 0:
        return {"error": f"Session '{session_name}' does not exist."}
    subprocess.run(["tmux", "kill-session", "-t", session_name], check=True)
    return {"status": "killed", "session": session_name}

def list_sessions():
    result = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"], capture_output=True, text=True)
    sessions = [s for s in result.stdout.strip().split("\n") if s]
    return {"sessions": sessions}
