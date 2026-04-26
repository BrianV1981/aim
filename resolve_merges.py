import os, subprocess, re

def resolve_version():
    if not os.path.exists("VERSION"): return
    with open("VERSION", "r") as f: content = f.read()
    versions = re.findall(r"v1\.\d+\.\d+", content)
    if not versions: return
    highest = sorted(versions, key=lambda x: [int(p) for p in x[1:].split('.')])[-1]
    with open("VERSION", "w") as f: f.write(highest + "\n")

def resolve_changelog():
    if not os.path.exists("CHANGELOG.md"): return
    with open("CHANGELOG.md", "r") as f: lines = f.readlines()
    out = []
    in_conflict = False
    for line in lines:
        if line.startswith("<<<<<<<"): in_conflict = True; continue
        if line.startswith("======="): continue
        if line.startswith(">>>>>>>"): in_conflict = False; continue
        out.append(line)
    
    # Deduplicate empty lines
    clean_out = []
    for line in out:
        if line.strip() == "" and clean_out and clean_out[-1].strip() == "": continue
        clean_out.append(line)
        
    with open("CHANGELOG.md", "w") as f: f.writelines(clean_out)

def merge_branch(branch):
    print(f"Merging {branch}...")
    res = subprocess.run(["git", "merge", branch, "--no-edit"], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Conflict detected in {branch}. Resolving...")
        resolve_version()
        resolve_changelog()
        
        # Check if there are other conflicts
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        for line in status.split("\n"):
            if line.startswith("UU "):
                conflicted_file = line[3:]
                if conflicted_file not in ["VERSION", "CHANGELOG.md"]:
                    print(f"WARNING: Unhandled conflict in {conflicted_file}")
                    # We will accept 'theirs' for python files as a brute force, then manually patch if needed
                    subprocess.run(["git", "checkout", "--theirs", conflicted_file])
                    
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Merge {branch} with auto-resolve"])

for b in ["fix/issue-437", "fix/issue-438", "fix/issue-439", "fix/issue-440"]:
    merge_branch(b)
