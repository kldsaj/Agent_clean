"""
Smoke test — verifies that all top-level packages are importable.

These tests run in isolation and set their own sys.path.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Project root: tests/unit/ -> tests/ -> project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"


def _ensure_path(path: Path) -> None:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.mark.unit
def test_core_package_import():
    """All top-level src/ packages and key sub-modules are importable."""
    _ensure_path(SRC_ROOT)
    _ensure_path(PROJECT_ROOT)

    # Top-level packages
    from src import core, ingestion, libs, mcp_server, observability

    # Key sub-modules referenced in DEV_SPEC
    from src.core import query_engine, response, trace
    from src.libs import llm, embedding, splitter, vector_store, reranker, evaluator
    from src.observability import dashboard

    assert core is not None
    assert ingestion is not None
    assert libs is not None
    assert mcp_server is not None
    assert observability is not None


@pytest.mark.unit
def test_config_files_exist():
    """All config files referenced in DEV_SPEC §5.2 are present."""
    assert (PROJECT_ROOT / "config" / "settings.yaml").exists()
    assert (PROJECT_ROOT / "config" / "prompts" / "image_captioning.txt").exists()
    assert (PROJECT_ROOT / "config" / "prompts" / "chunk_refinement.txt").exists()
    assert (PROJECT_ROOT / "config" / "prompts" / "rerank.txt").exists()


@pytest.mark.unit
def test_prompt_files_readable():
    """Prompt files contain non-empty, descriptive content."""
    for name in ["image_captioning.txt", "chunk_refinement.txt", "rerank.txt"]:
        path = PROJECT_ROOT / "config" / "prompts" / name
        content = path.read_text()
        assert len(content) > 10, f"{name} is empty or too short"


@pytest.mark.unit
def test_main_module_loadable():
    """main.py loads without syntax errors and exposes main()."""
    _ensure_path(PROJECT_ROOT)
    _ensure_path(SRC_ROOT)

    spec = importlib.util.spec_from_file_location("main", PROJECT_ROOT / "main.py")
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]

    assert hasattr(module, "main")
    assert callable(module.main)
