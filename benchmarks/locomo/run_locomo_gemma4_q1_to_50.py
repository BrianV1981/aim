#!/usr/bin/env python3
import sys
import os
import json
import requests
import io
from contextlib import redirect_stdout

# Add core aim project for retriever
PROJECT_ROOT = "/home/kingb/aim"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from aim_core.retriever import perform_search_internal

# Add aim-locomo project root for evaluation imports
LOCOMO_ROOT = "/home/kingb/aim-locomo"
if LOCOMO_ROOT not in sys.path:
    sys.path.insert(0, LOCOMO_ROOT)
    sys.path.insert(0, os.path.join(LOCOMO_ROOT, "benchmarks/locomo/locomo_repo"))

try:
    from task_eval.evaluation import eval_question_answering
except ImportError:
    print("Warning: Snap-research locomo repo not found. Evaluator will skip F1.")
    eval_question_answering = None

DATA_FILE = "/home/kingb/locomo-v2/locomo_v2_final.json"
OUT_FILE = "/home/kingb/aim-locomo/benchmarks/locomo/locomo_track1_gemma4_q1_to_50.json"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma4:e4b"

def query_ollama(prompt):
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=600)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"[ERROR] Ollama API Error: {e}")
        return "TIMEOUT_ERROR"

def run_benchmark():
    print("--- LOADING LOCOMO V2 DATASET (TRACK 1 - GEMMA 4) ---")
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] Data file not found: {DATA_FILE}")
        return
        
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
    
    # Load existing progress
    results = []
    if os.path.exists(OUT_FILE):
        with open(OUT_FILE, "r") as f:
            results = json.load(f)
            
    completed = len(results)
    if completed >= len(flat_questions):
        print("Block already completed.")
        return
        
    print(f"Resuming from question {completed+1} / {len(flat_questions)}")
    
    for i in range(completed, len(flat_questions)):
        q_data = flat_questions[i]
        question = q_data["qa"]["question"]
        ground_truth = q_data["qa"].get("answer", "Unknown")
        
        print(f"\n[Q{i+1}/50] QUESTION: {question}")
        
        # 1. RAG 3.5 Retrieval (Bypassing CLI overhead)
        print("      Executing native RAG 3.5 Hybrid Search...")
        try:
            # We capture stdout to prevent perform_search_internal from spamming the console
            f_capture = io.StringIO()
            with redirect_stdout(f_capture):
                search_results = perform_search_internal(question, top_k=2, target_dbs=[os.path.join(LOCOMO_ROOT, "archive/datajack_library.db")])
            
            context_blocks = []
            if search_results:
                for res in search_results:
                    content = res.get('content', '')
                    if content:
                        context_blocks.append(content)
        except Exception as e:
            print(f"[ERROR] Retrieval failed: {e}")
            search_results = []
            context_blocks = []
            
        context_str = "\n\n---\n\n".join(context_blocks)
        if not context_str:
            context_str = "No relevant context found in Engram DB."
            
        prompt = f"""You are a strict technical retrieval agent. You MUST answer the following question using ONLY the provided context.
If you find the exact answer in the context, output it on a single line prefixed by exactly [ANSWER].
If the answer is NOT in the context, DO NOT guess. You MUST output exactly: [ANSWER] I don't know, should I use a google search?

CONTEXT:
{context_str}

QUESTION: {question}
"""
        
        print(f"      Querying {MODEL_NAME} via local Ollama...")
        response_text = query_ollama(prompt)
        
        predicted_answer = "TIMEOUT_ERROR"
        if "[ANSWER]" in response_text:
            try:
                predicted_answer = response_text.split("[ANSWER]")[1].strip().split('\n')[0].strip()
            except:
                predicted_answer = response_text
        else:
            # If the model disobeys formatting, capture its raw output
            predicted_answer = response_text.strip()
            
        print(f"      PREDICTED: {predicted_answer}")
        print(f"      GROUND TRUTH: {ground_truth}")
        
        # Calculate metric
        f1, exact_match = 0.0, False
        if eval_question_answering:
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
                print(f"      Eval error: {e}")
                
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
            
    print("\n--- TRACK 1 BLOCK COMPLETE ---")
    print(f"Results saved to {OUT_FILE}")

if __name__ == "__main__":
    run_benchmark()__main__":
    run_benchmark()