# Benchmark Diagnostics Report: Session `873ce174` (Gemini CLI) vs. DeepSeek Baseline

**Date:** 2026-05-17
**Target Session JSONL (Gemini CLI):** `session-2026-05-14T03-28-873ce174.jsonl`
**Baseline Session JSON (DeepSeek):** `SESSION_0_100Q_RAW_20260517_151157.json`
**Subject:** API RPM Throttling vs. Gemini CLI "Thinking" Hangs

## 1. Executive Summary
This report analyzes a disastrous 10.7-hour execution of the LoCoMo-v2 benchmark by the Gemini CLI. The data empirically proves that the Gemini CLI suffers from a critical failure in handling API Rate Limit (`429 Too Many Requests`) errors. When throttled by upstream RPM (Requests Per Minute) limits, the CLI does not cancel the request or fail-fast; instead, it enters an infinite "Thinking" loop in the background.

The only reason the Gemini session completed (and generated the `ℹ Request cancelled` logs) is because an external **Ghost Benchmark Orchestrator Python Script** actively monitored the CLI and forcefully intervened to prevent permanent hangs.

When the exact same 100-question benchmark payload was run through the orchestrator using a DeepSeek model, the "Nightmare Loop" of timeouts and cooldowns was entirely absent, proving the fault lies exclusively within the Gemini CLI's request/retry logic.

## 2. Session Overview: Gemini CLI (The "Nightmare" Run)
*   **Total Chronological Duration:** 10.70 hours
*   **Context Usage:** Peaked at 19% (Confirming this was *not* a context window exhaustion issue).
*   **Turns Processed:** 1,695

## 3. The Orchestrator Mechanics (The "Nightmare" Loop)
The Gemini CLI developer must understand that the delays logged in the TUI were not native CLI timeouts. They were external overrides injected by the benchmark runner to keep the system alive under severe API throttling. 

The benchmark script enforces the following rigid pacing and fail-safe logic:
1.  **1-Minute Pacing:** A mandatory 60-second delay between every asked question to respect base API pacing.
2.  **5-Minute Hang Override (Escape Injection):** If an agent is asked a question and sits in a "Thinking" state for 5 minutes without returning an answer, the orchestrator script forcefully hits the `Escape` key. This terminates the hung request, generating the `ℹ Request cancelled` message in the TUI.
3.  **3-Minute Error Cooldown:** If an explicit background error is detected, the orchestrator script enforces a 180-second sleep before attempting the next operation to allow upstream quotas to clear.

## 4. Empirical Data Breakdown: Gemini vs. DeepSeek
An analysis of the raw JSON logs for both models under the exact same Ghost Orchestrator script reveals a staggering disparity:

### A. Gemini CLI Execution (`session-2026-05-14T03-28-873ce174.jsonl`)
*   **Count of 5-Minute Hangs Forcefully Cancelled:** 31 occurrences
    *   *The Orchestrator had to hit `Escape` 31 times because the Gemini CLI hung silently for 5 minutes on a 429 error.*
*   **Count of 3-Minute Error Cooldowns:** 60 occurrences
    *   *The Orchestrator detected explicit background errors from the Gemini CLI and forced a 3-minute sleep 60 times.*

### B. DeepSeek Baseline Execution (`SESSION_0_100Q_RAW_20260517_151157.json`)
*   **Actual Benchmark Duration (100 Questions):** 3.13 hours (187.6 minutes)
*   **Count of 5-Minute Hangs Forcefully Cancelled:** 0 occurrences
*   **Count of 3-Minute Error Cooldowns:** 0 occurrences
    *   *The DeepSeek model processed the entire 100-question benchmark cleanly in 3.13 hours without triggering a single fail-safe override from the orchestrator. The benchmark concluded exactly when the 100th question was successfully completed with the output: `[ANSWER] Sarah recommended "Becoming Nicole" by Amy Ellis Nutt.`*
    *   *(Note: The total raw session file spans 11.79 hours only because the Operator reopened the session hours later to ask manual follow-up questions. The core benchmark itself completed smoothly in 3.13 hours).*

## 5. Structural Bloat Analysis (63MB vs 4MB)
A secondary anomaly is the massive physical file size of the Gemini session (63MB) compared to the DeepSeek baseline (4.4MB). A script analysis of the `.jsonl` structure reveals that the bloat is directly tied to the "Nightmare Loop" exacerbating the CLI's internal serialization overhead.

*   **Expected Behavior:** A standard `aim search` with `k=10` yields a maximum of 15k to 45k characters of raw context.
*   **The Serialization Penalty:** When the Gemini CLI logs this search result to the `.jsonl` file, the 20k string is heavily escaped (turning every `"` into `\"` and every newline into `\n`). Furthermore, the CLI duplicates this massive string across multiple fields within the same JSON object (e.g., storing it once in `result` and again in `resultDisplay`). This causes a single 20k search return to consume over 90,000 characters on disk.
*   **The Compounding Loop:** During the 10.7-hour rate-limit coma, the orchestrator forcefully cancelled the hung CLI and repeatedly retried the same queries. Each retry successfully ran the massive search and appended another 90,000-character JSON payload to the file before hitting the 429 error during the reasoning phase.
*   **Conclusion:** The 63MB file is a "fossil record" containing 932 separate turns that are over 10,000 characters long. The file bloat is not due to a runaway search function, but rather the CLI repeatedly saving heavily serialized, duplicated tool-call payloads while failing to exit the rate-limit loop.

## 6. Conclusion & Actionable Feedback for CLI Developers
The 10.7-hour run was not caused by user error or context bloat (which remained at a mere 19%). It was caused by the upstream API severely restricting RPM limits, combined with the Gemini CLI's inability to fail-fast.

**The CLI must be updated to explicitly catch API throttling/429 errors and halt execution or notify the user.** 

Currently, it silently drops the connection and cycles "Thinking" for hours. Without the Ghost Benchmark Orchestrator script manually injecting 5-minute timeouts and `Escape` keypresses, a single rate-limited question would permanently lock the entire system. The flawless execution of the DeepSeek baseline proves that proper error surfacing entirely eliminates these catastrophic hangs.