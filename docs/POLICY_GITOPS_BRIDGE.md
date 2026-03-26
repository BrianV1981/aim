# Key Feature: The GitOps Bridge

**The Problem:** Autonomous AI agents are notoriously sloppy with version control. They create massive "kitchen sink" commits, bypass issue trackers, and force-push broken code, making it impossible to revert specific regressions.

**The Solution:** The GitOps Bridge. A natively integrated, absolute constraint layer that forces the AI into a strict Issue-Driven Development (IDD) and Semantic Release pipeline.

---

## 1. The Core Philosophy (Atomic Deployments)
A.I.M. enforces a **Continuous Release** methodology. AI agents are strictly forbidden from executing raw `git commit` or `git push` commands. 

If an agent wants to change code, it must follow the 3-step DevOps lifecycle.

## 2. The 3-Step Lifecycle

### Step 1: The Reporter (`aim bug`)
*   **Action:** `aim bug "Description of the problem"`
*   **Mechanism:** A.I.M. reads the `FALLBACK_TAIL.md` (the last 10 turns of raw JSON crash data), wraps it in a collapsible markdown block, and uses the `gh` CLI to instantly create a highly structured bug ticket on the remote GitHub repository.

### Step 2: The Isolation (`aim fix`)
*   **Action:** `aim fix <issue_id>`
*   **Mechanism:** Instantly executes `git checkout -b fix/issue-<id>`. This physically prevents the agent from contaminating the `main` branch while iterating through test-driven development (TDD) failures.

### Step 3: The Semantic Release (`aim push`)
*   **Action:** `aim push "Fix: Patched the auth logic (Closes #4)"`
*   **Mechanism:** This is the crown jewel of the GitOps Bridge. 
    1.  It reads the `Fix:` prefix.
    2.  It reads the `VERSION` file and mathematically calculates a SemVer patch bump (e.g., `v1.2.0` ➔ `v1.2.1`).
    3.  It automatically formats and prepends the new release to the `CHANGELOG.md`.
    4.  It stages, commits, and pushes the code to the isolated branch.

## 3. The Phase Protocol (`aim promote`)
When the feature is complete and the tests are green, the `aim promote` command automates the entire Senior DevOps merge lifecycle:
1. Checks out `main`.
2. Creates an immutable archive branch of the *current* state of main (e.g., `archive-phase-24-20260323`).
3. Merges the dev branch into `main`.
4. Pushes the new baseline to GitHub.
5. Deletes the local dev branch to keep the workspace perfectly clean.

## The Result
Your repository maintains a pristine, granular, automated public ledger. Every single line of code is tied to an issue, and every regression can be instantly reverted without untangling a mega-commit.