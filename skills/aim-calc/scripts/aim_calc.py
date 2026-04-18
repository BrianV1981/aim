import sys
import json
import math
import os
import traceback
from datetime import datetime

try:
    import pint
    ureg = pint.UnitRegistry()
    Q_ = ureg.Quantity
except ImportError:
    ureg = None
    Q_ = None

STATE_FILE = ".calc_state.json"
AUDIT_FILE = ".calc_audit.log"

def log_audit(input_expr, output_res):
    try:
        with open(AUDIT_FILE, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] INPUT: {input_expr} | OUTPUT: {output_res}\n")
    except Exception:
        pass

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "No expression provided."}))
        sys.exit(1)
        
    expr = sys.argv[1].strip()
    state = load_state()
    
    # Setup eval environment
    env = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    if ureg:
        env["u"] = ureg
        env["Q_"] = Q_
    
    # Load variables from state
    for k, v in state.items():
        # If it's a string, it might be a pint quantity representation
        if ureg and isinstance(v, str):
            try:
                env[k] = Q_(v)
                continue
            except Exception:
                pass
        env[k] = v

    var_name = None
    eval_expr = expr
    
    # Simple assignment parser: var_name = expression
    if "=" in expr and "==" not in expr and "!=" not in expr and "<=" not in expr and ">=" not in expr:
        parts = expr.split("=", 1)
        var_name = parts[0].strip()
        eval_expr = parts[1].strip()
        
    try:
        result = eval(eval_expr, {"__builtins__": {}}, env)
        
        res_val = result
        res_str = str(result)
        res_float = None
        
        if ureg and isinstance(result, type(ureg.Quantity(1))):
            res_val = str(result)
            try:
                res_float = float(result.magnitude)
            except Exception:
                pass
        else:
            try:
                res_float = float(result)
            except Exception:
                pass
                
        out = {
            "status": "success",
            "input_expression": expr,
            "result_formatted": res_str
        }
        
        if res_float is not None:
            out["result_float"] = res_float
            
        if var_name:
            state[var_name] = res_val
            save_state(state)
            out["saved_to_memory"] = var_name
            env[var_name] = result
            
        log_audit(expr, res_str)
        print(json.dumps(out, indent=2))
        
    except Exception as e:
        tb = traceback.format_exc()
        out = {
            "status": "error",
            "input_expression": expr,
            "error_type": type(e).__name__,
            "error": str(e),
            "traceback": tb
        }
        log_audit(expr, f"ERROR: {str(e)}")
        print(json.dumps(out, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
