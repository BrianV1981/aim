# A.I.M. GitOps Deployment Rules (The Atomic Architecture)

This document defines the strict version control protocols that all A.I.M. agents must follow. To prevent autonomous agents from destroying the `main` branch or generating complex merge conflicts, A.I.M. enforces an "Atomic Deployment" architecture via specialized CLI commands.

## 1. The Prime Directive
**AI agents are strictly forbidden from executing raw `git commit` or `git push` commands.** 
Every single bug fix, feature, or documentation update must be deployed immediately using the A.I.M. GitOps wrapper commands.

## 2. The Deployment Pipeline

### Step 1: Report & Track (`aim bug`)
Agents must never start coding without an explicit issue ticket.
*   **Command:** `aim bug "<Description of the issue>"` (or `aim bug-operator` for internal OS tasks).
*   **Action:** This interfaces with the GitHub CLI (`gh`) to create a structured issue ticket and returns an Issue ID.
*   **Rule:** The issue description must be concise but exhaustive, detailing the specific failure mode or requested enhancement.

### Step 2: Surgical Isolation (`aim fix`)
Agents must never code directly on the `main` branch.
*   **Command:** `aim fix <Issue_ID>`
*   **Action:** The CLI automatically checks out a clean Git worktree (e.g., `fix/issue-42`) inside the isolated `workspace/` directory.
*   **Rule:** The agent must immediately `cd` into the new isolated workspace folder before touching any code.

### Step 3: Atomic Release (`aim push`)
Once the code has been written, validated via automated tests, and confirmed working, the agent must deploy it atomically.
*   **Command:** `aim push "Prefix: <Description> (Closes #ID)"`
*   **Action:** The CLI parses the Semantic Prefix (e.g., `Fix:`, `Feature:`, `Docs:`), automatically bumps the `VERSION` file, triggers the `sovereign_sync.py` backup process, commits the code, and pushes the branch to GitHub.
*   **Rule:** The commit message *must* contain a valid Semantic Prefix and explicitly state `(Closes #ID)` so GitHub automatically closes the corresponding ticket.

## 3. The Batch Merge (`aim merge-batch`)
If multiple independent agents are working in parallel across different `workspace/` directories, the Operator or the Prime Agent can execute `aim merge-batch`. This command automatically evaluates all open `fix/*` branches, resolves non-conflicting merges into `main`, and safely deletes the isolated worktrees to maintain repository hygiene.
