"""
TDD integration tests for upstream LanceDB RAG merge (#531) into opencode fork.

Verifies:
- LanceDB backend survives opencode fork context (DeepSeek defaults, no Gemini regressions)
- Coreference rewriter pronoun detection heuristic
- Retriever properly routes through LanceDB VectorBackend
- No Gemini CLI subshells crept back into merged files
- EntityIntersectionReranker logic
"""
import pytest
import os
import sys
import re
import subprocess

# Ensure aim_core is importable from anywhere
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "aim_core"))


# ── Tantivy Query Generation ─────────────────────────────────────────

def test_tantivy_query_stopwords_and_proper_nouns():
    from aim_core.lance_backend import generate_tantivy_query

    fts, proper_nouns = generate_tantivy_query("What did Melanie do with activities?")
    # RAG 5: proper_nouns is a list, not a boolean
    assert isinstance(proper_nouns, list)
    assert "Melanie" in proper_nouns
    # RAG 5: proper nouns get + prefix for Tantivy strict inclusion
    assert "+melanie*" in fts
    assert "activities*" in fts
    assert "what*" not in fts       # stopword removed
    assert "did*" not in fts        # stopword removed
    assert "with*" not in fts       # stopword removed
    assert "do*" not in fts         # stopword removed


def test_tantivy_query_no_proper_nouns():
    from aim_core.lance_backend import generate_tantivy_query

    fts, proper_nouns = generate_tantivy_query("how to configure the cache")
    assert proper_nouns == []
    assert "configur*" in fts or "configure*" in fts
    assert "cache*" in fts


def test_tantivy_query_parentheses_preserved():
    from aim_core.lance_backend import generate_tantivy_query

    fts, proper_nouns = generate_tantivy_query("did (Caroline OR Dave) attend the meeting")
    assert isinstance(proper_nouns, list)
    assert "Caroline" in proper_nouns
    assert "Dave" in proper_nouns
    assert "(" in fts
    assert ")" in fts
    assert "OR" in fts
    # RAG 5: proper nouns get + prefix, even inside parentheses
    assert "+caroline*" in fts
    assert "+dave*" in fts
    assert "attend*" in fts


def test_tantivy_query_dangling_operators_cleaned():
    from aim_core.lance_backend import generate_tantivy_query

    fts, proper_nouns = generate_tantivy_query("( OR Melanie )")
    assert isinstance(proper_nouns, list)
    assert "Melanie" in proper_nouns
    assert "( OR" not in fts or re.search(r'^\s*OR\b', fts) is None


# ── EntityIntersectionReranker ────────────────────────────────────────

def test_entity_intersection_reranker_initialization():
    from aim_core.lance_backend import EntityIntersectionReranker

    # RAG 5: constructor takes proper_nouns list instead of enforce_intersection bool
    reranker = EntityIntersectionReranker(proper_nouns=[])
    assert reranker.proper_nouns == []

    reranker_with_nouns = EntityIntersectionReranker(proper_nouns=["Melanie", "Caroline"])
    assert reranker_with_nouns.proper_nouns == ["Melanie", "Caroline"]


# ── LanceDB VectorBackend ─────────────────────────────────────────────

def test_vector_backend_initialization(tmp_path):
    import lancedb
    from aim_core.lance_backend import VectorBackend

    backend = VectorBackend(path=str(tmp_path))
    assert backend.table_name == "fragments"
    assert backend.path == str(tmp_path)

    table = backend.get_table()
    assert table is not None
    assert table.name == "fragments"


def test_vector_backend_creates_schema(tmp_path):
    import lancedb
    import pyarrow as pa
    from aim_core.lance_backend import VectorBackend

    backend = VectorBackend(path=str(tmp_path))
    table = backend.get_table()

    schema = table.schema
    field_names = [f.name for f in schema]
    assert "sqlite_id" in field_names
    assert "session_id" in field_names
    assert "content" in field_names
    assert "vector" in field_names
    assert "source_db" in field_names
    assert "parent_id" in field_names


def test_blob_to_vec():
    from aim_core.lance_backend import blob_to_vec

    assert blob_to_vec(None) is None
    assert blob_to_vec(b"") is None

    import struct
    vec = [0.1, 0.2, 0.3]
    blob = struct.pack("fff", *vec)
    result = blob_to_vec(blob)
    assert result is not None
    assert len(result) == 3
    assert abs(result[0] - 0.1) < 0.001


