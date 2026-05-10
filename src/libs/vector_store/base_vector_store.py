"""
Base vector store contract for pluggable storage backends.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, Optional, Sequence


class BaseVectorStore(ABC):
    def __init__(self, config: Any) -> None:
        self.config = config

    def validate_records(
        self,
        records: Iterable[Mapping[str, Any]],
    ) -> List[Mapping[str, Any]]:
        validated = list(records)
        for record in validated:
            missing = {"id", "text", "metadata"} - set(record.keys())
            if missing:
                raise ValueError(
                    f"Vector store record missing required field(s): {', '.join(sorted(missing))}"
                )
        return validated

    def validate_query_args(
        self,
        vector: Sequence[float],
        top_k: int,
        filters: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if not vector:
            raise ValueError("Query vector must be non-empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        if filters is not None and not isinstance(filters, Mapping):
            raise ValueError("filters must be a mapping when provided")

    @abstractmethod
    def upsert(
        self,
        records: Iterable[Mapping[str, Any]],
        trace: Optional[Any] = None,
    ) -> None:
        """Persist records into the store."""

    @abstractmethod
    def query(
        self,
        vector: Sequence[float],
        top_k: int,
        filters: Optional[Mapping[str, Any]] = None,
        trace: Optional[Any] = None,
    ) -> List[Mapping[str, Any]]:
        """Return top-k search results for the provided vector."""

