#!/usr/bin/env python3
"""
A.I.M. LongMemEval Data Preparation Script (The Zero-Token Scribe for Benchmarks)

1. Unpacks the massive longmemeval_s_cleaned.json into 19,195 individual .jsonl files.
2. Immediately parses those .jsonl files through a custom extraction script to strip noise.
3. Converts them into clean, structured Markdown Flight Recorders (.md) for the Forge.
"""

import json
import os
from pathlib import Path
import sys
import re
import re

DATA_DIR = Path(__file__).parent / "data"
TEST_FILE = DATA_DIR / "longmemeval_s_cleaned.json"
JSONL_DIR = DATA_DIR / "raw_jsonl"
MD_DIR = DATA_DIR / "flight_recorders"

def process_content(c):
    """Clean up whitespace and formatting, similar to A.I.M.'s native extract_signal.py"""
    if isinstance(c, list):
        text = " ".join([str(item.get("text", "")) for item in c if isinstance(item, dict) and "text" in item])
    elif isinstance(c, dict):
        text = str(c.get("text", ""))
    else:
        text = str(c) if c is not None else ""
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def convert_to_markdown(session_id, messages):
    """
    Simulates A.I.M.'s Zero-Token Scribe.
    Converts a raw JSON list of messages into a highly structured Markdown Flight Recorder.
    """
    md_lines = [f"# Flight Recorder: {session_id}\n"]
    
    for msg in messages:
        role = str(msg.get("role", msg.get("speaker", "unknown"))).capitalize()
        content = process_content(msg.get("content", ""))
        
        if not content:
            continue
            
        match = re.search(r'\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)\d{2}\b', content, re.IGNORECASE)
        if match:
            current_date = f'[{match.group(0)}] '
        else:
            current_date = locals().get('current_date', '[Date Unknown] ')
        md_lines.append(f'{current_date}**{role}**: {content}\n')
        
    return "\n".join(md_lines)

def main():
    print("--- A.I.M. BENCHMARK DATA PREPARATION ---")
    
    if not TEST_FILE.exists():
        print(f"[ERROR] Original dataset not found at {TEST_FILE}")
        sys.exit(1)

    os.makedirs(JSONL_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    print("[1/2] Unpacking and Deduplicating Sessions...")
    questions = json.loads(TEST_FILE.read_text())
    
    unique_sessions = {}
    for item in questions:
        for sid, msgs in zip(item["haystack_session_ids"], item["haystack_sessions"]):
            if sid not in unique_sessions:
                unique_sessions[sid] = msgs

    total_sessions = len(unique_sessions)
    print(f"Found {total_sessions} unique sessions.")

    print("[2/2] Executing Zero-Token Scribe Extraction (JSONL -> MD)...")
    
    for i, (sid, msgs) in enumerate(unique_sessions.items()):
        # Step 1: Save as raw JSONL (simulating the raw transcript output)
        jsonl_file = JSONL_DIR / f"{sid}.jsonl"
        with open(jsonl_file, "w", encoding="utf-8") as f:
            for msg in msgs:
                f.write(json.dumps(msg) + "\n")
                
        # Step 2: Clean and convert to Markdown Flight Recorder
        md_content = convert_to_markdown(sid, msgs)
        md_file = MD_DIR / f"{sid}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        if (i + 1) % 1000 == 0:
            print(f"  -> Processed {i+1}/{total_sessions} sessions...")

    print(f"\n[SUCCESS] Extracted {total_sessions} clean Markdown Flight Recorders.")
    print(f"Location: {MD_DIR}")
    print("You can now run `aim bake` or our custom `build_cartridge.py` on this directory to generate high-fidelity vector embeddings.")

if __name__ == "__main__":
    main()