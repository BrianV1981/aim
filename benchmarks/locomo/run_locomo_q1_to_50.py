#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess
import glob

# Add aim-locomo project root for evaluation imports
sys.path.insert(0, "/home/kingb/aim-locomo")
sys.path.insert(0, "/home/kingb/aim-locomo/benchmarks/locomo/locomo_repo")

try:
    from task_eval.evaluation import eval_question_answering
except ImportError:
    print("Warning: Snap-research locomo repo not found. Evaluator will skip F1.")

DATA_FILE = "/home/kingb/locomo-v2/locomo_v2_final.json"
OUT_FILE = "/home/kingb/aim-locomo/benchmarks/locomo/locomo_track2_q1_to_50.json"
TMUX_SESSION = "aim_track2_locomo"
TARGET_DIR = "/home/kingb/aim-locomo"
CHATS_DIR = os.path.expanduser("~/.gemini/tmp/aim-locomo/chats")

def send_to_tmux(text):
    """Sends text to tmux securely using the buffer to prevent dropped keystrokes."""
    # We must escape double quotes inside the text for the shell command
    escaped_text = text.replace('"', '\\"')
    subprocess.run(["tmux", "set-buffer", escaped_text], check=True)
    subprocess.run(["tmux", "paste-buffer", "-t", TMUX_SESSION], check=True)
    subprocess.run(["tmux", "send-keys", "-t", TMUX_SESSION, "Enter"], check=True)

def get_latest_jsonl():
    """Finds the active session log for the current agent."""
    files = glob.glob(os.path.join(CHATS_DIR, "session-*.jsonl"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def wait_for_answer(latest_jsonl, timeout=300):
    """Tails the jsonl file waiting for the agent to output [ANSWER]."""
    start_time = time.time()
    last_line_count = 0
    
    while time.time() - start_time < timeout:
        try:
            with open(latest_jsonl, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if len(lines) > last_line_count:
                # Check new lines for the answer
                for line in lines[last_line_count:]:
                    if not line.strip(): continue
                    try:
                        turn = json.loads(line)
                        role = turn.get('role', '').upper()
                        text = turn.get('text', '')
                        
                        # Verify this is a final model response (not a tool call)
                        if role in ['GEMINI', 'MODEL', 'ASSISTANT']:
                            if "[ANSWER]" in text:
                                answer = text.split("[ANSWER]")[1].strip().split('\n')[0].strip()
                                return answer
                    except Exception as e:
                        pass
                last_line_count = len(lines)
        except Exception:
            pass
            
        time.sleep(2)
        
    print("[ERROR] Timeout waiting for agent response.")
    return None

def start_agent():
    """Spawns the tmux session if it isn't running."""
    res = subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION], capture_output=True)
    if res.returncode != 0:
        print(f"Starting new tmux session: {TMUX_SESSION}")
        subprocess.run(["tmux", "new-session", "-d", "-s", TMUX_SESSION, "gemini"], cwd=TARGET_DIR, check=True)
        time.sleep(5) # Give the agent time to boot and create the jsonl
    else:
        print(f"Tmux session {TMUX_SESSION} already running.")

def run_benchmark():
    print("--- LOADING LOCOMO V2 DATASET ---")
    with open(DATA_FILE, "r") as f:
        samples = json.load(f)
        
    # Flatten the first 50 questions
    flat_questions = []
    for sample in samples:
        for qa in sample["qa"]:
            flat_questions.append({
                "sample_id": sample["sample_id"],
                "qa": qa
            })
            if len(flat_questions) == 50:
                break
        if len(flat_questions) == 50:
            break
            
    print(f"Loaded {len(flat_questions)} questions for this block.")
    
    # Start the agent
    start_agent()
    
    # Pre-flight check for jsonl
    latest_jsonl = get_latest_jsonl()
    if not latest_jsonl:
        print("[ERROR] Cannot find gemini session transcript. Is the agent running?")
        sys.exit(1)
        
    print(f"Tailing agent log: {latest_jsonl}")
    
    # Load existing progress
    results = []
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE, "r") as f:
            results = json.load(f)
            
    completed = len(results)
    print(f"Resuming from question {completed+1} / {len(flat_questions)}")
    
    for i in range(completed, len(flat_questions)):
        q_data = flat_questions[i]
        question = q_data["qa"]["question"]
        ground_truth = q_data["qa"].get("answer", "Unknown")
        
        print(f"\n[Q{i+1}/50] QUESTION: {question}")
        
        prompt = f"""We are running the LoCoMo benchmark. 
Please use the `run_shell_command` tool to execute `aim search` and search the Engram DB for the answer to the following question. 
When you have found the exact answer, you MUST output it on a single line prefixed by exactly [ANSWER]. 
DO NOT output [ANSWER] until you have the final result.

Question: {question}"""
        
        send_to_tmux(prompt)
        
        # We must re-fetch the jsonl path in case reincarnation happened (though not in Q1-50 until the end)
        latest_jsonl = get_latest_jsonl()
        predicted_answer = wait_for_answer(latest_jsonl)
        
        if not predicted_answer:
            predicted_answer = "TIMEOUT_ERROR"
            
        print(f"      PREDICTED: {predicted_answer}")
        
        # Calculate metric
        f1, exact_match = 0.0, False
        if "eval_question_answering" in globals():
            qa_pred = q_data["qa"].copy()
            qa_pred["prediction"] = predicted_answer
            if "answer" not in qa_pred and "adversarial_answer" in qa_pred:
                qa_pred["answer"] = qa_pred["adversarial_answer"]
                
            try:
                res = eval_question_answering([qa_pred], eval_key="prediction")
                if len(res) == 3:
                    all_ems, all_f1s, lengths = res
                    f1 = float(all_f1s[0] if isinstance(all_f1s, list) and len(all_f1s) > 0 else (all_f1s if not isinstance(all_f1s, list) else 0.0))
                    exact_match = bool(all_ems[0] > 0 if isinstance(all_ems, list) and len(all_ems) > 0 else (all_ems > 0 if not isinstance(all_ems, list) else False))
            except Exception as e:
                print(f"Eval error: {e}")
                
        result_record = {
            "sample_id": q_data["sample_id"],
            "question": question,
            "ground_truth": ground_truth,
            "prediction": predicted_answer,
            "f1": f1,
            "exact_match": exact_match
        }
        
        results.append(result_record)
        with open(OUT_FILE, "w") as f:
            json.dump(results, f, indent=4)
            
        time.sleep(3) # Breather
        
    print("\n--- BLOCK 1 COMPLETE ---")
    print("Initiating Sovereign Reincarnation Protocol...")
    send_to_tmux("/reincarnate")
    print("Command injected. The agent will now autonomously transition its session.")
    
if __name__ == "__main__":
    run_benchmark()