"""
Modular RAG MCP Server — Application Entry Point

This module initializes the application:
1. Loads and validates configuration from config/settings.yaml
2. Initializes logging
3. Exposes the MCP server start-up routine

Usage:
    python main.py                  # Start MCP server (stdio mode)
    python main.py --check-config   # Validate config and exit
    python main.py --version        # Print version and exit
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on the path so "from src.xxx import yyy" works
_project_root = Path(__file__).parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.core.settings import load_settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="modular-rag",
        description="Modular RAG MCP Server — A pluggable, observable RAG service framework.",
    )
    parser.add_argument("--check-config", action="store_true",
                        help="Load and validate config, then exit.")
    parser.add_argument("--version", action="store_true",
                        help="Print version and exit.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.version:
        print("modular-rag-mcp-server v0.1.0")
        return 0

    # Load and validate configuration
    try:
        settings = load_settings()
    except FileNotFoundError:
        print("ERROR: config/settings.yaml not found.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Failed to load configuration: {exc}", file=sys.stderr)
        return 1

    if args.check_config:
        print(f"OK: Configuration loaded successfully.")
        print(f"  LLM provider : {settings.llm.provider}")
        print(f"  Embedding    : {settings.embedding.provider}")
        print(f"  Vector store  : {settings.vector_store.backend}")
        print(f"  Rerank       : {settings.retrieval.rerank_backend}")
        print(f"  Dashboard    : {'enabled' if settings.dashboard.enabled else 'disabled'}")
        return 0

    # Placeholder: start MCP server (implemented in Phase E)
    print("Modular RAG MCP Server is running. (MCP server startup in Phase E)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
