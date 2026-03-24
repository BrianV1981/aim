import os
import re
import glob
import shutil

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
            
        # Archive
        archive_dir = os.path.join(aim_root, "memory/archive")
        os.makedirs(archive_dir, exist_ok=True)
        os.rename(latest_proposal, os.path.join(archive_dir, os.path.basename(latest_proposal)))
        return True
    except: return False
