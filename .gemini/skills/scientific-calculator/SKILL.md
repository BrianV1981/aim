---
name: scientific-calculator
description: Expert in scientific computation. Use for complex floating-point math, orbital mechanics, and physics equations to avoid hallucination.
---
# Scientific Calculator Instructions
You are strictly forbidden from calculating complex math using your internal weights. 
When you need to solve an equation, you MUST execute the following script via the shell:
`python scripts/benchmarks/tools/scientific_calculator.py "<expression>"`

**Example:**
`python scripts/benchmarks/tools/scientific_calculator.py "sqrt(398600 / 6678.0)"`