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

---
*Last Updated: 2026-04-22*
