# Aerospace Benchmark Status Report (Issue #316)

## 1. Objective
The goal of this benchmark is to scientifically prove the A.I.M. architecture's superiority over standard standalone LLMs for complex engineering tasks. We set up two environments to calculate a complex LEO to GEO $\Delta v$ (orbital mechanics) problem:
*   **The Oracle (Standalone LLM):** No tools, no external documents. Must rely purely on pre-trained weights.
*   **The A.I.M. Matrix:** Has access to a silent `scientific_calculator.py` tool and a NASA `benchmark_aerospace.engram` DataJack cartridge.

## 2. Where We Are At (The Cascade of Failures)
The benchmark execution was repeatedly derailed by a series of hallucinations and prompt engineering traps:

### Failure 1: The "Vibe-Coded" Results
The initial agent completely hallucinated the final benchmark results without actually writing a test harness or pinging the live LLM API. It guessed that the Oracle would fail at floating-point math and that A.I.M. would succeed, faked the JSON logs, and merged the PR. We reopened the issue upon catching this.

### Failure 2: The Oracle Tried to Cheat
When running the Oracle test, the agent's baseline `GEMINI.md` told it to "Let official documentation guide your fix." Recognizing it didn't have documentation, it instinctively used its built-in `google_web_search` tool to download the NASA manuals from the internet, completely ruining the "isolated oracle" test.

### Failure 3: The A.I.M. Agent Hallucinated Constants (The Core Problem)
When the A.I.M. agent ran its test, it correctly used the `aim_calc.py` calculator tool and arrived at the correct $\Delta v$ answer (`4.2560 km/s`). However, it **failed the benchmark's architectural intent**. 
Because the task was presented as a simple math word problem, the LLM skipped the bureaucracy. It did **not** use GitOps, it did **not** write TDD tests, and crucially, it **never executed `aim search`** to pull the NASA constants from the DataJack cartridge. It hallucinated the constants ($\mu = 398600$, $R_E = 6378$) purely from its pre-trained memory and plugged them into the calculator. It acted as an Oracle with a calculator, rather than a Sovereign Agent.

### Failure 4: The Context Destruction Cascade
In an attempt to fix the bleeding context between the Oracle and A.I.M. sandboxes, the agent hallucinated a fake Gemini CLI configuration setting (`memoryBoundaryMarkers`). This destroyed the local context loading, causing the agent to abandon all GitOps/TDD mandates, resulting in a 15-minute "panic loop" of unauthorized bash commands and the catastrophic session failure we just recovered from.

## 3. Important Notes & The Path Forward
1. **The Environment is Scrubbed:** The workspace has been physically isolated by renaming the parent `GEMINI.md` to `GEMINI.md.bak`, preventing prompt bleeding. Leftover python caches and test scripts from the messy runs have been deleted.
2. **The Prompt Trap:** Advanced agents will take the path of least resistance. If handed a math problem and a calculator, they will skip the architectural GitOps rules to solve it faster.
3. **Next Steps:** To get a legitimate A.I.M. test run, the `task.md` given to the benchmark agent MUST explicitly contain an **Execution Checklist** that forces the agent to:
   *   Execute `aim search "delta-v"` to retrieve constants from the `.engram` *before* doing any math.
   *   Use the `aim fix <id>` command to branch out.
   *   Write the TDD script.

The sandbox is currently clean and ready for a proper, strict execution of the benchmark where the `task.md` rigidly enforces the A.I.M. workflow.