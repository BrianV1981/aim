#!/home/kingb/aim/venv/bin/python3
import json
import os
import glob
import sys
from datetime import datetime
from forensic_utils import get_embedding

ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"
ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"

class AIMIndexer:
    def __init__(self):
        self.raw_dir = ARCHIVE_RAW_DIR
        self.index_dir = ARCHIVE_INDEX_DIR
        
    def get_unprocessed_files(self):
        """
        Returns a list of raw JSON files that are newer than their index counterparts.
        """
        all_raw = glob.glob(os.path.join(self.raw_dir, "*.json"))
        to_process = []
        
        for raw_path in all_raw:
            filename = os.path.basename(raw_path)
            index_path = os.path.join(self.index_dir, filename.replace(".json", ".fragments.json"))
            
            if not os.path.exists(index_path):
                # Never indexed
                to_process.append(raw_path)
            else:
                # Re-index only if raw is newer
                if os.path.getmtime(raw_path) > os.path.getmtime(index_path):
                    to_process.append(raw_path)
                    
        return to_process

    def extract_fragments(self, session_data):
        """
        Parses the session into 'Semantic Fragments' for indexing.
        """
        fragments = []
        messages = session_data.get('messages', [])
        
        for msg in messages:
            msg_type = msg.get('type')
            
            if msg_type == 'user':
                content = msg.get('content', [])
                text = " ".join([c.get('text', '') for c in content if 'text' in c])
                fragments.append({
                    "type": "user_prompt",
                    "content": text,
                    "timestamp": msg.get('timestamp')
                })
            
            elif msg_type == 'gemini':
                fragments.append({
                    "type": "model_response",
                    "content": msg.get('content', ''),
                    "timestamp": msg.get('timestamp')
                })
                
                thoughts = msg.get('thoughts', [])
                for thought in thoughts:
                    fragments.append({
                        "type": "model_thought",
                        "subject": thought.get('subject'),
                        "content": thought.get('description'),
                        "timestamp": thought.get('timestamp')
                    })
                
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

    def process(self):
        files = self.get_unprocessed_files()
        if not files:
            print("A.I.M. Indexer: Everything is up to date.")
            return

        print(f"A.I.M. Indexer: Found {len(files)} files to process.")
        
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
                
                frag['embedding'] = get_embedding(text_to_embed, task_type='RETRIEVAL_DOCUMENT')
            
            # Save the processed fragments to the index
            output_path = os.path.join(self.index_dir, os.path.basename(file_path).replace('.json', '.fragments.json'))
            with open(output_path, 'w') as f:
                json.dump(fragments, f, indent=2)
            
            print(f"Successfully indexed {len(fragments)} fragments to {os.path.basename(output_path)}")

if __name__ == "__main__":
    indexer = AIMIndexer()
    indexer.process()
