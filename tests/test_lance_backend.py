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

from aim_core.lance_backend import generate_tantivy_query, VectorBackend

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
