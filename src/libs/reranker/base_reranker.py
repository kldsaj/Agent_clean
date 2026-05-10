"""
Base reranker contract for pluggable reranking backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Sequence


class BaseReranker(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: Sequence[Any],
        trace: Optional[Any] = None,
    ) -> List[Any]:
        """Return candidates ordered by relevance."""

