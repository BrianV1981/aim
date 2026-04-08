# SWE-Bench Target (Proxy)
**Title:** URLValidator rejects valid IPv6 addresses when they contain mixed-case hex digits.
**Objective:**
1. Locate the URLValidator in the django_repo codebase.
2. Fix the regex pattern to correctly support mixed-case IPv6 literals (A-F).
3. Prove your fix works using your mandated TDD workflow.
