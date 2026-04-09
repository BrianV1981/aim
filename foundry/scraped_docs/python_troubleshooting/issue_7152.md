# Q: builtin_str(method) incorrectly converts binary method names
**Source:** https://github.com/psf/requests/issues/7152

## The Problem / Request
<open-swe-issue-content><github-issue>
method = builtin_str(method) problem

In requests/models.py, line 441, there is this code:

```python
method = builtin_str(method)
```

This causes problems when using binary method names like `b'GET'` - it converts them to the string `"b'GET'"` instead of `"GET"`.

The fix should decode bytes to string properly instead of using builtin_str.
</github-issue>

<repository>
psf/requests
</repository>

<base-commit>
a0df2cbb10419037d11d04352b3175405ab52941
</base-commit>

Please analyze this issue and provide a fix. The fix should be minimal and focused on resolving the described problem.</open-swe-issue-content>
<details>
<summary>Agent Context</summary>
<open-swe-do-not-edit-task-plan>
{
  "tasks": [
    {
      "id": "aed66fc5-954e-483e-909b-1dd5458581f9",
      "taskIndex": 0,
      "request": "[original issue]\n**builtin_str(method) incorrectly converts binary method names**\n<github-issue>\nmethod = builtin_str(method) problem\n\nIn requests/models.py, line 441, there is this code:\n\n```python\nmethod = builtin_str(method)\n```\n\nThis causes problems when using binary method names like `b'GET'` - it converts them to the string `\"b'GET'\"` instead of `\"GET\"`.\n\nThe fix should decode bytes to string properly instead of using builtin_str.\n</github-issue>\n\n<repository>\npsf/requests\n</repository>\n\n<base-commit>\na0df2cbb10419037d11d04352b3175405ab52941\n</base-commit>\n\nPlease analyze this issue and provide a fix. The fix should be minimal and focused on resolving the described problem.",
      "title": "Fix binary method name conversion in requests/models.py",
      "createdAt": 1768151023113,
      "completed": false,
      "planRevisions": [
        {
          "revisionIndex": 0,
          "plans": [
            {
              "index": 0,
              "plan": "**Modify the `prepare_method` function in `src/requests/models.py`** (lines 393-397) to properly handle binary method names. The current implementation uses `to_native_string(self.method.upper())` which should work correctly, but based on the issue description, the fix should ensure that when a bytes method name like `b'GET'` is passed, it is properly decoded to a string `'GET'` instead of being converted to its string representation `\"b'GET'\"`. The fix should:\n\n1. Check if `method` is bytes using `isinstance(method, bytes)`\n2. If bytes, decode it to a string using `.decode('utf-8')` or use the existing `to_native_string()` function from `src/requests/_internal_utils.py`\n3. Then call `.upper()` on the resulting string\n\nThe updated `prepare_method` function should look like:\n```python\ndef prepare_method(self, method):\n    \"\"\"Prepares the given HTTP method.\"\"\"\n    self.method = method\n    if self.method is not None:\n        self.method = to_native_string(self.method).upper()\n```\n\nThis ensures that bytes are decoded BEFORE calling `.upper()`, which is a cleaner approach. The `to_native_string()` function (defined in `src/requests/_internal_utils.py` at lines 25-35) properly decodes bytes to strings using the specified encoding (default: ascii).",
              "completed": false
            }
          ],
          "createdAt": 1768151023113,
          "createdBy": "agent"
        }
      ],
      "activeRevisionIndex": 0
    }
  ],
  "activeTaskIndex": 0
}
</open-swe-do-not-edit-task-plan>
</details>

## The Solution / Discussion
### Response 1
### 🤖 Plan Generated

I've generated a plan for this issue and will proceed to implement it since auto-accept is enabled.

**Plan: Fix binary method name conversion in requests/models.py**

- Task 1:
```
**Modify the `prepare_method` function in `src/requests/models.py`** (lines 393-397) to properly handle binary method names. The current implementation uses `to_native_string(self.method.upper())` which should work correctly, but based on the issue description, the fix should ensure that when a bytes method name like `b'GET'` is passed, it is properly decoded to a string `'GET'` instead of being converted to its string representation `"b'GET'"`. The fix should:

1. Check if `method` is bytes using `isinstance(method, bytes)`
2. If bytes, decode it to a string using `.decode('utf-8')` or use the existing `to_native_string()` function from `src/requests/_internal_utils.py`
3. Then call `.upper()` on the resulting string

The updated `prepare_method` function should look like:
\```python
def prepare_method(self, method):
    """Prepares the given HTTP method."""
    self.method = method
    if self.method is not None:
        self.method = to_native_string(self.method).upper()
```

This ensures that bytes are decoded BEFORE calling `.upper()`, which is a cleaner approach. The `to_native_string()` function (defined in `src/requests/_internal_utils.py` at lines 25-35) properly decodes bytes to strings using the specified encoding (default: ascii).
```

Proceeding to implementation...

### Response 2
Hi @surenraju, it's not clear what problem you're encountering from what you've provided. The line you're referencing does not exist in Requests current codebase. The PR you've provided also doesn't make sense.

It's clear this is being done by a confused AI agent. Please avoid filing spam issues and PRs in the future.

