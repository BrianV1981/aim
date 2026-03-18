#!/usr/bin/env python3
import os
import json
import sys
import re

# --- CONFIGURATION ---
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{48}",        # OpenAI API Key
    r"ghp_[a-zA-Z0-9]{36}",       # GitHub PAT
    r"-----BEGIN [A-Z ]+ PRIVATE KEY-----", # RSA/OpenSSH Private Keys
    r"\"[a-zA-Z0-9_\-\.]{10,}\"\s*:\s*\"[a-zA-Z0-9_\-\.]{20,}\"", # Likely API key-value pair
    r"password\s*:\s*[\"'][^\"']+[\"']", # Hardcoded passwords
    r"api_key\s*:\s*[\"'][^\"']+[\"']"   # Hardcoded API keys
]

def find_secrets(text):
    """Scans text for patterns that look like credentials."""
    for pattern in SECRET_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"Secret Pattern Detected: '{match.group(0)[:10]}...'"
    return None

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return

        data = json.loads(input_data)
        
        # BeforeTool payload for write_file/replace contains the content in args
        args = data.get('arguments', {})
        content = args.get('content', '') or args.get('new_string', '')

        # 1. Pattern Check
        reason = find_secrets(content)
        if reason:
            error_msg = f"SECRET SHIELD ALERT: Operation blocked. Potential credential leak detected: {reason}"
            print(json.dumps({
                "decision": "abort",
                "message": error_msg
            }))
            return

        # If everything looks good, proceed
        print(json.dumps({"decision": "proceed"}))

    except Exception:
        # Default to safe mode: proceed if we can't parse
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
