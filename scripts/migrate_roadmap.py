import os
import re
import subprocess

roadmap_path = "docs/ROADMAP.md"

with open(roadmap_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_phase = None
issues_created = 0

for line in lines:
    # Match phase headers: ## Phase 39: The Sovereign Comlink (Full Two-Way Remote CLI) [PLANNED]
    phase_match = re.match(r"^##\s+(Phase\s+\d+:\s+.*?)\s+\[.*\]", line)
    if phase_match:
        current_phase = phase_match.group(1).strip()
        continue
    
    # Match incomplete tasks: - [ ] **Task Name:** Task description
    task_match = re.match(r"^\-\s+\[\s\]\s+\*\*(.*?)\*\*(.*)", line)
    if task_match and current_phase:
        # Ignore the task we just created manually
        if "Migrate Roadmap to GitHub Issues" in line:
            continue
            
        task_name = task_match.group(1).strip()
        task_desc = task_match.group(2).strip()
        
        # Clean up leading colons or spaces in desc
        if task_desc.startswith(":"):
            task_desc = task_desc[1:].strip()
            
        title = f"[{current_phase.split(':')[0]}] {task_name.strip(':')}"
        body = f"{task_desc}\n\n*Auto-generated from ROADMAP.md under {current_phase}*"
        
        print(f"Creating issue: {title}")
        try:
            subprocess.run(
                ["gh", "issue", "create", "--title", title, "--body", body],
                check=True
            )
            issues_created += 1
        except subprocess.CalledProcessError as e:
            print(f"Failed to create issue '{title}': {e}")

print(f"\nSuccessfully created {issues_created} issues from ROADMAP.md!")
