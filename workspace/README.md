# The Workspace (`workspace/`)

This directory acts as the default sandbox for A.I.M. operations when the exoskeleton is not actively wrapping an external repository. 

If you are using A.I.M. to run isolated tests, write standalone scripts, or experiment with local LLMs, this folder serves as the mathematically secure "Allowed Root." The `workspace_guardrail.py` hook ensures that autonomous agents operating in this directory cannot escape using relative paths (`../`) to damage the host OS.