import pytest
import os
import lancedb
import pyarrow as pa
from aim_core.lance_backend import generate_tantivy_query, VectorBackend

def test_generate_tantivy_query():
    # Test strict proper noun requirement and parenthesis preservation
    q = "What did Melanie do with (activities OR partake)?"
    fts, has_proper = generate_tantivy_query(q)
    assert has_proper is True
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
