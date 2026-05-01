import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../aim_core')))
from extract_signal import extract_signal, skeleton_to_markdown

def test_legacy_thought_formatting(tmp_path):
    """
    Tests that if an older session has massive 'thought blocks' embedded
    directly inside the content field (instead of the structured 'thoughts' array),
    extract_signal.py correctly identifies it as a monologue and wraps it
    so the RAG 4.0 scrubber can incinerate it.
    """
    
    # Simulate a massive legacy thought block inside the content field
    legacy_thought_text = "I am investigating the wipe_docs function within the aim_core/aim_init.py file. My primary objective is to understand its file deletion mechanisms.\n\n" * 50
    legacy_thought_text += "Here is the actual answer you requested."
    
    payload = {
        "role": "model",
        "content": legacy_thought_text,
        "timestamp": "2026-04-26T22:02:43.122Z"
    }
    
    test_jsonl = tmp_path / "test_legacy.jsonl"
    with open(test_jsonl, "w") as f:
        f.write(json.dumps(payload) + "\n")
        
    skeleton = extract_signal(str(test_jsonl))
    md_output = skeleton_to_markdown(skeleton, "session_123")
    
    # The markdown output MUST wrap the massive investigative block in the > **Internal Monologue:** syntax
    assert "> **Internal Monologue:**" in md_output, "Failed to wrap legacy thoughts in monologue syntax"
    assert "> * I am investigating the wipe_docs function" in md_output, "Failed to prefix legacy thoughts with blockquote syntax"
    
    # The actual answer should remain outside the blockquote
    assert "Here is the actual answer you requested." in md_output
    assert "> * Here is the actual answer you requested." not in md_output
