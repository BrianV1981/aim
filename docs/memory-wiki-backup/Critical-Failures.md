# Critical Failures & Diagnostics

## API Rate Limiting (429) & "Thinking" Hangs
- **Issue:** Identified a major flaw in the agent's error-handling logic where API `429` (Rate Limit) errors trigger an extended "Thinking" state (unresponsive for up to 60 minutes) without fail-fast notifications.
- **Upstream Bug:** This is tracked in `google-gemini/gemini-cli` as [Issue #25736](https://github.com/google-gemini/gemini-cli/issues/25736).
- **SLA Violation:** Documented as a critical architectural failure for Ultra subscribers where the system fails to surface throttling events.
- **Root Cause:** The agent's internal retry-backoff logic fails to surface throttling events, creating a "black box" hang. Confirmed that these 429 errors are RPM-bound (Requests Per Minute) and can occur even at low context usage (e.g., 3%).
- **Mitigation:** Execute a full `aim pulse` and `/reincarnate` cycle to flush the context window and reset the API rate-limit counter.

## Model Downgrade Protection
- **Configuration:** `experimental.dynamicModelConfiguration` must be enabled in `~/.gemini/settings.json`.
- **Constraint:** Strictly limit `modelChains` to `gemini-3.1-pro-preview` to prevent silent autonomous fallbacks to Flash models during high-latency periods or rate-limiting events.

## CLI Timeout Exceptions
- **Issue:** Native CLI operations can fail with hard timeouts. For example, calls to `gemini -m gemini-3-flash-preview` were observed timing out after 45 seconds.
- **Impact:** Can cause silent failures in background tasks or agent sub-shells if not properly caught and logged.
- **Mitigation:** Ensure Model Hard-Lock is active to prevent fallback to potentially unstable flash endpoints. Implement robust timeout handling and fallback strategies for programmatic CLI invocations.
