# 🐙 GitHub Workflow Patterns

Best practices for interacting with GitHub and the `gh` CLI from within an autonomous agent environment.

## Robust Issue Reporting
To avoid shell expansion errors (such as backticks in code blocks being interpreted by the shell) during command execution, use the following pattern:

1. **Write to Temporary File:** Write the full report body to a local temporary file (e.g., `/tmp/gemini_bug_report.md`).
2. **Execute via File:** Use the `gh` CLI to create the issue using the `--body-file` flag.

```bash
gh issue create --title "Issue Title" --body-file /tmp/gemini_bug_report.md
```

This ensures that the content of the report is passed exactly as intended without corruption from shell escaping rules.

## GitOps Repository Hygiene & Operations
- **Workspace Clean Sweep:** Systematically purged untracked `tmp_*.py`, `patch_*.py`, stray artifact files, and legacy sandboxes across `aim` and `locomo-v2` workspaces. Deprecated technical documentation (`AIM_SEARCH_SECRET_SAUCE.md`) and consolidated orphaned scripts.
- **Benchmark Artifacts:** Published benchmark scripts, ingestion pipelines, and the immutable JSON proof log (`A_I_M_LONGMEMEVAL_PROOF_LOG.json`) to the public `locomo-v2` repository.
- **Documentation Overhaul:** Purged legacy SQLite references from `README.md`. Generated a unified `docs/README.md` index summarizing 22 core architectural records using a custom Python parser. Relocated `QA_PAIRS.md` and upgrade trackers to `docs/` for operational clarity.

---
*Last Updated: 2026-04-22*
