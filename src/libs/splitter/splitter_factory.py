"""
Factory for constructing splitter implementations from settings.
"""
from __future__ import annotations

from typing import Mapping, Optional, Type

from src.core.settings import Settings
from src.libs.splitter.base_splitter import BaseSplitter


class SplitterFactory:
    _registry: dict[str, Type[BaseSplitter]] = {}

    @classmethod
    def register(cls, backend: str, implementation: Type[BaseSplitter]) -> None:
        cls._registry[backend.lower()] = implementation

    @classmethod
    def create(
        cls,
        settings: Settings,
        registry: Optional[Mapping[str, Type[BaseSplitter]]] = None,
    ) -> BaseSplitter:
        backend = settings.ingestion.splitter_backend.lower()
        lookup = {key.lower(): value for key, value in (registry or cls._registry).items()}
        implementation = lookup.get(backend)
        if implementation is None:
            available = ", ".join(sorted(lookup)) or "<none>"
            raise ValueError(
                f"Unsupported splitter backend '{settings.ingestion.splitter_backend}'. "
                f"Available backends: {available}"
            )
        return implementation(settings.ingestion)

