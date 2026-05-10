"""
Factory for constructing reranker implementations from settings.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional, Type

from src.core.settings import Settings
from src.libs.reranker.base_reranker import BaseReranker


class NoneReranker(BaseReranker):
    def rerank(self, query: str, candidates, trace: Optional[Any] = None):
        return list(candidates)


class RerankerFactory:
    _registry: dict[str, Type[BaseReranker]] = {"none": NoneReranker}

    @classmethod
    def register(cls, backend: str, implementation: Type[BaseReranker]) -> None:
        cls._registry[backend.lower()] = implementation

    @classmethod
    def create(
        cls,
        settings: Settings,
        registry: Optional[Mapping[str, Type[BaseReranker]]] = None,
    ) -> BaseReranker:
        backend = settings.retrieval.rerank_backend.lower()
        lookup = {key.lower(): value for key, value in (registry or cls._registry).items()}
        implementation = lookup.get(backend)
        if implementation is None:
            available = ", ".join(sorted(lookup)) or "<none>"
            raise ValueError(
                f"Unsupported rerank backend '{settings.retrieval.rerank_backend}'. "
                f"Available backends: {available}"
            )
        return implementation(settings.retrieval)
