#!/usr/bin/env python3
import sys
import math
import datetime
import os
import argparse
import ast
import operator

# Define a safe environment for evaluation
safe_names = {'__builtins__': None}
for name, val in vars(math).items():
    if not name.startswith('_'):
        safe_names[name] = val

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

def safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op = type(node.op)
        if op in allowed_operators:
            return allowed_operators[op](left, right)
        else:
            raise TypeError(f"Unsupported operator: {op}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op = type(node.op)
        if op in allowed_operators:
            return allowed_operators[op](operand)
        else:
            raise TypeError(f"Unsupported unary operator: {op}")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in safe_names and callable(safe_names[func_name]):
                args = [safe_eval(arg) for arg in node.args]
                return safe_names[func_name](*args)
            else:
                raise NameError(f"Unsupported function: {func_name}")
        else:
             raise TypeError(f"Unsupported function call type")
    elif isinstance(node, ast.Name):
        if node.id in safe_names and not callable(safe_names[node.id]):
            return safe_names[node.id]
        raise NameError(f"Unsupported variable: {node.id}")
    else:
        raise TypeError(f"Unsupported node type: {type(node)}")

def evaluate_expression(expression):
    try:
        # Pre-process common math symbols for ease of use
        expr = expression.replace('^', '**')
        
        # Parse the expression
        tree = ast.parse(expr, mode='eval')
        result = safe_eval(tree.body)
        return float(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Scientific Calculator (Silent Audit Tool)")
    parser.add_argument("expression", type=str, help="Mathematical expression to evaluate (e.g., 'sqrt(9.81 * 6371)')")
    parser.add_argument("--audit-file", type=str, default="benchmark_audit.log", help="Path to the hidden audit log file")
    
    args = parser.parse_args()
    expression = args.expression
    audit_file = args.audit_file
    
    result = evaluate_expression(expression)
    
    # Silently log the attempt
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] INPUT: {expression} | OUTPUT: {result}\n"
    
    try:
        with open(audit_file, "a") as f:
            f.write(log_entry)
    except Exception:
        pass # Silently fail if logging fails to prevent the agent from knowing it's being audited
        
    print(result)

if __name__ == "__main__":
    main()
