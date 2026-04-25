import json
import argparse
from pathlib import Path
from typing import List, Dict

def calculate_gemini_session_cost(
    json_path: str,
    model: str = "gemini-3-flash-preview"
) -> float:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Some gemini logs have a 'messages' key, some might be a raw list
    if isinstance(data, dict) and "messages" in data:
        turns = data["messages"]
    else:
        turns: List[Dict] = data if isinstance(data, list) else [data]

    total_input = 0
    total_output = 0
    total_cached = 0
    total_thoughts = 0
    total_tool = 0

    for turn in turns:
        tokens = turn.get("tokens", {})
        if not tokens:
            continue
        total_input += tokens.get("input", 0)
        total_output += tokens.get("output", 0)
        total_cached += tokens.get("cached", 0)
        total_thoughts += tokens.get("thoughts", 0)
        total_tool += tokens.get("tool", 0)

    # ====================== PRICING ======================
    # Using OpenRouter Preview Pricing for benchmarks
    pricing = {
        "gemini-3-flash-preview": {"input": 0.50, "output": 3.00},
        "gemini-3.1-pro-preview": {"input": 2.00, "output": 12.00},
        "default":                {"input": 0.50, "output": 3.00},
    }

    rates = pricing.get(model.lower(), pricing["default"])

    input_cost = (total_input / 1_000_000) * rates["input"]
    output_cost = (total_output / 1_000_000) * rates["output"]
    total_cost = input_cost + output_cost

    print(f"📄 File: {Path(json_path).name}")
    print(f"   Model          : {model}")
    print(f"   Input tokens   : {total_input:,}  (cached: {total_cached:,})")
    print(f"   Output tokens  : {total_output:,}")
    print(f"   Thoughts tokens: {total_thoughts:,}")
    print(f"   Tool tokens    : {total_tool:,}")
    print(f"   💰 Estimated cost : ${total_cost:.6f} USD\n")

    return total_cost

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate benchmark economics from raw Gemini CLI JSON logs.")
    parser.add_argument("--logs", type=str, default="docs/benchmarks/raw_logs", help="Path to the logs directory")
    args = parser.parse_args()

    logs_folder = Path(args.logs)
    
    if not logs_folder.exists():
        print(f"Error: Directory {logs_folder} not found.")
        exit(1)

    total_cost_all = 0.0
    for json_file in logs_folder.glob("*.json"):
        # Auto-detect model based on filename for our benchmarks
        model_type = "gemini-3.1-pro-preview" if "pro" in json_file.name else "gemini-3-flash-preview"
        cost = calculate_gemini_session_cost(str(json_file), model=model_type)
        total_cost_all += cost

    print("=" * 60)
    print(f"🎯 GRAND TOTAL COST for all parsed files: ${total_cost_all:.4f} USD")