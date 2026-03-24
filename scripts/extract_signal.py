#!/usr/bin/env python3
import json
import sys
import os

def extract_signal(json_path):
    """
    Surgically extracts the architectural signal from a session JSON.
    Removes raw tool outputs while keeping Intent, Thoughts, and Actions.
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages') or data.get('session_history')
        if messages is None:
            return []
            
        signal = []
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
                
            m_role = msg.get('role') or msg.get('type')
            ts = msg.get('timestamp', 'Unknown')
            
            # --- SIGNAL EXTRACTION ---
            fragment = { "role": m_role, "timestamp": ts }
            
            content = msg.get('content')
            
            def process_content(c):
                if isinstance(c, list):
                    return " ".join([str(item.get('text', '')) for item in c if isinstance(item, dict) and 'text' in item])
                return str(c) if c is not None else ""

            if m_role == 'user' or m_role == 'system':
                fragment['text'] = process_content(content)
            
            elif m_role in ['gemini', 'model']:
                fragment['text'] = process_content(content)
                fragment['thoughts'] = msg.get('thoughts', [])
                
                # Capture the INTENT of the actions, not the raw output
                tool_calls = msg.get('toolCalls', []) or msg.get('tool_calls', [])
                fragment['actions'] = []
                for call in tool_calls:
                    if not isinstance(call, dict):
                        continue
                    name = call.get('name') or call.get('function', {}).get('name')
                    args = call.get('args') or call.get('function', {}).get('arguments')
                    fragment['actions'].append({ "tool": name, "intent": str(args)[:200] })
            else:
                # Skip tool results and other roles to maximize reduction
                continue
            
            signal.append(fragment)
            
        return signal
    except Exception as e:
        return f"Extraction Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_signal.py <path_to_json>")
        sys.exit(1)
    
    result = extract_signal(sys.argv[1])
    print(json.dumps(result, indent=2))
