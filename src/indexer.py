#!/usr/bin/env python3
import json
import os
import glob
import sys
from datetime import datetime
from forensic_utils import get_embedding, ForensicDB, AIM_ROOT, chunk_text

ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
ARCHIVE_INDEX_DIR = os.path.join(AIM_ROOT, "archive/index")

class AIMIndexer:
    def __init__(self):
        self.raw_dir = ARCHIVE_RAW_DIR
        self.index_dir = ARCHIVE_INDEX_DIR
        self.db = ForensicDB()
        
    def get_unprocessed_files(self):
        """
        Returns a list of raw JSON files that are newer than their entries in the database.
        """
        all_raw = glob.glob(os.path.join(self.raw_dir, "*.json"))
        to_process = []
        
        for raw_path in all_raw:
            filename = os.path.basename(raw_path)
            session_id = filename.replace(".json", "")
            
            db_mtime = self.db.get_session_mtime(session_id)
            raw_mtime = os.path.getmtime(raw_path)
            
            if raw_mtime > db_mtime:
                to_process.append(raw_path)
                    
        return to_process

    def _add_fragment(self, fragments, f_type, content, timestamp, subject=None, metadata=None):
        """Internal helper to chunk and add fragments."""
        if not content: return
        
        # Semantic Chunking (Phase 12.1)
        # We split large blocks into manageable overlapping chunks
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            frag = {
                "type": f_type,
                "content": chunk,
                "timestamp": timestamp,
                "metadata": metadata or {}
            }
            if subject: frag["subject"] = subject
            if len(chunks) > 1:
                frag["metadata"]["chunk_index"] = i
                frag["metadata"]["total_chunks"] = len(chunks)
            
            fragments.append(frag)

    def extract_fragments(self, session_data):
        """
        Parses the session into 'Semantic Fragments' for indexing.
        """
        fragments = []
        messages = session_data.get('messages', [])
        
        for msg in messages:
            msg_type = msg.get('type')
            ts = msg.get('timestamp')
            
            if msg_type == 'user':
                content_list = msg.get('content', [])
                text = " ".join([c.get('text', '') for c in content_list if 'text' in c])
                self._add_fragment(fragments, "user_prompt", text, ts)
            
            elif msg_type == 'gemini':
                # Sub-divide the model's actual response
                self._add_fragment(fragments, "model_response", msg.get('content', ''), ts)
                
                # Thoughts
                thoughts = msg.get('thoughts', [])
                for thought in thoughts:
                    self._add_fragment(fragments, "model_thought", thought.get('description'), ts, subject=thought.get('subject'))
                
                # Tool Actions (Critical for forensic trail)
                tool_calls = msg.get('toolCalls', [])
                for call in tool_calls:
                    tool_name = call.get('name')
                    args_str = json.dumps(call.get('args'))
                    self._add_fragment(fragments, "tool_action", f"A.I.M. executed {tool_name} with args: {args_str}", ts, metadata={"tool": tool_name})
        
        return fragments

    def process(self):
        files = self.get_unprocessed_files()
        if not files:
            print("A.I.M. Indexer: Everything is up to date.")
            return

        print(f"A.I.M. Indexer: Found {len(files)} files to process.")
        
        for file_path in files:
            print(f"Processing {os.path.basename(file_path)}...")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Phase 24: The Contractor Protocol (The Bouncer)
            history = data.get('messages', []) or data.get('session_history', [])
            if history:
                first_msg = history[0]
                if first_msg.get('type') == 'user' or first_msg.get('role') == 'user':
                    content_val = first_msg.get('content', '')
                    text = ""
                    if isinstance(content_val, list):
                        text = " ".join([c.get('text', '') for c in content_val if isinstance(c, dict)])
                    elif isinstance(content_val, str):
                        text = content_val
                        
                    if '[EPHEMERAL]' in text:
                        print(f"Skipping {os.path.basename(file_path)}: Subagent noise detected.")
                        self.db.update_session_mtime(os.path.basename(file_path).replace(".json", ""), os.path.getmtime(file_path))
                        continue
            
            session_id = os.path.basename(file_path).replace(".json", "")
            fragments = self.extract_fragments(data)
            
            # Add embeddings to fragments
            for frag in fragments:
                text_to_embed = frag.get('content', '')
                if frag.get('subject'):
                    text_to_embed = f"{frag.get('subject')}: {text_to_embed}"
                
                frag['embedding'] = get_embedding(text_to_embed, task_type='RETRIEVAL_DOCUMENT')
            
            # Save to Database
            self.db.add_session(session_id, os.path.basename(file_path), os.path.getmtime(file_path))
            self.db.add_fragments(session_id, fragments)
            
            # Optional: Also save to JSON for legacy compatibility/backup
            output_path = os.path.join(self.index_dir, os.path.basename(file_path).replace('.json', '.fragments.json'))
            with open(output_path, 'w') as f:
                json.dump(fragments, f, indent=2)
            
            print(f"Successfully indexed {len(fragments)} fragments for {session_id}")
        
        self.db.close()

if __name__ == "__main__":
    indexer = AIMIndexer()
    indexer.process()
