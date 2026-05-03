# GitOps Discipline

The branch strategy, commit rules, and worktree hygiene for aim-opencode.

## Branch Strategy

```
upstream/main ──→ origin/main ──→ origin/opencode
     (clean mirror)    (fork deltas)
```

- **`main`**: Never modified directly. Only receives merges from `upstream/main`. Acts as a clean upstream mirror.
- **`opencode`**: The active development branch. All features, fixes, and documentation live here.
- **`fix/issue-<id>`**: Isolated worktree branches created by `aim fix <id>`. Merged into `opencode` when complete.

## Commit Rules

1. **Surgical staging only** — `git add <specific-files>`, NEVER `git add .`
2. **No blind commits** — `git commit -a` is forbidden
3. **Pre-commit hooks** run via `./pre-commit.sh` (if configured)
4. **Push after each completed unit of work**, not in bulk at session end
5. **Never push to `main`** — the validator enforces this

## Commit Message Format

```
<type>: <description> (Closes #<id>)

<optional body with details>
```

Types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`

## Worktree Hygiene

A.I.M. creates isolated Git worktrees at `workspace/issue-<id>` for each ticket via `aim fix <id>`.

- `workspace/` is listed in `.opencodeignore` to prevent recursive scanning across hundreds of duplicate files
- Clean up worktrees after issues are resolved:

```bash
# Remove a specific worktree
git worktree remove workspace/issue-531

# List all active worktrees
git worktree list

# Bulk cleanup
git worktree prune
```

## Workflow by Command

| Command | What it does |
|---|---|
| `aim bug "title" --context ... --failure ... --intent ...` | Creates a GitHub issue on `BrianV1981/aim` with full context |
| `aim fix <id>` | Creates isolated worktree, branches from `opencode` |
| `aim push "feat: description"` | Versions, commits, and pushes current branch to `origin` |
| `aim update fork --dry-run` | Previews upstream sync without changing anything |
| `aim update fork` | Executes full sync pipeline and runs tests |

## Safety Guards

- `aim push` validates that you're NOT on `main` before pushing
- `aim update fork` runs the full test suite after merge, blocking deploy on failures
- `aim fix` creates an isolated worktree, preventing cross-contamination
- Never run `git push --force` to `main` under any circumstances

## Pre-Push Checklist

Before `aim push`:

1. `git branch --show-current` — must NOT output `main`
2. `pytest tests/ -x -q` — all tests pass
3. `git status` — only intended files staged (surgical staging)
4. `git diff --cached` — review what's being committed
