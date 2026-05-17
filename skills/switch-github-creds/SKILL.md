<activated_skill>
<instructions>
# Skill: switch-github-creds

This skill explains how to switch the active GitHub credentials used by the `gh` CLI tool when you encounter 403 Forbidden errors or permission issues during `git push` or other GitHub API operations.

## Context
When multiple GitHub accounts are logged in via the GitHub CLI, `git` commands (if configured to use the `gh` credential helper) and `gh` API commands will default to the active account. If you attempt to push to a repository that your active account does not have write access to, you will receive a 403 Forbidden error.

## Workflow

1. **Check Current Status:**
   Run `gh auth status` to see all logged-in accounts and identify which one is currently active.
   
2. **Identify the Correct Account:**
   Determine the username of the account that has permissions to the target repository (e.g., `BrianV1981`).

3. **Switch the Active Account:**
   Execute the following command to switch the active context to the correct user:
   ```bash
   gh auth switch -u <USERNAME>
   ```
   *Example: `gh auth switch -u BrianV1981`*

4. **Verify and Execute:**
   After switching, you will see a success message (`✓ Switched active account for github.com to <USERNAME>`). You can now safely execute your `git push origin main` or other GitHub operations.
</instructions>
</activated_skill>