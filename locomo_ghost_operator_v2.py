import os
import json
import time
import subprocess
import glob
from datetime import datetime

PROJECT_ROOT = "/home/kingb/aim-locomo"
DATA_FILE = "/home/kingb/benchmark_results/data/locomo_v2/locomo_v2_final.json"
if not os.path.exists(DATA_FILE):
    DATA_FILE = "/home/kingb/benchmark_results/data/locomo_v2/locomo_track1_qwen_q1_to_50.json"

def get_latest_transcript():
    # Gemini CLI saves transcripts for aim-locomo here
    search_dir = os.path.expanduser("~/.gemini/tmp/aim-locomo/chats/*.jsonl")
    files = glob.glob(search_dir)
    if not files: return None
    return max(files, key=os.path.getmtime)

def wait_for_response(transcript_path, last_line_count):
    print("Waiting for Gemini to finish generating answer...")
    raw_context = []
    final_answer = ""
    start_time = time.time()
    last_activity = start_time
    
    while True:
        try:
            with open(transcript_path, "r") as f:
                lines = f.readlines()
                if len(lines) > last_line_count:
                    new_lines = lines[last_line_count:]
                    last_line_count = len(lines)
                    last_activity = time.time()  # Reset: agent is alive
                    for line in new_lines:
                        try:
                            msg = json.loads(line)
                            raw_context.append(msg)
                            
                            # In Gemini CLI, tool responses usually have type "tool" or "tool_response"
                            # The agent's final text will be in a "gemini" message.
                            if msg.get("type") == "gemini":
                                content = msg.get("content", "")
                                # The A.I.M. system prompt requires answers to start with [ANSWER]
                                if "[ANSWER]" in content.upper() or "I don't know" in content:
                                    final_answer = content
                                    return final_answer, raw_context, last_line_count
                        except Exception as e:
                            pass
            
            # Dynamic timeout: only fail if agent has been idle for 120s
            idle_time = time.time() - last_activity
            if idle_time > 120:
                print(f"Timeout: agent idle for {int(idle_time)}s. Returning sentinel for retry.")
                return "TIMEOUT_NO_ANSWER", raw_context, last_line_count

            # Safety net: hard cap at 600s
            if time.time() - start_time > 600:
                print("Hard timeout after 600s.")
                return "TIMEOUT_NO_ANSWER", raw_context, last_line_count
                
            time.sleep(2)
        except Exception as e:
            time.sleep(2)

def send_via_buffer(session_name, text):
    # Avoid escaping issues by using a temp file and load-buffer instead of set-buffer
    tmp_file = "/tmp/locomo_benchmark_prompt.txt"
    with open(tmp_file, "w") as f:
        f.write(text)
    
    subprocess.run(["tmux", "load-buffer", tmp_file])
    subprocess.run(["tmux", "paste-buffer", "-t", session_name])
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"])

def run_ghost_operator():
    print(f"Loading data from {DATA_FILE}")
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        
    questions = []
    for sample in data:
        if "qa" in sample:
            for qa in sample["qa"]:
                questions.append(qa)
        elif "question" in sample:
            questions.append(sample)
                
    if not questions:
        print("No questions found.")
        return
        
    # The benchmark uses the first 199 questions for Track B
    questions = questions[:199]
    print(f"Loaded {len(questions)} questions. Sliced to 199 for Track B benchmark.")
    
    # Save to the benchmark_results folder with a timestamp to avoid overwriting RAG 5 / RAG 10 data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = "/home/kingb/benchmark_results/reports/locomo_v2/track_b"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"trackB_predictions_{timestamp}.json")
    
    predictions = []
    chunks = [200]
    idx = 0
    tmux_session = "ghost_aim"
    
    print(f"Starting new tmux session '{tmux_session}'...")
    subprocess.run(["tmux", "kill-session", "-t", tmux_session], stderr=subprocess.DEVNULL)
    # Spin up a new detached tmux session, cd to aim-locomo, launch gemini --yolo
    subprocess.run(["tmux", "new-session", "-d", "-s", tmux_session, "-c", PROJECT_ROOT, "gemini", "--yolo", "-m", "gemini-3-flash-preview"])
    time.sleep(5)

    # --- PRIMER LOGIC ---
    old_transcript = get_latest_transcript()
    primer_msg = "MANDATE: You are about to be given a series of 199 questions. This is a strict benchmark testing your RAG v5 memory system. For every question, you MUST use your search tool to find the answer. Answer directly and concisely. Acknowledge that you are ready."
    print("Sending benchmark primer to agent...")
    send_via_buffer(tmux_session, primer_msg)

    print("Waiting for new Gemini transcript to be created by primer...")
    transcript_path = old_transcript
    for _ in range(20):
        time.sleep(2)
        current = get_latest_transcript()
        if current and current != old_transcript:
            transcript_path = current
            break
    if not transcript_path or transcript_path == old_transcript:
        print("Could not find new Gemini transcript for primer. Proceeding with the latest found.")

    # Wait for the primer response so it doesn't pollute the first question
    last_line_count = 0
    ans, _, last_line_count = wait_for_response(transcript_path, last_line_count)
    print(f"Primer acknowledged: {ans[:50]}")
    # ---------------------

    for chunk_size in chunks:
        chunk_questions = questions[idx:idx+chunk_size]
        if not chunk_questions: break

        print(f"\\n--- STARTING BATCH OF {len(chunk_questions)} ---")

        for i, qa in enumerate(chunk_questions):
            q = qa["question"]
            print(f"Sending: {q}")

            old_transcript = transcript_path
            
            max_retries = 3
            ans = ""
            raw_context = []
            
            for attempt in range(max_retries):
                # Simulate human typing via tmux buffer
                send_via_buffer(tmux_session, q)
                
                ans, raw_context, last_line_count = wait_for_response(transcript_path, last_line_count)
                print(f"Answer received: {ans[:50].replace(chr(10), ' ')}...")
                
                ans_lower = ans.lower()
                if "startcall:" in ans_lower or "native cli exception" in ans_lower or "ollama error" in ans_lower:
                    print(f"⚠️ Detected tool leak or error. Retrying ({attempt+1}/{max_retries})...")
                    time.sleep(5) # Pacing before retry
                    q = "You experienced a tool error or leaked raw JSON. Please use the aim-locomo search tool correctly and answer the question: " + qa["question"]
                    continue
                else:
                    break # Valid answer received
            
            pred = qa.copy()
            pred["prediction"] = ans
            pred["raw_rag_context"] = raw_context # Inject the raw tool calls and context into the output!
            predictions.append(pred)
            
            with open(out_file, "w") as f:
                json.dump(predictions, f, indent=4)
                
            print("Pacing: Sleeping for 5 seconds before next question...")
            time.sleep(5)
            
        idx += chunk_size
        print(f"Batch complete. Handled {chunk_size} questions.")
                
    print(f"All chunks completed. Results saved to {out_file}. Leaving tmux session open for manual review.")

if __name__ == "__main__":
    run_ghost_operator()
