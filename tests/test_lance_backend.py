import pytest
import os
import lancedb
import pyarrow as pa
from aim_core.lance_backend import generate_tantivy_query, VectorBackend

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
