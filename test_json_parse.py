import json
import re

out_str = """
⚠ Hook(s) [pre-compress-checkpoint] failed
[WARNING] some warning

{
  "session_id": "abc",
  "response": "OK",
  "stats": {"tokens": 100}
}
Created execution plan for SessionEnd...
Hook execution for SessionEnd...
"""

def extract_json(output):
    # Find all potential JSON blocks using regex
    # Non-greedy match from { to }
    matches = re.finditer(r'\{.*?\}', output, re.DOTALL)
    
    # But wait, non-greedy might stop at the first internal }, breaking nested JSON.
    # A better approach: stack-based brace matching to find outermost JSON objects.
    
    json_objects = []
    stack = []
    start_idx = -1
    
    for i, char in enumerate(output):
        if char == '{':
            if not stack:
                start_idx = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack: # Outermost object closed
                    json_objects.append(output[start_idx:i+1])
                    
    for obj_str in reversed(json_objects): # Start from the last printed JSON object
        try:
            parsed = json.loads(obj_str)
            if isinstance(parsed, dict) and "response" in parsed:
                return parsed["response"]
        except json.JSONDecodeError:
            continue
            
    return None

print(extract_json(out_str))
