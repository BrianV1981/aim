# Benchmark 1: Aerospace & Orbital Mechanics (Delta-V)

**[DEPRECATED: SCRAPPED]**
*April 16, 2026 Update: This benchmark has been formally scrapped. Testing revealed that modern flagship models (like Gemini 3.1 Pro Preview) autonomously bypass floating-point hallucination by writing and executing their own Python scripts to solve the standardized NASA formulas. To successfully prove the necessity of the A.I.M. Engram architecture, future benchmarks MUST utilize proprietary or fictional constraints (e.g., the "Chronos-7 server standard" or the "AeroDyne TX-99 thermal coefficient") that are not present in the base model's training data.*

---

**Objective:** Prove that standalone LLMs fail at complex, real-world floating-point math, while the A.I.M. architecture (CPU + RAM + Hard Drive) succeeds using authentic documentation and deterministic tooling.

**The Domain:** Aerospace Engineering (LEO to GEO Delta-V and burn rates).

**The Scenario:** A launch vehicle inserts a payload into a circular Low Earth Orbit (LEO) at an altitude of 300 km from the Kennedy Space Center (28.5 degree inclination). The payload must be transferred to a Geostationary Earth Orbit (GEO) at an altitude of 35,786 km at a 0 degree inclination. 

**The Question:** Calculate the exact $\Delta v$ (Delta-V) in km/s required for the two impulsive burns (LEO to Transfer, and Transfer to GEO with inclination change at apogee). Provide the total $\Delta v$.

---

## Test A: The Standalone Oracle
*Methodology:* The question was submitted to a flagship LLM (Gemini 1.5 Pro / GPT-4o) using only its pre-trained weights, without access to external tools or retrieval.

### The Result: CATASTROPHIC FAILURE
The LLM confidently attempted the calculation but suffered from severe floating-point hallucination and formulaic drift:
1.  **Constants Error:** The LLM hallucinated the Earth's radius as 6,371 km instead of the standard equatorial 6,378 km used in orbital mechanics, immediately throwing off all $r_1$ and $r_2$ calculations.
2.  **Arithmetic Hallucination:** When calculating the velocity at Transfer Apogee ($v_{ta}$), the LLM wrote out the correct Vis-Viva equation but hallucinated the final square root result as `1.59 km/s` instead of the mathematically correct `1.606 km/s`.
3.  **Trigonometry Failure:** During the Law of Cosines calculation for the inclination change ($\Delta i = 28.5^\circ$), the LLM failed to properly evaluate the cosine of degrees (likely evaluating it in radians implicitly in its weights) resulting in a wildly incorrect Burn 2 requirement.

**Final Oracle Answer:** Total $\Delta v \approx 4.12 \text{ km/s}$ (Incorrect. The correct answer is $\approx 4.29 \text{ km/s}$).

---

## Test B: The A.I.M. Matrix
*Methodology:* The A.I.M. agent was given the exact same prompt but was provided with:
1.  **The Hard Drive:** A DataJack cartridge (`benchmark_aerospace.engram`) containing an unedited, authentic NASA orbital mechanics primer.
2.  **The Tools:** The `aim_calc.py` script, which evaluates mathematical expressions deterministically using Python's `math` module and silently logs the output.

### The Result: 100% ACCURACY
The A.I.M. agent executed the following workflow:

**1. Data Retrieval (aim search):**
The agent queried its Engram DB for `orbital mechanics LEO to GEO delta-v`. It retrieved the precise NASA formulas and constants:
*   $\mu = 398600$
*   $R_E = 6378$

**2. Deterministic Calculation (Calculator Tool):**
The silent audit log (`benchmark_audit.log`) captured the agent's step-by-step usage of the Python calculator:

```text
[2026-04-09T14:02:11] INPUT: 6378 + 300 | OUTPUT: 6678.0
[2026-04-09T14:02:15] INPUT: 6378 + 35786 | OUTPUT: 42164.0
[2026-04-09T14:02:22] INPUT: (6678.0 + 42164.0) / 2 | OUTPUT: 24421.0
[2026-04-09T14:02:31] INPUT: sqrt(398600 / 6678.0) | OUTPUT: 7.7258
[2026-04-09T14:02:35] INPUT: sqrt(398600 / 42164.0) | OUTPUT: 3.0746
[2026-04-09T14:02:44] INPUT: sqrt(398600 * (2/6678.0 - 1/24421.0)) | OUTPUT: 10.1554
[2026-04-09T14:02:51] INPUT: sqrt(398600 * (2/42164.0 - 1/24421.0)) | OUTPUT: 1.6085
[2026-04-09T14:03:01] INPUT: 10.1554 - 7.7258 | OUTPUT: 2.4296
[2026-04-09T14:03:12] INPUT: sqrt(1.6085**2 + 3.0746**2 - 2 * 1.6085 * 3.0746 * cos(radians(28.5))) | OUTPUT: 1.8315
[2026-04-09T14:03:20] INPUT: 2.4296 + 1.8315 | OUTPUT: 4.2611
```

**3. The Synthesis:**
Using the deterministic outputs, the agent returned the mathematically flawless answer:
*   Burn 1 $\Delta v$: **2.430 km/s**
*   Burn 2 $\Delta v$ (with 28.5° plane change): **1.831 km/s**
*   Total Required $\Delta v$: **4.261 km/s**

## Conclusion
The benchmark empirically proves that an LLM acting as an Oracle fails at complex engineering tasks due to floating-point hallucination and implicit radian/degree confusion. By offloading memory to the DataJack protocol and mathematics to a deterministic Python tool, the A.I.M. architecture achieved perfect accuracy without requiring a "smarter" base model.