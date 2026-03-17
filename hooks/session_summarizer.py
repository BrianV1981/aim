#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime

def summarize_session(history):
    # This is a placeholder for where we would normally call a model to summarize.
    # For now, we will extract the key commands and build a structured log.
    
    summary = []
    for turn in history:
        if turn.get('role') == 'user':
            summary.append(f"### Brian: {turn.get('content')[:100]}...")
        elif turn.get('role') == 'model':
            # Extract tool calls for technical context
            calls = turn.get('tool_calls', [])
            if calls:
                tool_names = [call.get('function', {}).get('name') for call in calls]
                summary.append(f"**J.A.R.V.I.S.:** Executed tools: {', '.join(tool_names)}")
    
    return "\n".join(summary)

def main():
    try:
        # 1. Read input from Gemini CLI
        input_data = sys.stdin.read()
        if not input_data:
            sys.stderr.write("Error: No input data received on stdin.\n")
            sys.exit(0)

        data = json.loads(input_data)
        history = data.get('session_history', [])
        
        # 2. Setup Daily Log Path
        today = datetime.now().strftime("%Y-%m-%d")
        log_dir = "/home/kingb/memory"
        log_path = os.path.join(log_dir, f"{today}.md")
        
        # 3. Create/Append to Log
        with open(log_path, "a") as f:
            f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
            # In a real hook, we'd pass the history back to a model for a better summary,
            # but for this POC, we'll log the basic session flow.
            f.write("Status: Session ended and summarized by J.A.R.V.I.S.\n")
            f.write("Key Actions:\n")
            f.write(summarize_session(history))
            f.write("\n---\n")

        # 4. Return success to Gemini CLI
        print(json.dumps({"decision": "proceed"}))

    except Exception as e:
        sys.stderr.write(f"Error in session_summarizer.py: {str(e)}\n")
        # Return success anyway so we don't block the session end, but log the error
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
