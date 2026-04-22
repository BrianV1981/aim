#!/usr/bin/env python3
import sys
import math
import datetime
import os
import argparse
import ast
import operator
import json
import traceback

STATE_FILE = "/tmp/.calc_state.json"
AUDIT_FILE = "/tmp/benchmark_audit.log"

# Define a safe environment for evaluation
base_safe_names = {'__builtins__': None}
for name, val in vars(math).items():
    if not name.startswith('_'):
        base_safe_names[name] = val

# Add some basic operators
allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

def safe_eval(node, safe_names):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise TypeError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left, safe_names)
        right = safe_eval(node.right, safe_names)
        op = type(node.op)
        if op in allowed_operators:
            return allowed_operators[op](left, right)
        else:
            raise TypeError(f"Unsupported operator: {op}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand, safe_names)
        op = type(node.op)
        if op in allowed_operators:
            return allowed_operators[op](operand)
        else:
            raise TypeError(f"Unsupported unary operator: {op}")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in safe_names and callable(safe_names[func_name]):
                args = [safe_eval(arg, safe_names) for arg in node.args]
                return safe_names[func_name](*args)
            else:
                raise NameError(f"Unsupported function: '{func_name}'")
        else:
             raise TypeError(f"Unsupported function call type")
    elif isinstance(node, ast.Name):
        if node.id in safe_names and not callable(safe_names[node.id]):
            return float(safe_names[node.id])
        raise NameError(f"Undefined variable: '{node.id}'")
    else:
        raise TypeError(f"Unsupported node type: {type(node)}")

def evaluate_expression(expression):
    state = load_state()
    safe_names = base_safe_names.copy()
    safe_names.update(state)
    
    try:
        # Pre-process common math symbols for ease of use
        expr = expression.replace('^', '**')
        
        # Parse the expression
        tree = ast.parse(expr, mode='exec')
        
        if not tree.body:
            return {"status": "error", "error_type": "EmptyExpression", "message": "No expression provided."}
            
        node = tree.body[0]
        
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                return {"status": "error", "error_type": "InvalidAssignment", "message": "Only simple variable assignments are supported (e.g., 'x = 5')."}
            var_name = node.targets[0].id
            result = safe_eval(node.value, safe_names)
            state[var_name] = float(result)
            save_state(state)
            return {
                "status": "success",
                "input_expression": expression,
                "result_float": float(result),
                "saved_to_memory": var_name
            }
        elif isinstance(node, ast.Expr):
            result = safe_eval(node.value, safe_names)
            return {
                "status": "success",
                "input_expression": expression,
                "result_float": float(result)
            }
        else:
            return {"status": "error", "error_type": "UnsupportedStatement", "message": "Only expressions and simple assignments are supported."}
            
    except NameError as e:
        return {"status": "error", "error_type": "NameError", "message": str(e), "suggestion": "Ensure the variable is defined or the function is a valid math function (like sqrt, cos)."}
    except Exception as e:
        return {"status": "error", "error_type": type(e).__name__, "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="aim-calc: Agent-Native Scientific Calculator")
    parser.add_argument("expression", type=str, help="Mathematical expression to evaluate (e.g., 'v_leo = sqrt(9.81 * 6371)')")
    parser.add_argument("--audit-file", type=str, default=AUDIT_FILE, help="Path to the hidden audit log file")
    
    args = parser.parse_args()
    expression = args.expression
    audit_file = args.audit_file
    
    output_json = evaluate_expression(expression)
    
    # Silently log the attempt
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] INPUT: {expression} | OUTPUT: {json.dumps(output_json)}\n"
    
    try:
        with open(audit_file, "a") as f:
            f.write(log_entry)
    except Exception:
        pass # Silently fail
        
    print(json.dumps(output_json, indent=2))

if __name__ == "__main__":
    main()
