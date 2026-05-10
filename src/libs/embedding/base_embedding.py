"""
Base embedding contract for pluggable embedding backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Sequence


class BaseEmbedding(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    def embed(
        self,
        texts: Sequence[str],
        trace: Optional[Any] = None,
    ) -> List[List[float]]:
        """Return dense vectors for the provided texts."""

