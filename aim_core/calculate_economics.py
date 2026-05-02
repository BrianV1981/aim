import json
import argparse
from pathlib import Path
from typing import List, Dict

def calculate_session_cost(
    json_path: str,
    model: str = "deepseek-v4-pro"
) -> float:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Support both Gemini JSONL and OpenCode export JSON formats
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
    # Prices in USD per 1M tokens
    pricing = {
        # DeepSeek (OpenCode primary)
        "deepseek-v4-pro":      {"input": 0.55, "output": 2.19},
        "deepseek-chat":        {"input": 0.27, "output": 1.10},
        "deepseek-coder":       {"input": 0.27, "output": 1.10},
        "deepseek-r1":          {"input": 0.55, "output": 2.19},
        # Gemini (backward compat)
        "deepseek-chat": {"input": 0.27, "output": 1.10},
        "deepseek/deepseek-v4-pro": {"input": 0.55, "output": 2.19},
        "default":                {"input": 0.55, "output": 2.19},
    }

    rates = pricing.get(model.lower(), pricing["default"])

    input_cost = (total_input / 1_000_000) * rates["input"]
    output_cost = (total_output / 1_000_000) * rates["output"]
    total_cost = input_cost + output_cost

    print(f"\U0001f4c4 File: {Path(json_path).name}")
    print(f"   Model          : {model}")
    print(f"   Input tokens   : {total_input:,}  (cached: {total_cached:,})")
    print(f"   Output tokens  : {total_output:,}")
    print(f"   Thoughts tokens: {total_thoughts:,}")
    print(f"   Tool tokens    : {total_tool:,}")
    print(f"   \U0001f4b0 Estimated cost : ${total_cost:.6f} USD\n")

    return total_cost

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate benchmark economics from session JSON logs.")
    parser.add_argument("--logs", type=str, default="docs/benchmarks/raw_logs", help="Path to the logs directory")
    parser.add_argument("--model", type=str, default="deepseek-v4-pro", help="Model to use for pricing")
    args = parser.parse_args()

    logs_folder = Path(args.logs)
    
    if not logs_folder.exists():
        print(f"Error: Directory {logs_folder} not found.")
        exit(1)

    total_cost_all = 0.0
    for json_file in logs_folder.glob("*.json"):
        # Auto-detect model based on filename pattern
        if "deepseek" in json_file.name.lower() or "opencode" in json_file.name.lower():
            model_type = "deepseek-v4-pro"
        elif "pro" in json_file.name:
            model_type = "deepseek-chat"
        else:
            model_type = args.model
        cost = calculate_session_cost(str(json_file), model=model_type)
        total_cost_all += cost

    print("=" * 60)
    print(f"\U0001f3af GRAND TOTAL COST for all parsed files: ${total_cost_all:.4f} USD")
