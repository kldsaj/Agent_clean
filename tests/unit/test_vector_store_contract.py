from __future__ import annotations

import pytest

from src.core.settings import Settings
from src.libs.vector_store.base_vector_store import BaseVectorStore
from src.libs.vector_store.vector_store_factory import VectorStoreFactory


class FakeVectorStore(BaseVectorStore):
    def __init__(self, config):
        super().__init__(config)
        self.records = []

    def upsert(self, records, trace=None):
        validated = self.validate_records(records)
        self.records.extend(validated)

    def query(self, vector, top_k, filters=None, trace=None):
        self.validate_query_args(vector, top_k, filters)
        return [
            {"id": record["id"], "score": 1.0, "metadata": record["metadata"]}
            for record in self.records[:top_k]
        ]


def test_vector_store_factory_routes_backend_using_registry():
    settings = Settings()
    settings.vector_store.backend = "fake"

    store = VectorStoreFactory.create(settings, registry={"fake": FakeVectorStore})

    assert isinstance(store, FakeVectorStore)
    assert store.config is settings.vector_store


def test_vector_store_contract_validates_record_shape():
    store = FakeVectorStore(Settings().vector_store)

    with pytest.raises(ValueError):
        store.upsert([{"id": "chunk-1", "metadata": {}}])


def test_vector_store_contract_validates_query_args():
    store = FakeVectorStore(Settings().vector_store)

    with pytest.raises(ValueError):
        store.query(vector=[], top_k=0)
