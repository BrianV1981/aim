---
name: scientific-calculator
description: Expert in scientific computation. Use for complex floating-point math, orbital mechanics, and physics equations to avoid hallucination. Supports variable assignment and stateful memory.
---
# Scientific Calculator Instructions
You are strictly forbidden from calculating complex math using your internal weights. 
When you need to solve an equation, you MUST execute the following script via the shell.
The calculator outputs structured JSON and maintains a stateful memory of variables you assign.

**Execution Command:**
`python scripts/benchmarks/tools/aim_calc.py "<expression>"`

**Examples of Variable Assignment (Saves to Memory):**
`python scripts/benchmarks/tools/aim_calc.py "v_leo = sqrt(398600 / 6678.0)"`

**Examples of Referencing Memory:**
`python scripts/benchmarks/tools/aim_calc.py "v_geo - v_leo"`