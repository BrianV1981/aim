import os
import re
import glob
import shutil
import json
from datetime import datetime, timedelta

def find_aim_root():
    """Dynamically discovers the A.I.M. root directory."""
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")

def should_run_tier(tier_name, interval_hours):
    """Checks if the specified tier is due for execution based on the interval."""
    if not os.path.exists(STATE_FILE):
        return True # Run if no state exists
        
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        last_run_str = state.get('tiers', {}).get(tier_name, {}).get('last_run')
        if not last_run_str:
            return True
            
        last_run = datetime.fromisoformat(last_run_str)
        if datetime.now() >= last_run + timedelta(hours=interval_hours):
            return True
    except:
        return True
    return False

def mark_tier_run(tier_name):
    """Updates the state file with the current timestamp for the tier."""
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except: pass
    
    if 'tiers' not in state: state['tiers'] = {}
    if tier_name not in state['tiers']: state['tiers'][tier_name] = {}
    
    state['tiers'][tier_name]['last_run'] = datetime.now().isoformat()
    
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def cleanup_consumed_files(file_paths, cleanup_mode="archive"):
    """Performs the 'Consume & Clean' operation."""
    if not file_paths: return
    
    archive_dir = os.path.join(AIM_ROOT, "memory/archive")
    os.makedirs(archive_dir, exist_ok=True)
    
    for f in file_paths:
        if not os.path.exists(f): continue
        
        if cleanup_mode == "delete":
            try: os.remove(f)
            except: pass
        else:
            # Default to archive
            try:
                dest = os.path.join(archive_dir, os.path.basename(f))
                # Handle filename collisions in archive
                if os.path.exists(dest):
                    ts = datetime.now().strftime("%H%M%S")
                    dest = dest.replace(".md", f"_{ts}.md")
                shutil.move(f, dest)
            except: pass

def commit_proposal(aim_root):
    proposal_dir = os.path.join(aim_root, "memory/proposals")
    memory_path = os.path.join(aim_root, "core/MEMORY.md")
    
    if not os.path.exists(proposal_dir): return False
    
    proposals = glob.glob(os.path.join(proposal_dir, "PROPOSAL_*.md"))
    if not proposals: return False

    proposals.sort(reverse=True)
    latest_proposal = proposals[0]

    try:
        with open(latest_proposal, 'r') as f:
            content = f.read()
            
        if "### 3. MEMORY DELTA" in content:
            delta_part = content.split("### 3. MEMORY DELTA")[1].strip()
            delta = re.sub(r"^```(markdown|md)?\n", "", delta_part)
            delta = re.sub(r"\n```$", "", delta).strip()
        else:
            delta = content.strip()
        
        with open(memory_path, 'w') as f:
            f.write(delta)
            
        # Archive the committed proposal
        archive_dir = os.path.join(aim_root, "memory/archive")
        os.makedirs(archive_dir, exist_ok=True)
        os.rename(latest_proposal, os.path.join(archive_dir, os.path.basename(latest_proposal)))
        return True
    except: return False
