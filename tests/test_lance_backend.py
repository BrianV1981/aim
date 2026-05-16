import pytest
import os
import sys
import lancedb
import pyarrow as pa

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "aim_core")
if aim_root not in sys.path:
    sys.path.append(aim_root)
if src_dir not in sys.path:
    sys.path.append(src_dir)

import pandas as pd
from aim_core.lance_backend import generate_tantivy_query, VectorBackend, EntityIntersectionReranker

def test_generate_tantivy_query():
    # Test strict proper noun requirement and parenthesis preservation
    q = "What did Melanie do with (activities OR partake)?"
    fts, has_proper = generate_tantivy_query(q)
    assert has_proper
    assert "Melanie" in has_proper
    assert "melanie*" in fts
    assert "(" in fts and ")" in fts
    assert "activities*" in fts
    assert "partake*" in fts

def test_vector_backend_init(tmp_path):
    backend = VectorBackend(path=str(tmp_path))
    assert backend is not None
    table = backend.get_table()
    assert table is not None
    assert table.name == "fragments"

def test_add_fragments(tmp_path):
    backend = VectorBackend(path=str(tmp_path))
    fragments = [
        {
            "session_id": "test_session_1",
            "type": "session_history",
            "content": "This is a test fragment.",
            "vector": [0.1] * 768
        },
        {
            "session_id": "test_session_1",
            "type": "session_history",
            "content": "This is another test fragment.",
            "vector": [0.2] * 768
        }
    ]
    backend.add_fragments(fragments)
    
    table = backend.get_table()
    assert table.count_rows() == 2
    
    results = table.search("test fragment").limit(10).to_pandas()
    assert len(results) == 2
    assert "test_session_1" in results["session_id"].values


# --- RAG 5.21: EntityIntersectionReranker proper noun boosting tests ---

def _make_table(fragments):
    records = []
    for i, f in enumerate(fragments):
        records.append({
            "fragment_id": f.get("fragment_id", i + 1),
            "session_id": f.get("session_id", "test_session"),
            "type": f.get("type", "session_history"),
            "content": f.get("content", ""),
            "timestamp": f.get("timestamp", "2026-01-01T00:00:00Z"),
            "metadata": f.get("metadata", "{}"),
            "parent_id": f.get("parent_id", None),
            "source_db": f.get("source_db", "test"),
            "vector": f.get("vector", [0.1] * 768),
        })
    df = pd.DataFrame(records)
    return pa.Table.from_pandas(df)


def test_reranker_no_proper_nouns():
    reranker = EntityIntersectionReranker(proper_nouns=[])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "Jessica went camping in June."},
        {"fragment_id": 2, "content": "Jack went camping in July."},
    ])
    fts_table = _make_table([
        {"fragment_id": 1, "content": "Jessica went camping in June."},
    ])
    result = reranker.rerank_hybrid("who went camping", vec_table, fts_table)
    result_df = result.to_pandas()
    assert len(result_df) == 2
    score_1 = result_df[result_df["fragment_id"] == 1]["score"].values[0]
    score_2 = result_df[result_df["fragment_id"] == 2]["score"].values[0]
    assert score_1 > score_2


def test_reranker_with_proper_noun_boosts_match():
    reranker = EntityIntersectionReranker(proper_nouns=["Jessica"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "Jack went camping in July."},
        {"fragment_id": 2, "content": "Jessica went camping in June."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", vec_table, empty_table)
    result_df = result.to_pandas()
    top_row = result_df.iloc[0]
    assert top_row["fragment_id"] == 2


def test_reranker_proper_noun_not_present_no_boost():
    reranker = EntityIntersectionReranker(proper_nouns=["Sarah"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "Jack went camping."},
        {"fragment_id": 2, "content": "Jessica went camping."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", vec_table, empty_table)
    result_df = result.to_pandas()
    scores = result_df["score"].values
    assert result_df.iloc[0]["fragment_id"] == 1
    assert scores[0] > scores[1]


def test_reranker_case_insensitive_match():
    reranker = EntityIntersectionReranker(proper_nouns=["JESSICA"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "Jack went camping in July."},
        {"fragment_id": 2, "content": "Jessica went camping in June."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", vec_table, empty_table)
    result_df = result.to_pandas()
    top_row = result_df.iloc[0]
    assert top_row["fragment_id"] == 2


def test_reranker_multiple_proper_nouns():
    reranker = EntityIntersectionReranker(proper_nouns=["Jack", "Jessica"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "The weather was nice."},
        {"fragment_id": 2, "content": "Jack went fishing."},
        {"fragment_id": 3, "content": "Jessica went hiking."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("outdoor activities", vec_table, empty_table)
    result_df = result.to_pandas()
    top_ids = result_df["fragment_id"].values[:2]
    assert 1 not in top_ids


def test_reranker_empty_results_handled():
    reranker = EntityIntersectionReranker(proper_nouns=["Jessica"])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", empty_table, empty_table)
    assert result.num_rows == 0
