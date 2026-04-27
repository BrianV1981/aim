# Native CLI Exceptions

## Overview
Native CLI exceptions are critical errors that occur when the underlying programmatic calls to the Gemini CLI fail unexpectedly, such as due to hard timeouts. These failures can manifest silently in background tasks or sub-shells if not properly monitored and caught.

## 45-Second Timeouts
A known pattern of native CLI exceptions occurs when the `gemini` command times out.
- **Trigger:** Calling models with lower stability or performance SLAs (e.g., `gemini-3-flash-preview`) can result in commands timing out after exactly 45 seconds.
- **Example:** `Command '['gemini', '-p', '', '-o', 'json', '-y', '-m', 'gemini-3-flash-preview']' timed out after 45 seconds`

## Impact & Mitigation
- **Impact:** The failure is often ungraceful, leaving background scripts or automated agent sessions in a stalled or failed state without clear feedback to the operator.
- **Mitigation:** It is imperative to enforce the **Model-Lock Protocol** (see [Model-Lock-Protocol](Model-Lock-Protocol.md)) and bind the configuration to high-tier models (like `gemini-3.1-pro-preview`) to avoid the unstable paths that lead to these timeouts. Additionally, developers must implement robust timeout and error handling for programmatic CLI invocations.

---
*Last Updated: 2026-04-25*
