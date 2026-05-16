# Rate Limits and Performance

## 429 Rate Limit (Too Many Requests)
API rate limits (Requests Per Minute - RPM and Tokens Per Minute - TPM) are independent of the context window usage percentage. 

### Epistemic Certainty on 429s
- **RPM vs. Capacity:** Confirmed that "Thinking" hangs are typically triggered by **Request-Per-Minute (RPM)** rate limits rather than context window capacity or total token usage. For example, hangs have been observed even at **3% context usage**.
- **Throttle Recovery:** Hitting these limits requires a session reset via the `/reincarnate` command. This is the **mandatory protocol** for clearing "Thinking" lags and resetting the API's RPM window when context usage or tool frequency triggers throttling.

### Symptoms
- **Catastrophic "Thinking" Hang:** When a `429` error is received from the `cloudcode-pa` endpoint, the Gemini CLI may enter an unresponsive state for up to 60 minutes.
- **Silent Failures:** The CLI fails to notify the user of the rate limit, continuing to show a "Thinking" indicator without making progress (Issue #25736).

### Mitigation
- **Forced Transparency:** Set all model chain actions (`terminal`, `transient`, `not_found`, `unknown`) to `"prompt"` in `~/.gemini/settings.json`. This forces the CLI to stop and ask for user intervention when an error occurs.
- **Model Hard-Lock:** Use strict model chains (e.g., `gemini-3.1-pro-preview`) to prevent the CLI from attempting to fallback to lower-tier models during throttling events, which can exacerbate the hang.

## Daily Token Quotas & Discrepancies
- **Flash Model Throttling:** The Flash tier is strictly throttled at a daily ceiling of approximately **178.7 million tokens**.
- **Pro Model Allocation:** The Pro tier enjoys a significantly larger daily limit of approximately **556.8 million tokens**.
- **Impact:** This disproportionate throttling means high-volume tasks (like benchmark ingestions) will unexpectedly exhaust Flash quotas long before Pro limits are reached.

## Performance Optimization
- **Pulse Protocol:** Regularly use `python3 scripts/aim_cli.py pulse` to anchor state. This allows for safe reincarnation without losing track of current workstreams.
- **Direct Execution:** Avoid shell aliases; use direct script paths (e.g., `python3 scripts/aim_cli.py`) to ensure command availability within isolated subshells and worktrees.
- **API Pacing & Timeouts (Benchmarking):** For heavy latency models, runners must strictly enforce pacing. The V6 architecture mandates a 60-second pacing delay between successful questions, a 300-second thinking timeout, and injects an `Escape` key alongside a 180-second cooldown sleep upon encountering a `TIMEOUT_ERROR` to prevent rate-limiting cascades.
- **V5 Benchmark Architecture:** Implements an automated 50-question bundler with intelligent pause-for-cooldown logic to mitigate `429 Too Many Requests` API latency errors and context window bloat during high-volume evaluations.
- **Ollama Safe-Generation Protocol:** When generating multimodal datasets with local Ollama models, scripts must enforce strict serialization (one model at a time), explicit VRAM management (sending `keep_alive: 0` to force model unloading), and incremental JSON checkpointing to prevent VRAM thrashing and systemic hangs.
