#!/usr/bin/env python3
import json
import os
import glob
import requests
from datetime import datetime

# --- CONFIGURATION ---
ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"
ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

class AIMIndexer:
    def __init__(self):
        self.raw_dir = ARCHIVE_RAW_DIR
        self.index_dir = ARCHIVE_INDEX_DIR
        
    def get_unprocessed_files(self):
        """Returns a list of raw JSON files that haven't been indexed yet."""
        # For simplicity in this prototype, we'll index everything.
        # In production, we would maintain an index of processed file hashes.
        return glob.glob(os.path.join(self.raw_dir, "*.json"))

    def extract_fragments(self, session_data):
        """
        Parses the session into 'Semantic Fragments' for indexing.
        Filters out noise and focuses on User intent, Model reasoning, and Model results.
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
        """Calls the local Ollama instance to get vector embeddings."""
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": text
            })
            return response.json().get('embedding')
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None

    def process(self):
        files = self.get_unprocessed_files()
        print(f"A.I.M. Indexer: Found {len(files)} files to process.")
        
        for file_path in files:
            print(f"Processing {os.path.basename(file_path)}...")
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            fragments = self.extract_fragments(data)
            
            # Add embeddings to fragments
            for frag in fragments:
                # We combine subject and content for thoughts to provide better context
                text_to_embed = frag.get('content', '')
                if frag.get('subject'):
                    text_to_embed = f"{frag.get('subject')}: {text_to_embed}"
                
                # Call Ollama to get the actual embedding
                frag['embedding'] = self.get_embedding(text_to_embed)
            
            # Save the processed fragments to the index
            output_path = os.path.join(self.index_dir, os.path.basename(file_path).replace('.json', '.fragments.json'))
            with open(output_path, 'w') as f:
                json.dump(fragments, f, indent=2)
            
            print(f"Successfully indexed {len(fragments)} fragments to {os.path.basename(output_path)}")

if __name__ == "__main__":
    indexer = AIMIndexer()
    indexer.process()
