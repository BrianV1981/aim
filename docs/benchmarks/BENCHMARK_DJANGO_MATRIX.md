# Benchmark: The Matrix vs. Base Weights (Django SWE-bench)

## Overview
This benchmark is designed to empirically test the "Exoskeleton Hypothesis": *Can scaffolding quality (mandated workflows, RAG knowledge cartridges, and strict guardrails) substitute for raw model capability?* 

By testing the exact same underlying LLM (Gemini 3.1 Pro Preview) against a complex, real-world software engineering task, we aim to isolate the value of the A.I.M. framework. If the A.I.M.-wrapped model outperforms the raw model, it proves that treating an LLM like a rigidly scoped state machine (a "bot") yields superior code quality compared to treating it like a generalized oracle.

## The Target
We will utilize a verified issue from the official **SWE-bench** dataset targeting the `django/django` repository.
*   **The Codebase:** Django at the exact commit hash prior to the human-authored patch.
*   **The Prompt:** The raw, unedited text of the original GitHub issue.

## Group A: The Control (Raw Gemini CLI)
This represents the standard "Vibe Coding" approach used by the majority of developers today.
*   **Model:** `gemini-3.1-pro-preview`
*   **Environment:** Standard terminal execution inside the cloned repository.
*   **Knowledge Base:** Reliant entirely on the model's pre-trained base weights and generic repository scanning tools (e.g., standard `@repo` or `grep` commands).
*   **Prompt:** *"Fix this issue: [Insert GitHub Issue Text]"*

## Group B: The Experimental (A.I.M. Matrix Agent)
This represents the "MMO Botter" approach: a highly constrained, heavily armed specialist agent.
*   **Model:** `gemini-3.1-pro-preview` (Routed via the A.I.M. Frontal Lobe).
*   **Environment:** The A.I.M. Sovereign Cockpit (`django_test_matrix` instance).
*   **Knowledge Base:** The "Python Specialist Matrix" injected via DataJack `.engram` cartridges (`python314.engram`, `django.engram`, `pytest.engram`, `flake8.engram`, `bandit.engram`).
*   **The Mandate:** The `specialty-agents/django-expert.md` system prompt is locked in, strictly forbidding blind execution.
*   **Required Workflow:**
    1.  **Research:** Must `aim search` the Django `.engram` for architectural syntax before writing.
    2.  **Reproduce:** Must write a standalone `pytest` script that empirically fails due to the bug (Red).
    3.  **Patch:** Modify the codebase.
    4.  **Verify:** Execute the test until it passes (Green).
    5.  **Secure:** Run `flake8` and `bandit` on the modified files before committing.

## Key Metrics
1.  **Resolution Success:** Does the generated patch resolve the issue without breaking the broader Django test suite? (Pass/Fail)
2.  **Context Efficiency (Cost):** Total input and output tokens consumed. Does A.I.M.'s localized `aim search` cost less than the Control group's brute-force repository scanning?
3.  **Time to Resolution:** Total duration of the autonomous loop.
4.  **Hallucination Rate:** Instances of deprecated API usage or hallucinated file paths.

---
*Results will be appended to this document upon completion of the test runs.*