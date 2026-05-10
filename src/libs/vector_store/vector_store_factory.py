"""
Factory for constructing vector store implementations from settings.
"""
from __future__ import annotations

from typing import Mapping, Optional, Type

from src.core.settings import Settings
from src.libs.vector_store.base_vector_store import BaseVectorStore


class VectorStoreFactory:
    _registry: dict[str, Type[BaseVectorStore]] = {}

    @classmethod
    def register(cls, backend: str, implementation: Type[BaseVectorStore]) -> None:
        cls._registry[backend.lower()] = implementation

    @classmethod
    def create(
        cls,
        settings: Settings,
        registry: Optional[Mapping[str, Type[BaseVectorStore]]] = None,
    ) -> BaseVectorStore:
        backend = settings.vector_store.backend.lower()
        lookup = {key.lower(): value for key, value in (registry or cls._registry).items()}
        implementation = lookup.get(backend)
        if implementation is None:
            available = ", ".join(sorted(lookup)) or "<none>"
            raise ValueError(
                f"Unsupported vector store backend '{settings.vector_store.backend}'. "
                f"Available backends: {available}"
            )
        return implementation(settings.vector_store)

