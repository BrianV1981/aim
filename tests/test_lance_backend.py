import pytest
import os
import lancedb
import pyarrow as pa
import pandas as pd
from aim_core.lance_backend import generate_tantivy_query, VectorBackend, EntityIntersectionReranker

def test_generate_tantivy_query():
    # RAG 5: strict proper noun inclusion with + prefix, returns list not bool
    q = "What did Melanie do with (activities OR partake)?"
    fts, proper_nouns = generate_tantivy_query(q)
    assert isinstance(proper_nouns, list)
    assert "Melanie" in proper_nouns
    assert "+melanie*" in fts
    assert "(" in fts and ")" in fts
    assert "activities*" in fts
    assert "partake*" in fts

def test_vector_backend_init(tmp_path):
    backend = VectorBackend(path=str(tmp_path))
    assert backend is not None
    table = backend.get_table()
    assert table is not None
    assert table.name == "fragments"


# --- RAG 5.21: EntityIntersectionReranker proper noun boosting tests ---

def _make_table(fragments):
    """Helper to build a pyarrow Table from a list of dicts for the reranker."""
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
    """Without proper nouns, scores are proportional to reciprocal rank."""
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
    # Frag 1 appears in both vec and fts → higher score
    score_1 = result_df[result_df["fragment_id"] == 1]["score"].values[0]
    score_2 = result_df[result_df["fragment_id"] == 2]["score"].values[0]
    assert score_1 > score_2


def test_reranker_with_proper_noun_boosts_match():
    """When both fragments are vector-only, the proper-noun one gets boosted above."""
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
    """Proper nouns that don't appear in any fragment change nothing."""
    reranker = EntityIntersectionReranker(proper_nouns=["Sarah"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "Jack went camping."},
        {"fragment_id": 2, "content": "Jessica went camping."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", vec_table, empty_table)
    result_df = result.to_pandas()
    scores = result_df["score"].values
    # Without boost, frag 1 outranks frag 2 by vec rank order
    assert result_df.iloc[0]["fragment_id"] == 1
    assert scores[0] > scores[1]


def test_reranker_case_insensitive_match():
    """Proper noun matching is case-insensitive."""
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
    """Any matching proper noun triggers boost for that fragment."""
    reranker = EntityIntersectionReranker(proper_nouns=["Jack", "Jessica"])
    vec_table = _make_table([
        {"fragment_id": 1, "content": "The weather was nice."},
        {"fragment_id": 2, "content": "Jack went fishing."},
        {"fragment_id": 3, "content": "Jessica went hiking."},
    ])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("outdoor activities", vec_table, empty_table)
    result_df = result.to_pandas()
    # Fragments 2 and 3 (with proper nouns) should be boosted above frag 1
    top_ids = result_df["fragment_id"].values[:2]
    assert 1 not in top_ids


def test_reranker_empty_results_handled():
    """Reranker handles empty inputs without error."""
    reranker = EntityIntersectionReranker(proper_nouns=["Jessica"])
    empty_table = _make_table([])
    result = reranker.rerank_hybrid("who went camping", empty_table, empty_table)
    assert result.num_rows == 0
