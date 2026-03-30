# Forensic Audit: Case Study in Systemic API Latency (Issue #203)

**Subject:** Google Gemini Ultra API Performance (March 26–31, 2026)
**Target:** 149MB Session Log (`session-2026-03-28T14-17-f2926552.json`)

## 1. The Compute Wall (Latency)
The audit confirms that the "Ultra" plan buckles well below its advertised context window.
* **The 5-Minute Wall:** Latency first crossed **304 seconds** at Turn 34 with only **139,105 tokens** in context.
* **Throughput Decay:** Average Tokens-per-Second (TPS) dropped from **3.70** (First 10 turns) to **1.21** (Last 10 turns).
* **The Result:** The system is physically incapable of maintaining Senior Engineering reasoning at scale without aggressive session resets.

## 2. Instruction Fade (Cognitive Drift)
Structural compliance fails significantly earlier than technical logic.
* **Turn 6:** The model began ignoring the "Explain Before Acting" and "Use specialized tools" mandates.
* **Turn 16:** The model reverted to generic bash commands (`cat | tail`) instead of using provided A.I.M. tools (`read_file`).
* **Conclusion:** Context saturation "drowns out" the System Prompt, causing the agent to revert to generic LLM behavior.

## 3. The Forensic Receipt
| Turn # | Total Tokens | Latency (s) | Instruction Ignored |
| :--- | :--- | :--- | :--- |
| 6 | 34,090 | 3.7 | Use grep_search |
| 7 | 34,147 | 20.5 | Use list_directory |
| 10 | 49,152 | 44.2 | Use list_directory |
| 16 | 64,573 | 91.1 | Use read_file |
| 22 | 65,657 | 153.7 | Use read_file |
| 34 | 139,105 | 304.5 | **CRITICAL LAG** / Use read_file |

---
**Status:** Audit Verified. receipts ready for disclosure.
