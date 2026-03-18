#!/home/kingb/aim/venv/bin/python3
import json
import os
import glob
import sys
import keyring
from google import genai
from datetime import datetime

# --- CONFIGURATION ---
# Retrieve API key from local keyring
API_KEY = keyring.get_password("aim-system", "google-api-key")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("ERROR: GOOGLE_API_KEY not found in keyring. Run scripts/set_key.py first.", file=sys.stderr)
    sys.exit(1)

ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"
ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"
MODEL = "models/gemini-embedding-2-preview"

class AIMIndexer:
    def __init__(self, client):
        self.client = client
        self.raw_dir = ARCHIVE_RAW_DIR
        self.index_dir = ARCHIVE_INDEX_DIR
        
    def get_unprocessed_files(self):
        """Returns a list of raw JSON files that haven't been indexed yet."""
        return glob.glob(os.path.join(self.raw_dir, "*.json"))

    def extract_fragments(self, session_data):
        """
        Parses the session into 'Semantic Fragments' for indexing.
        """
        fragments = []
        messages = session_data.get('messages', [])
        
        for msg in messages:
            msg_type = msg.get('type')
            
            # 1. User Intent
            if msg_type == 'user':
                content = msg.get('content', [])
                text = " ".join([c.get('text', '') for c in content if 'text' in c])
                fragments.append({
                    "type": "user_prompt",
                    "content": text,
                    "timestamp": msg.get('timestamp')
                })
            
            # 2. Model Thoughts & Response
            elif msg_type == 'gemini':
                # The final response
                fragments.append({
                    "type": "model_response",
                    "content": msg.get('content', ''),
                    "timestamp": msg.get('timestamp')
                })
                
                # The internal reasoning (FORENSIC GOLD)
                thoughts = msg.get('thoughts', [])
                for thought in thoughts:
                    fragments.append({
                        "type": "model_thought",
                        "subject": thought.get('subject'),
                        "content": thought.get('description'),
                        "timestamp": thought.get('timestamp')
                    })
                
                # State-Changing Tool Calls (Selective)
                tool_calls = msg.get('toolCalls', [])
                for call in tool_calls:
                    tool_name = call.get('name')
                    if tool_name in ['replace', 'write_file', 'run_shell_command']:
                        fragments.append({
                            "type": "tool_action",
                            "tool": tool_name,
                            "args": call.get('args'),
                            "content": f"A.I.M. executed {tool_name} with args: {json.dumps(call.get('args'))}",
                            "timestamp": call.get('timestamp')
                        })
        
        return fragments

    def get_embedding(self, text):
        """Calls the Google GenAI SDK for high-fidelity vector embeddings."""
        try:
            result = self.client.models.embed_content(
                model=MODEL,
                contents=text,
                config={
                    'task_type': 'RETRIEVAL_DOCUMENT',
                    'title': 'A.I.M. Session Fragment'
                }
            )
            # The new SDK returns embeddings as a list of Embeddings objects
            return result.embeddings[0].values
        except Exception as e:
            # Silent failure to avoid leaking state in hooks
            return None

    def process(self):
        files = self.get_unprocessed_files()
        print(f"A.I.M. Indexer (Sovereign SDK): Found {len(files)} files to process.")
        
        for file_path in files:
            print(f"Processing {os.path.basename(file_path)}...")
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            fragments = self.extract_fragments(data)
            
            # Add embeddings to fragments
            for frag in fragments:
                text_to_embed = frag.get('content', '')
                if frag.get('subject'):
                    text_to_embed = f"{frag.get('subject')}: {text_to_embed}"
                
                # Call Google Embedding API
                frag['embedding'] = self.get_embedding(text_to_embed)
            
            # Save the processed fragments to the index
            output_path = os.path.join(self.index_dir, os.path.basename(file_path).replace('.json', '.fragments.json'))
            with open(output_path, 'w') as f:
                json.dump(fragments, f, indent=2)
            
            print(f"Successfully indexed {len(fragments)} fragments to {os.path.basename(output_path)}")

if __name__ == "__main__":
    if not client:
        print("ERROR: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    else:
        indexer = AIMIndexer(client)
        indexer.process()
