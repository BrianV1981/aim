import sys
import os
import json
import time
import requests

PROJECT_ROOT = "/home/kingb/aim-locomo"
sys.path.insert(0, PROJECT_ROOT)

# Add snap-research/locomo to path for evaluation imports
sys.path.insert(0, os.path.join(PROJECT_ROOT, "benchmarks/locomo/locomo_repo"))
from task_eval.evaluation_stats import analyze_aggr_acc
from task_eval.evaluation import eval_question_answering

from aim_core.retriever import perform_search_internal
import aim_core.retriever

aim_core.retriever.get_federated_dbs = lambda: [os.path.join(PROJECT_ROOT, "archive/datajack_library.db")]

print("Loading locomo_v2_final.json benchmark questions...")
data_file = "/home/kingb/locomo-v2/locomo_v2_final.json"
out_file = os.path.join(PROJECT_ROOT, "benchmarks/locomo/locomo_rag2_predictions.json")

with open(data_file, "r") as f:
    samples = json.load(f)

# Try to resume if out_file exists
if os.path.exists(out_file):
    try:
        with open(out_file, "r") as f:
            predictions = json.load(f)
    except:
        predictions = []
else:
    predictions = []

completed_samples = {p.get("sample_id") for p in predictions if isinstance(p, dict)}

system_prompt = """You are an advanced Temporal RAG Evaluation Bot.
Your goal is to answer the user's question using ONLY the provided conversational context.

CRITICAL INSTRUCTION ON RELATIVE TIME:
Every line in the context is prefixed with a timestamp (e.g. `[1:56 pm on 8 May, 2023] **Caroline**: ...`).
If the speaker uses a relative time word like "yesterday", "last year", or "next month", you MUST mathematically calculate the exact date/year using the timestamp prefix on that specific line. 
DO NOT answer with "yesterday" or "last year". Give the calculated calendar date or year.

Answer concisely in a short phrase."""

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "gemma4:e4b"

def ask_ollama(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"Error: {e}"

for sample in samples:
    sample_id = sample.get("sample_id", "unknown")
    if sample_id in completed_samples:
        print(f"--- SKIPPING COMPLETED SAMPLE: {sample_id} ---")
        continue

    print(f"\n--- EVALUATING SAMPLE: {sample_id} ---")
    
    # 1. Create a brand new agent context for this dialogue (The 10-Session Rule)
    agent_memory = [
        {"role": "system", "content": system_prompt}
    ]

    qa_list = sample.get("qa", [])
    sample_preds = {"sample_id": sample_id, "qa": []}
    
    for idx, qa in enumerate(qa_list):
        question = qa["question"]
        ground_truth = qa.get("answer", "Unknown")
        
        print(f"\n[Q{idx+1}/{len(qa_list)}] QUESTION: {question}")
        
        # 0. Query Transformation (One-off call, doesn't pollute memory)
        transform_prompt = f"Rewrite the following question into a highly optimized search query for a database. Extract key entities, keywords, and temporal markers. Return ONLY the search query string (e.g. Word1 OR Word2 AND Word3), nothing else.\n\nQuestion: {question}"
        
        search_query = ask_ollama([
            {"role": "system", "content": "You are a search optimization bot."},
            {"role": "user", "content": transform_prompt}
        ])
                
        print(f"      TRANSFORMED QUERY: {search_query}")
        
        # 1. Forensic Retrieval
        results = perform_search_internal(search_query, top_k=10)
        
        # 2. Context Synthesis
        context = ""
        for i, res in enumerate(results):
            context += f"[{res.get('timestamp', 'Unknown Time')}] **{res.get('speaker', 'Unknown')}:** {res.get('content')}\n"
            
        # 3. Final Answer Generation (Persistent Memory)
        prompt = f"CONVERSATIONAL CONTEXT:\n{context}\n\nQUESTION: {question}"
        
        # Append the new question to the agent's rolling memory
        agent_memory.append({"role": "user", "content": prompt})
        
        answer = ask_ollama(agent_memory)
        
        # Append the agent's answer to its memory so it "remembers" it for the next question
        agent_memory.append({"role": "assistant", "content": answer})
            
        print(f"      PREDICTED RAG ANSWER: {answer}\n      GROUND TRUTH ANSWER: {ground_truth}")
        
        qa_pred = qa.copy()
        qa_pred["prediction"] = answer
        if "answer" not in qa_pred and "adversarial_answer" in qa_pred:
            qa_pred["answer"] = qa_pred["adversarial_answer"]
        
        # Calculate metric
        try:
            res = eval_question_answering([qa_pred], eval_key="prediction")
            if len(res) == 3:
                all_ems, all_f1s, lengths = res
                f1 = all_f1s[0] if isinstance(all_f1s, list) and len(all_f1s) > 0 else (all_f1s if not isinstance(all_f1s, list) else 0.0)
                exact_match = all_ems[0] > 0 if isinstance(all_ems, list) and len(all_ems) > 0 else (all_ems > 0 if not isinstance(all_ems, list) else False)
            else:
                f1, exact_match = 0.0, False
        except Exception as e:
            print(f"Evaluation error: {e}")
            f1, exact_match = 0.0, False
            
        qa_pred["pred"] = answer
        qa_pred["f1"] = f1
        qa_pred["exact_match"] = exact_match
        
        sample_preds["qa"].append(qa_pred)
        
    predictions.append(sample_preds)
    
    # Save incrementally
    with open(out_file, "w") as f:
        json.dump(predictions, f, indent=4)
        
print("\n--- ALL PREDICTIONS COMPLETE ---")

# Run aggregate evaluation
stats_file = out_file.replace('.json', '_stats.json')
analyze_aggr_acc(data_file, out_file, stats_file, "aim_rag2", "aim_rag2_f1", rag=True)
print(f"Evaluation complete. Stats saved to {stats_file}")
