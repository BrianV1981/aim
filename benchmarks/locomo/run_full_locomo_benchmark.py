import sys
import os
import json
import time

PROJECT_ROOT = "/home/kingb/aim-locomo"
sys.path.insert(0, PROJECT_ROOT)

# Add snap-research/locomo to path for evaluation imports
sys.path.insert(0, os.path.join(PROJECT_ROOT, "benchmarks/locomo/locomo_repo"))
from task_eval.evaluation_stats import analyze_aggr_acc
from task_eval.evaluation import eval_question_answering

from aim_core.retriever import perform_search_internal
from aim_core.reasoning_utils import generate_reasoning
import aim_core.retriever

aim_core.retriever.get_federated_dbs = lambda: [os.path.join(PROJECT_ROOT, "archive/datajack_library.db")]

print("Loading locomo10.json benchmark questions...")
data_file = "/home/kingb/aim/locomo10.json"
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

for sample in samples:
    sample_id = sample["sample_id"]
    if sample_id in completed_samples:
        print(f"Skipping already completed sample: {sample_id}")
        continue
        
    print(f"--- EVALUATING SAMPLE: {sample_id} ---")
    
    qa_list = sample["qa"]
    sample_preds = {"sample_id": sample_id, "qa": []}
    
    for idx, qa in enumerate(qa_list):
        question = qa["question"]
        ground_truth = qa.get("answer", "Unknown")
        
        print(f"\n[Q{idx+1}/{len(qa_list)}] QUESTION: {question}")
        
        # 0. Query Transformation
        transform_prompt = f"Rewrite the following question into a highly optimized search query for a database. Extract key entities, keywords, and temporal markers. Return ONLY the search query string (e.g. Word1 OR Word2 AND Word3), nothing else.\n\nQuestion: {question}"
        while True:
            try:
                search_query = generate_reasoning(transform_prompt, system_instruction="You are a search optimization bot.", brain_type="default_reasoning").strip()
                if "[ERROR: CAPACITY_LOCKOUT]" in search_query:
                    print("      [RATE LIMIT] Capacity Lockout detected on transform. Sleeping for 30s...")
                    time.sleep(30)
                    continue
                break
            except Exception as e:
                search_query = question
                break
            
        print(f"      TRANSFORMED QUERY: {search_query}")
        
        # 1. Retrieve Context from Engram DB
        results = perform_search_internal(search_query, top_k=25)
        context = "\n".join([res["content"] for res in results])
        
        # 2. Format Prompt with Temporal Instructions
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nShort exact answer:"
        
        # 3. Generate Answer
        while True:
            try:
                answer = generate_reasoning(prompt, system_instruction=system_prompt, brain_type="default_reasoning").strip()
                if "[ERROR: CAPACITY_LOCKOUT]" in answer:
                    print("      [RATE LIMIT] Capacity Lockout detected on answer. Sleeping for 30s...")
                    time.sleep(30)
                    continue
                break
            except Exception as e:
                answer = f"Error: {e}"
                break
            
        print(f"      PREDICTED RAG ANSWER: {answer}")
        
        qa_pred = qa.copy()
        qa_pred["prediction"] = answer
        
        # Calculate metric
        try:
            em_score, f1_score, _, _, _ = eval_question_answering([qa_pred], eval_key="prediction")
            f1 = f1_score
            exact_match = em_score > 0
        except Exception as e:
            print(f"Evaluation error: {e}")
            f1, exact_match = 0.0, False
            
        qa_pred["pred"] = answer
        qa_pred["f1"] = f1
        qa_pred["exact_match"] = exact_match
        
        sample_preds["qa"].append(qa_pred)
        time.sleep(1) # Delay to avoid rate limits
        
    predictions.append(sample_preds)
    
    # Save incrementally
    with open(out_file, "w") as f:
        json.dump(predictions, f, indent=4)
        
print("\n--- ALL PREDICTIONS COMPLETE ---")

# Run aggregate evaluation
stats_file = out_file.replace('.json', '_stats.json')
analyze_aggr_acc(data_file, out_file, stats_file, "aim_rag2", "aim_rag2_f1", rag=True)
print(f"Evaluation complete. Stats saved to {stats_file}")