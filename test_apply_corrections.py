import pytest
from apply_corrections import parse_question_id, apply_corrections

def test_parse_question_id():
    assert parse_question_id("locomo_0_qa1") == (0, 1)
    assert parse_question_id("locomo_9_qa199") == (9, 199)
    
    with pytest.raises(ValueError):
        parse_question_id("invalid_id")

def test_apply_corrections():
    dataset = [
        {
            "sample_id": "conv-0",
            "qa": [
                {
                    "question": "Q0",
                    "answer": "wrong0",
                    "evidence": ["D0:0"]
                },
                {
                    "question": "Q1",
                    "answer": "wrong1",
                    "evidence": ["D1:0"]
                }
            ]
        }
    ]
    
    errors = [
        {
            "question_id": "locomo_0_qa1",
            "question": "Q1",
            "correct_answer": "right1",
            "correct_evidence": ["D1:1"]
        }
    ]
    
    count = apply_corrections(dataset, errors)
    assert count == 1
    assert dataset[0]["qa"][1]["answer"] == "right1"
    assert dataset[0]["qa"][1]["evidence"] == ["D1:1"]
    
    # Ensure Q0 was unaffected
    assert dataset[0]["qa"][0]["answer"] == "wrong0"
    assert dataset[0]["qa"][0]["evidence"] == ["D0:0"]

def test_apply_corrections_out_of_bounds():
    dataset = [
        {
            "sample_id": "conv-0",
            "qa": [
                {
                    "question": "Q0",
                    "answer": "wrong0",
                    "evidence": ["D0:0"]
                }
            ]
        }
    ]
    
    errors = [
        {
            "question_id": "locomo_1_qa0", # Dialogue doesn't exist
            "question": "Qx",
            "correct_answer": "rightx",
            "correct_evidence": ["Dx:x"]
        },
        {
            "question_id": "locomo_0_qa5", # QA doesn't exist
            "question": "Qy",
            "correct_answer": "righty",
            "correct_evidence": ["Dy:y"]
        }
    ]
    
    count = apply_corrections(dataset, errors)
    assert count == 0 # None should be applied
