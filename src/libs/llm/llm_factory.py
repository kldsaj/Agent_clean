"""
Factory for constructing LLM implementations from settings.
"""
from __future__ import annotations

from typing import Mapping, Optional, Type

from src.core.settings import Settings
from src.libs.llm.base_llm import BaseLLM


class LLMFactory:
    _registry: dict[str, Type[BaseLLM]] = {}

    @classmethod
    def register(cls, provider: str, implementation: Type[BaseLLM]) -> None:
        cls._registry[provider.lower()] = implementation

    @classmethod
    def create(
        cls,
        settings: Settings,
        registry: Optional[Mapping[str, Type[BaseLLM]]] = None,
    ) -> BaseLLM:
        provider = settings.llm.provider.lower()
        lookup = {key.lower(): value for key, value in (registry or cls._registry).items()}
        implementation = lookup.get(provider)
        if implementation is None:
            available = ", ".join(sorted(lookup)) or "<none>"
            raise ValueError(
                f"Unsupported llm provider '{settings.llm.provider}'. "
                f"Available providers: {available}"
            )
        return implementation(settings.llm)

