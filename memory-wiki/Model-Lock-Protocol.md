# Model-Lock Protocol

## Overview
The Model-Lock Protocol is a defensive configuration strategy designed to prevent the Gemini CLI from silently downgrading to high-RPM/low-intelligence models (like Gemini Flash) when the primary high-tier model (Gemini Pro/Ultra) hits rate limits or is otherwise unavailable.

## Configuration Steps
To enforce this protocol, modify `~/.gemini/settings.json`:

1.  **Enable Dynamic Model Configuration:**
    ```json
    "experimental": {
        "dynamicModelConfiguration": true
    }
    ```

2.  **Restrict Model Chains:**
    Explicitly define the `modelChains` for `preview` and `pro` aliases to include ONLY the desired high-tier model. This prevents the CLI's default fallback logic from engaging.
    ```json
    "modelConfigs": {
        "modelChains": {
            "preview": ["gemini-3.1-pro-preview"],
            "pro": ["gemini-3.1-pro-preview"]
        }
    }
    ```
    *Note: By restricting chains to `gemini-3.1-pro-preview`, we establish a "No-Fallback" pattern that prevents silent downgrades to Flash models.*

## Impact
- **Intelligence Guarantee:** Ensures that the agent always operates with the required reasoning capabilities for complex engineering tasks.
- **Loop Prevention:** By disabling fallback to models with higher RPM limits, it forces the system to confront `429` errors directly rather than entering a degraded performance state that can lead to "Thinking" hangs.

---
*Last Updated: 2026-04-22*
