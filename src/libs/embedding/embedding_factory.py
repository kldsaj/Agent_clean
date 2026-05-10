"""
Factory for constructing embedding implementations from settings.
"""
from __future__ import annotations

from typing import Mapping, Optional, Type

from src.core.settings import Settings
from src.libs.embedding.base_embedding import BaseEmbedding


class EmbeddingFactory:
    _registry: dict[str, Type[BaseEmbedding]] = {}

    @classmethod
    def register(cls, provider: str, implementation: Type[BaseEmbedding]) -> None:
        cls._registry[provider.lower()] = implementation

    @classmethod
    def create(
        cls,
        settings: Settings,
        registry: Optional[Mapping[str, Type[BaseEmbedding]]] = None,
    ) -> BaseEmbedding:
        provider = settings.embedding.provider.lower()
        lookup = {key.lower(): value for key, value in (registry or cls._registry).items()}
        implementation = lookup.get(provider)
        if implementation is None:
            available = ", ".join(sorted(lookup)) or "<none>"
            raise ValueError(
                f"Unsupported embedding provider '{settings.embedding.provider}'. "
                f"Available providers: {available}"
            )
        return implementation(settings.embedding)

