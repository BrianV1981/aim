#!/home/kingb/aim/venv/bin/python3
import os
import json
import glob
import sys
import subprocess
import math
import keyring
from google import genai
from datetime import datetime

# --- CONFIGURATION (Load from core/CONFIG.json) ---
# We try to find the AIM_ROOT dynamically
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim" # Default fallback

CWD = os.getcwd()
AIM_ROOT = find_aim_root(CWD)
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ALLOWED_ROOT = CONFIG['settings']['allowed_root']
CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
MEMORY_MD_PATH = os.path.join(CONFIG['paths']['core_dir'], "MEMORY.md")
EMBEDDING_MODEL = CONFIG['models']['embedding']
PRUNING_THRESHOLD = CONFIG['settings']['semantic_pruning_threshold']

# API Client
API_KEY = keyring.get_password("aim-system", "google-api-key")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    return dot_product / (magnitude1 * magnitude2)

def get_embedding(text):
    if not client: return None
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config={'task_type': 'RETRIEVAL_DOCUMENT'}
        )
        return result.embeddings[0].values
    except Exception:
        return None

def get_latest_pulse():
    pattern = os.path.join(CONTINUITY_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pattern)
    if not pulses: return None
    pulses.sort(reverse=True)
    try:
        with open(pulses[0], 'r') as f:
            return {"path": pulses[0], "content": f.read()}
    except Exception:
        return None

def get_git_delta(cwd):
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd, check=True, capture_output=True, text=True)
        status = subprocess.check_output(["git", "status", "--short"], cwd=cwd, text=True).strip()
        diff_stat = subprocess.check_output(["git", "diff", "HEAD", "--stat"], cwd=cwd, text=True).strip()
        if not status and not diff_stat: return None
        delta = "### 📋 Git Offline Awareness (Delta)\n"
        if status: delta += f"**Status:**\n```text\n{status}\n```\n"
        if diff_stat: delta += f"**Diff Stat:**\n```text\n{diff_stat}\n```\n"
        return delta
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_project_context(cwd):
    current = os.path.abspath(cwd)
    while current.startswith(ALLOWED_ROOT):
        context_file = os.path.join(current, "CONTEXT.md")
        if os.path.exists(context_file):
            try:
                with open(context_file, 'r') as f:
                    return {"path": context_file, "content": f.read()}
            except Exception: pass
        parent = os.path.dirname(current)
        if parent == current: break
        current = parent
    return None

def main():
    try:
        input_data = sys.stdin.read()
        cwd = CWD
        if input_data:
            data = json.loads(input_data)
            cwd = data.get('dir_path', cwd)
        abs_cwd = os.path.abspath(os.path.expanduser(cwd))
        if not abs_cwd.startswith(ALLOWED_ROOT):
            print(json.dumps({}))
            return
    except Exception:
        print(json.dumps({}))
        return

    injection_parts = []
    
    # Core Memory for Semantic Pruning
    core_memory_text = ""
    if os.path.exists(MEMORY_MD_PATH):
        with open(MEMORY_MD_PATH, 'r') as f:
            core_memory_text = f.read()
    core_embedding = get_embedding(core_memory_text) if core_memory_text else None

    # 1. Project-Specific CONTEXT.md
    project_context = get_project_context(abs_cwd)
    if project_context:
        # Pruning check: Is this project context already in core memory?
        if core_embedding:
            proj_embedding = get_embedding(project_context['content'])
            if cosine_similarity(core_embedding, proj_embedding) < PRUNING_THRESHOLD:
                injection_parts.append(f"## 📁 Project Context: {os.path.basename(os.path.dirname(project_context['path']))}\n{project_context['content']}")
        else:
            injection_parts.append(f"## 📁 Project Context: {os.path.basename(os.path.dirname(project_context['path']))}\n{project_context['content']}")

    # 2. Git Delta Injection (Never Pruned - always dynamic)
    git_delta = get_git_delta(abs_cwd)
    if git_delta:
        injection_parts.append(git_delta)
# 5. A.I.M. Latest Pulse (Pruned against Core)
pulse = get_latest_pulse()

# --- PILLAR B: CRASH RECOVERY (Interim Backup) ---
backup_path = os.path.join(AIM_ROOT, "continuity/INTERIM_BACKUP.json")
if os.path.exists(backup_path):
    # If the backup exists and is NEWER than the latest pulse, it means we crashed
    backup_mtime = os.path.getmtime(backup_path)
    pulse_mtime = os.path.getmtime(pulse['path']) if pulse else 0

    if backup_mtime > pulse_mtime:
        try:
            with open(backup_path, 'r') as bf:
                backup_data = json.load(bf)
                # We inject a warning and the raw recovery data
                warning_msg = "## ⚠️ CRASH RECOVERY DETECTED\n"
                warning_msg += "The previous session ended abruptly. You are reading from the raw `INTERIM_BACKUP.json` because a clean Continuity Pulse was not generated.\n"
                warning_msg += "**CRITICAL DIRECTIVE:** The state is fragile. You MUST ask the Operator for context clarification or confirm your next steps before executing any tools.\n"
                warning_msg += "Here is the last captured context:\n"
                injection_parts.append(f"{warning_msg}```json\n{json.dumps(backup_data.get('session_history', [])[-5:], indent=2)}\n```")
        except: pass
# --------------------------------------------------

if pulse:

        if core_embedding:
            pulse_embedding = get_embedding(pulse['content'])
            # We only inject the pulse if it's significantly different from Core Memory
            if cosine_similarity(core_embedding, pulse_embedding) < PRUNING_THRESHOLD:
                injection_parts.append(f"## 🧠 A.I.M. Context Pulse: {os.path.basename(pulse['path'])}\n{pulse['content']}")
        else:
            injection_parts.append(f"## 🧠 A.I.M. Context Pulse: {os.path.basename(pulse['path'])}\n{pulse['content']}")

    # --- PILLAR A: HEARTBEAT SCOPE INJECTION ---
    heartbeat_path = os.path.join(CONFIG['paths']['core_dir'], "HEARTBEAT.md")
    if os.path.exists(heartbeat_path):
        try:
            with open(heartbeat_path, 'r') as f:
                injection_parts.append(f"## 💓 A.I.M. Heartbeat Protocol\n{f.read()}")
        except: pass
    # -------------------------------------------

    if not injection_parts:
        print(json.dumps({}))
        return

    # --- PILLAR D: PENDING MEMORY PROPOSAL (Visibility) ---
    proposal_path = os.path.join(AIM_ROOT, "memory/DISTILLATION_PROPOSAL.md")
    if os.path.exists(proposal_path):
        mtime = os.path.getmtime(proposal_path)
        # Check if the proposal is NEWER than the last MEMORY.md update
        memory_mtime = os.path.getmtime(MEMORY_MD_PATH)
        if mtime > memory_mtime:
            warning = "## 🧠 PENDING MEMORY PROPOSAL DETECTED\n"
            warning += "There is an uncommitted memory distillation proposal in `memory/DISTILLATION_PROPOSAL.md`.\n"
            warning += "**URGENT DIRECTIVE:** You MUST notify the Operator immediately and ask for approval to commit these updates via `aim commit`.\n"
            injection_parts.append(warning)
    # ------------------------------------------------------

    final_injection = "\n--- [A.I.M. AUTOMATIC CONTEXT INJECTION (Semantically Pruned)] ---\n\n"
    final_injection += "\n\n---\n\n".join(injection_parts)
    final_injection += "\n\n--- [END INJECTION] ---\n"
    
    print(json.dumps({"content": final_injection}))

if __name__ == "__main__":
    main()