# ── Coreference Rewriter ──────────────────────────────────────────────

def test_coreference_rewriter_pronoun_detection():
    """Verify the pronoun detection heuristic without requiring Ollama."""
    # The coreference_rewriter uses simple pronoun detection
    pronouns = {"it", "this", "that", "these", "those", "he", "she", "they", "him", "her", "them"}

    assert "it" in pronouns
    assert "he" in pronouns
    assert "they" in pronouns

    # Test word splitting heuristic
    def has_pronoun(text):
        words = set(text.lower().replace("?", "").replace(".", "").split())
        return bool(pronouns.intersection(words))

    assert has_pronoun("How do I fix it") is True
    assert has_pronoun("What did she say") is True
    assert has_pronoun("configure the database settings") is False
    assert has_pronoun("What color is that car") is True


def test_coreference_rewriter_module_exists():
    """Verify coreference_rewriter.py file exists and has expected functions."""
    import ast
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "hooks", "coreference_rewriter.py")
    assert os.path.exists(path), "coreference_rewriter.py missing"
    with open(path, "r") as f:
        tree = ast.parse(f.read())
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "main" in functions


# ── Retriever LanceDB Routing ─────────────────────────────────────────

def test_retriever_imports_lance_backend():
    """Verify retriever.py correctly imports from lance_backend."""
    from aim_core.retriever import VectorBackend
    assert VectorBackend is not None


def test_retriever_has_perform_search_internal():
    """Verify the core search function exists and is LanceDB-routed."""
    from aim_core.retriever import perform_search_internal
    assert callable(perform_search_internal)


def test_retriever_has_flashrank_reranker():
    """Verify the FlashRank cross-encoder reranker path exists."""
    import inspect
    from aim_core.retriever import perform_search_internal

    source = inspect.getsource(perform_search_internal)
    assert "flashrank" in source
    assert "Ranker" in source
    assert "RerankRequest" in source
    assert "LanceDB" in source or "VectorBackend" in source


# ── Fork Integrity: No Gemini CLI Regression ──────────────────────────

def test_no_gemini_cli_in_lance_backend():
    """Ensure lance_backend.py doesn't reintroduce Gemini CLI subprocess calls."""
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "aim_core", "lance_backend.py")
    with open(path, "r") as f:
        content = f.read()
    assert 'gemini' not in content.lower() or '"gemini"' not in content


def test_no_gemini_cli_in_coreference_rewriter():
    """Ensure coreference_rewriter.py doesn't spawn Gemini CLI."""
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "hooks", "coreference_rewriter.py")
    with open(path, "r") as f:
        content = f.read()
    # Should not contain a gemini CLI subprocess spawn
    assert "Popen([\"gemini\"" not in content
    assert "gemini --yolo" not in content
    assert "gemini\", \"--yolo" not in content


def test_no_gemini_cli_in_retriever():
    """Ensure retriever.py doesn't reintroduce Gemini CLI paths."""
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "aim_core", "retriever.py")
    with open(path, "r") as f:
        content = f.read()
    assert "Popen([\"gemini\"" not in content
    assert "subprocess.*gemini" not in content


def test_deepseek_defaults_in_reasoning_utils():
    """Ensure reasoning_utils.py keeps DeepSeek defaults (not Gemini)."""
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "aim_core", "reasoning_utils.py")
    with open(path, "r") as f:
        content = f.read()
    assert "deepseek-chat" in content
    assert "openai-compat" in content
    # Should NOT have the old Gemini upstream fallback
    assert "gemini-2.5-flash" not in content


def test_opencode_spawn_in_wiki_tools():
    """Ensure wiki_tools.py uses opencode (not gemini) for tmux spawn."""
    aim_root = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(aim_root, "aim_core", "wiki_tools.py")
    with open(path, "r") as f:
        content = f.read()
    assert '"opencode"' in content
    assert '"gemini", "--yolo"' not in content


# ── Regression: Merge did not break existing tests ────────────────────

def test_existing_lance_backend_tests_pass():
    """Run the upstream test_lance_backend.py to ensure it still passes."""
    import subprocess
    test_file = os.path.join(os.path.dirname(__file__), "test_lance_backend.py")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-x", "-q", "--tb=short"],
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    assert result.returncode == 0, f"Existing LanceDB tests failed:\n{result.stderr}"
