"""
Base LLM contract for pluggable chat backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class BaseLLM(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    def chat(self, messages: Iterable[dict[str, Any]]) -> str:
        """Return a text response for the provided chat messages."""

