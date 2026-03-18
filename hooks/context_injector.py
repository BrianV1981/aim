#!/usr/bin/env python3
import os
import json
import glob
import sys
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
ALLOWED_ROOT = "/home/kingb"
AIM_ROOT = os.path.join(ALLOWED_ROOT, "aim")
CONTINUITY_DIR = os.path.join(AIM_ROOT, "continuity")

def get_latest_pulse():
    """Finds and reads the most recent context pulse from continuity/."""
    # Look for timestamped files: YYYY-MM-DD_HHMM.md
    pattern = os.path.join(CONTINUITY_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pattern)
    
    if not pulses:
        return None
    
    pulses.sort(reverse=True)
    latest_path = pulses[0]
    
    try:
        with open(latest_path, 'r') as f:
            content = f.read()
        return {
            "path": latest_path,
            "content": content
        }
    except Exception:
        return None

def get_git_delta(cwd):
    """Summarizes git status and diff --stat for offline awareness."""
    try:
        # Check if we are in a git repo
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                       cwd=cwd, check=True, capture_output=True, text=True)
        
        status = subprocess.check_output(["git", "status", "--short"], 
                                         cwd=cwd, text=True).strip()
        diff_stat = subprocess.check_output(["git", "diff", "HEAD", "--stat"], 
                                            cwd=cwd, text=True).strip()
        
        if not status and not diff_stat:
            return None
            
        delta = "### 📋 Git Offline Awareness (Delta)\n"
        if status:
            delta += f"**Status:**\n```text\n{status}\n```\n"
        if diff_stat:
            delta += f"**Diff Stat:**\n```text\n{diff_stat}\n```\n"
        return delta
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_project_context(cwd):
    """Searches for CONTEXT.md in cwd or its parents (stops at ALLOWED_ROOT)."""
    current = os.path.abspath(cwd)
    while current.startswith(ALLOWED_ROOT):
        context_file = os.path.join(current, "CONTEXT.md")
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    content = f.read()
                return {
                    "path": context_file,
                    "content": content
                }
            except Exception:
                pass
        
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None

def main():
    try:
        # 1. Read input from Gemini CLI
        input_data = sys.stdin.read()
        cwd = os.getcwd()
        if input_data:
            data = json.loads(input_data)
            cwd = data.get('dir_path', cwd)
            
        # 2. Scope Check: Activity restricted to /home/kingb/
        abs_cwd = os.path.abspath(os.path.expanduser(cwd))
        if not abs_cwd.startswith(ALLOWED_ROOT):
            print(json.dumps({}))
            return
            
    except Exception:
        print(json.dumps({}))
        return

    injection_parts = []

    # 3. Project-Specific CONTEXT.md
    project_context = get_project_context(abs_cwd)
    if project_context:
        injection_parts.append(f"## 📁 Project Context: {os.path.basename(os.path.dirname(project_context['path']))}\n{project_context['content']}")

    # 4. Git Delta Injection
    git_delta = get_git_delta(abs_cwd)
    if git_delta:
        injection_parts.append(git_delta)

    # 5. A.I.M. Latest Pulse (The Brain)
    pulse = get_latest_pulse()
    if pulse:
        injection_parts.append(f"## 🧠 A.I.M. Context Pulse: {os.path.basename(pulse['path'])}\n{pulse['content']}")

    if not injection_parts:
        print(json.dumps({}))
        return

    # 6. Combine and Inject
    final_injection = "\n--- [A.I.M. AUTOMATIC CONTEXT INJECTION] ---\n\n"
    final_injection += "\n\n---\n\n".join(injection_parts)
    final_injection += "\n\n--- [END INJECTION] ---\n"
    
    print(json.dumps({
        "content": final_injection
    }))

if __name__ == "__main__":
    main()
