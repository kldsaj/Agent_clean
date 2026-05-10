"""
Base splitter contract for pluggable chunking backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class BaseSplitter(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    @abstractmethod
    def split_text(self, text: str, trace: Optional[Any] = None) -> List[str]:
        """Split text into ordered text fragments."""

