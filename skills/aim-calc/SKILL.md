---
name: aim-calc
description: "A stateful scientific calculator. Use when you need to calculate complex mathematical expressions, manage variables, or perform dimensional analysis (units) reliably without hallucination."
---

# aim-calc: The Agent-Native Scientific Calculator

You are strictly forbidden from calculating complex math using your internal weights. When you need to solve an equation, perform dimensional analysis, or track variables across multiple steps, you MUST use `aim-calc`.

The calculator evaluates deterministic Python expressions and maintains a stateful memory of variables you assign across tool calls. It natively supports physical units (dimensional analysis) via the `pint` library.

**Execution Command:**
`python skills/aim-calc/scripts/aim_calc.py "<expression>"`

## Workflow & Examples

**1. Basic Math:**
`python skills/aim-calc/scripts/aim_calc.py "sqrt(398600 / 6678.0)"`
The output will be strict JSON.

**2. Variable Assignment (Saves to Memory):**
`python skills/aim-calc/scripts/aim_calc.py "v_leo = sqrt(398600 / 6678.0)"`
This stores `v_leo` in the persistent memory state (`.calc_state.json`) and silently logs to `.calc_audit.log`.

**3. Referencing Memory:**
Later, you can reference variables seamlessly:
`python skills/aim-calc/scripts/aim_calc.py "burn1 = v_tp - v_leo"`

**4. Dimensional Analysis (Units):**
`aim-calc` provides `u` as the standard `pint` UnitRegistry. You can define units natively:
`python skills/aim-calc/scripts/aim_calc.py "speed = 12 * u.meter / u.second"`
`python skills/aim-calc/scripts/aim_calc.py "distance = speed * (2 * u.minute)"`
`python skills/aim-calc/scripts/aim_calc.py "distance.to(u.km)"`

All executions return structured JSON containing success/error status, evaluated floats, and actionable error messages/Tracebacks if you make a syntax mistake.
