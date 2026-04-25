# Configuration and Variables

## Model Hard-Locking Pattern
To ensure intelligence consistency and prevent silent autonomous fallbacks to lower-performing models (e.g., Flash) which can cause 45-second native CLI timeouts:
- **Dynamic Configuration:** Set `experimental.dynamicModelConfiguration: true` in `~/.gemini/settings.json`.
- **Strict Model Chains:** Redefine `modelConfigs.modelChains` to bind exclusively to `gemini-3.1-pro-preview`. This forces deterministic model selection and prevents silent "Thinking" hangs.

## Forced Transparency Pattern
To ensure the agent requests intervention when stuck and prevents silent model downgrades:
- **Action Handlers:** Configured action handlers (`terminal`, `transient`, `not_found`, `unknown`) to `"prompt"` within the model chain.
- **Operator Intervention:** This forces the CLI to halt and wait for user directives during failures or ambiguous states rather than autonomously attempting recovery with suboptimal models.

## Background Daemons & Cognitive Routing
- **Internal Reasoning Bypasses:** The environment variable `AIM_INTERNAL_REASONING=1` must be respected to instantly bypass recursive triggers when spawning fully detached background processes (e.g. `session_summarizer.py` hooks).
- **OAuth Keychain Access:** Do not set the `GEMINI_CLI_CONFIG_DIR` parameter in internal reasoning utilities; omitting it restores the ability for headless background tasks to correctly load the global OAuth keychain.
- **Primary Brain Fallback:** The "Primary Brain" setting is exclusively a fallback engine for *headless background scripts* (like `aim audit`). Interactive sessions must be governed solely by global Gemini CLI configurations.

---
*Last Updated: 2026-04-25*
