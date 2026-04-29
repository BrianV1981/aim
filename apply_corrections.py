import json
import re

def parse_question_id(question_id):
    """Parses a question_id like 'locomo_0_qa1' and returns (0, 1)."""
    match = re.match(r"locomo_(\d+)_qa(\d+)", question_id)
    if not match:
        raise ValueError(f"Invalid question_id format: {question_id}")
    return int(match.group(1)), int(match.group(2))

def apply_corrections(dataset, errors):
    """Applies corrections from errors list to the dataset in place.
    Returns the number of corrections applied.
    """
    count = 0
    for error in errors:
        qid = error.get("question_id")
        if not qid:
            continue
            
        dialogue_idx, qa_idx = parse_question_id(qid)
        
        # Safety checks
        if dialogue_idx >= len(dataset):
            print(f"Warning: dialogue_idx {dialogue_idx} out of bounds.")
            continue
            
        qa_list = dataset[dialogue_idx].get("qa", [])
        if qa_idx >= len(qa_list):
            print(f"Warning: qa_idx {qa_idx} out of bounds for dialogue {dialogue_idx}.")
            continue
            
        # Verify the question text matches roughly to ensure we're editing the right one
        original_q = qa_list[qa_idx].get("question", "")
        if isinstance(original_q, dict):
            original_q = original_q.get("text", "")
            
        error_q = error.get("question", "")
        
        if original_q.strip().lower() != error_q.strip().lower():
            print(f"Warning: Question mismatch at {qid}. Dataset: '{original_q}', Error: '{error_q}'")
            # We'll still apply it, but good to warn
            
        # Apply corrections
        qa_list[qa_idx]["answer"] = error.get("correct_answer")
        qa_list[qa_idx]["evidence"] = error.get("correct_evidence")
        count += 1
        
    return count

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to original locomo10.json")
    parser.add_argument("--errors", required=True, help="Path to locomo-audit errors.json")
    parser.add_argument("--output", required=True, help="Path to save the corrected dataset")
    args = parser.parse_args()
    
    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    with open(args.errors, "r", encoding="utf-8") as f:
        errors = json.load(f)
        
    print(f"Loaded dataset with {len(dataset)} dialogues.")
    print(f"Loaded {len(errors)} corrections.")
    
    count = apply_corrections(dataset, errors)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully applied {count} corrections.")
    print(f"Saved corrected dataset to {args.output}")

if __name__ == "__main__":
    main()
