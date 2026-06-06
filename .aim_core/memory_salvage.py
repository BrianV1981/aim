#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime

# Import the existing signal extraction logic so we don't duplicate code
from extract_signal import extract_signal, skeleton_to_markdown

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()

def detect_format(filepath):
    """Stage 1: The Detective (Auto-Detection)"""
    if filepath.endswith('.md'):
        return 'markdown'
    
    try:
        with open(filepath, 'r') as f:
            first_char = f.read(1)
            if first_char == '[':
                return 'json_array'
            return 'jsonl'
    except:
        return 'unknown'

def clean_and_flatten(filepath, format_type):
    """Stage 2 & 3: The Cleaner and Flattener"""
    session_id = os.path.basename(filepath).replace('.jsonl', '').replace('.json', '')
    
    if format_type == 'jsonl':
        # Leverage existing A.I.M. extraction logic for jsonl
        print(f"[*] Extracting signal skeleton from JSONL...")
        skeleton = extract_signal(filepath)
        if isinstance(skeleton, str) and skeleton.startswith("Extraction Error"):
            print(f"[ERROR] {skeleton}")
            return None
    elif format_type == 'json_array':
        # Future-proofing: Parse standard JSON arrays (like Claude/ChatGPT dumps)
        # For now, we attempt a basic map to our skeleton format
        print(f"[*] Parsing monolithic JSON Array...")
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            skeleton = []
            for msg in data:
                if not isinstance(msg, dict): continue
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if isinstance(content, list):
                    text = " ".join([str(item.get("text", "")) for item in content if isinstance(item, dict)])
                else:
                    text = str(content)
                skeleton.append({"role": role, "text": text, "timestamp": "Imported"})
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON Array: {e}")
            return None
    else:
        print(f"[ERROR] Unsupported format for cleaning: {format_type}")
        return None

    print(f"[*] Flattening skeleton into Obsidian-native Markdown...")
    md_content = skeleton_to_markdown(skeleton, session_id)
    
    # Save the flattened file to the local history vault
    history_dir = os.path.join(AIM_ROOT, ".archive", "history")
    os.makedirs(history_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    salvaged_path = os.path.join(history_dir, f"{timestamp}_salvaged_{session_id}.md")
    
    with open(salvaged_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"[SUCCESS] Salvaged markdown saved to: {salvaged_path}")
    return salvaged_path

def handoff_to_swarm(md_path):
    """Stage 4: The Handoff"""
    print(f"[*] Triggering Watchdog/Scribe Handoff...")
    script_path = os.path.join(AIM_ROOT, "hooks", "session_summarizer.py")
    
    if not os.path.exists(script_path):
        print(f"[ERROR] Watchdog script not found at {script_path}")
        return
        
    try:
        subprocess.run([sys.executable, script_path, "--reincarnate", md_path], check=True)
        print(f"\\n[SUCCESS] Memory Salvage Engine complete. Swarm is processing.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Watchdog handoff failed with code {e.returncode}")

def main():
    if len(sys.argv) < 2:
        print("Usage: memory_salvage.py <path/to/raw/log>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
        
    print(f"\\n--- A.I.M. UNIVERSAL MEMORY SALVAGE ENGINE ---")
    print(f"[*] Target: {filepath}")
    
    format_type = detect_format(filepath)
    print(f"[*] Detected Format: {format_type.upper()}")
    
    if format_type == 'markdown':
        print(f"[*] Clean Markdown detected. Bypassing Cleaner. Routing straight to Handoff...")
        handoff_to_swarm(filepath)
    elif format_type in ['jsonl', 'json_array']:
        md_path = clean_and_flatten(filepath, format_type)
        if md_path:
            handoff_to_swarm(md_path)
    else:
        print(f"[ERROR] Unknown file structure. Cannot salvage.")

if __name__ == "__main__":
    main()