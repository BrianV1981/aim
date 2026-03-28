#!/usr/bin/env python3
import os
import sys
import argparse
import concurrent.futures

# --- BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from reasoning_utils import generate_reasoning
from config_utils import CONFIG

def process_file(file_path, instruction):
    """Sub-agent worker function."""
    if not os.path.exists(file_path):
        return file_path, f"[ERROR] File not found: {file_path}"
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return file_path, f"[ERROR] Could not read file: {e}"
        
    prompt = f"INSTRUCTION:\n{instruction}\n\nFILE CONTENT ({file_path}):\n```\n{content}\n```\n\nPlease provide a concise answer directly addressing the instruction based solely on the file content."
    system_instruction = "You are a specialized sub-agent. Your job is to analyze a single file and provide a highly concise, binary or short-string answer based on the provided instruction. Do not write filler text."
    
    # Use tier1 (fast/cheap model) if configured, else default
    tier = "tier1" if "tier1" in CONFIG.get("models", {}).get("tiers", {}) else "default_reasoning"
    
    try:
        response = generate_reasoning(prompt, system_instruction=system_instruction, brain_type=tier, timeout=30)
        return file_path, response.strip()
    except Exception as e:
        return file_path, f"[ERROR] Sub-agent execution failed: {e}"

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Dynamic Sub-Agent Delegation (RLM Pattern)")
    parser.add_argument("instruction", help="The specific prompt/instruction for the sub-agents (e.g., 'Does this file contain the timeout bug?')")
    parser.add_argument("--files", nargs="+", required=True, help="List of files to process in parallel")
    
    args = parser.parse_args()
    
    print(f"--- A.I.M. SUB-AGENT DELEGATION ---")
    print(f"Instruction: {args.instruction}")
    print(f"Targets: {len(args.files)} files")
    print("Spawning parallel workers...\n")
    
    results = {}
    # Use ThreadPoolExecutor to run LLM network calls in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_file = {executor.submit(process_file, fp, args.instruction): fp for fp in args.files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            fp = future_to_file[future]
            try:
                fp_result, response = future.result()
                results[fp_result] = response
            except Exception as exc:
                results[fp] = f"[FATAL] {exc}"

    print("--- DELEGATION RESULTS ---")
    for fp in args.files:  # Print in original order
        res = results.get(fp, "[ERROR] No result")
        print(f"\n[Target]: {fp}\n[Result]: {res}")

if __name__ == "__main__":
    main()
