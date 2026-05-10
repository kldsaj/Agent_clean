# Phase B Core Abstractions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first Phase B slice (`B1-B5`) with test-first abstractions, factories, and reranker fallback behavior.

**Architecture:** Each libs family gets a small abstract contract plus a factory that routes by provider/backend from `Settings`. Tests use fake implementations via injected registries so we can validate pluggability before real provider integrations exist.

**Tech Stack:** Python 3.9, `abc`, `typing`, `pytest`

---

### Task 1: Add tests for B1-B5 routing and contracts

**Files:**
- Create: `tests/unit/test_llm_factory.py`
- Create: `tests/unit/test_embedding_factory.py`
- Create: `tests/unit/test_splitter_factory.py`
- Create: `tests/unit/test_vector_store_contract.py`
- Create: `tests/unit/test_reranker_factory.py`

- [ ] Write failing tests for each factory and contract.
- [ ] Run targeted pytest commands and confirm red.

### Task 2: Implement base contracts and factories

**Files:**
- Create: `src/libs/llm/base_llm.py`
- Create: `src/libs/llm/llm_factory.py`
- Create: `src/libs/embedding/base_embedding.py`
- Create: `src/libs/embedding/embedding_factory.py`
- Create: `src/libs/splitter/base_splitter.py`
- Create: `src/libs/splitter/splitter_factory.py`
- Create: `src/libs/vector_store/base_vector_store.py`
- Create: `src/libs/vector_store/vector_store_factory.py`
- Create: `src/libs/reranker/base_reranker.py`
- Create: `src/libs/reranker/reranker_factory.py`
- Modify: `src/core/settings.py`

- [ ] Implement the smallest code that makes the tests pass.
- [ ] Keep provider selection centralized in factories only.

### Task 3: Verify and prepare for the next Phase B slice

**Files:**
- Modify: `src/libs/*/__init__.py` as needed

- [ ] Run the focused test suite for `B1-B5`.
- [ ] Confirm imports and routing behavior stay green.
- [ ] Hand off next slice: provider implementations (`B7.x`).
