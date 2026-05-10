# Phase B Core Libs Design

**Scope:** Phase B first slice covering `B1-B5` only.

## Goal

Turn the current config-only pluggability into code-level pluggability for:

- LLM
- Embedding
- Splitter
- VectorStore
- Reranker

## Design

Each library family gets:

- one abstract base class defining the contract
- one factory as the single provider-routing entry point
- focused unit tests that validate routing and error behavior

Provider-specific implementations are intentionally deferred to later Phase B
tasks. For this slice, factories must support injected registries so tests can
exercise routing with fake implementations.

## Key Decisions

- Factories own provider selection. Higher-level pipeline/query code should not
  branch on provider names.
- Reranker includes a built-in `NoneReranker` fallback for
  `retrieval.rerank_backend=none`.
- Vector store uses dict-based record/result contracts for now so it does not
  depend on Phase C types.
- Splitter config adds a minimal `splitter_backend` field under ingestion to
  make provider routing explicit.

## Success Criteria

- `B1-B5` tests exist and pass.
- Unknown providers fail with readable errors.
- Factory routing is deterministic and isolated from implementation details.
