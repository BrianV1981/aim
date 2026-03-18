#!/usr/bin/env python3
import os
import json
import subprocess
import glob

# --- CONFIGURATION ---
ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"
SUMMARIZER_PATH = "/home/kingb/aim/hooks/session_summarizer.py"

def back_populate():
    """Iterates through archived sessions and runs the summarizer on them."""
    transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    transcripts.sort() # Process in chronological order based on filename
    
    print(f"Found {len(transcripts)} transcripts to process.")
    
    for transcript_path in transcripts:
        print(f"Processing: {os.path.basename(transcript_path)}...")
        try:
            with open(transcript_path, 'r') as f:
                data = json.load(f)
            
            # Map transcript schema to summarizer schema
            # Transcript: sessionId -> Summarizer: session_id
            # Transcript: messages -> Summarizer: session_history
            
            # The summarizer expects 'role' (user/model) but transcript has 'type' (user/gemini)
            history = []
            for msg in data.get('messages', []):
                role = 'user' if msg.get('type') == 'user' else 'model'
                # Handle content which is a list in transcripts
                content = msg.get('content', '')
                history.append({
                    'role': role,
                    'content': content,
                    'tool_calls': msg.get('toolCalls', []) # Transcript uses toolCalls, summarizer uses tool_calls
                })
            
            payload = {
                "session_id": data.get('sessionId'),
                "session_history": history
            }
            
            # Pipe the payload to the summarizer
            process = subprocess.Popen(
                ["python3", SUMMARIZER_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=json.dumps(payload))
            
            if stderr:
                print(f"  Error: {stderr.strip()}")
            else:
                print(f"  Success: {stdout.strip()}")
                
        except Exception as e:
            print(f"  Failed to process {transcript_path}: {e}")

if __name__ == "__main__":
    back_populate()
