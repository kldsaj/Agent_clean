from __future__ import annotations

from src.core.settings import Settings
from src.libs.embedding.base_embedding import BaseEmbedding
from src.libs.embedding.embedding_factory import EmbeddingFactory


class FakeEmbedding(BaseEmbedding):
    def embed(self, texts, trace=None):
        return [[float(len(text))] for text in texts]


def test_embedding_factory_routes_provider_using_registry():
    settings = Settings()
    settings.embedding.provider = "fake"

    embedding = EmbeddingFactory.create(settings, registry={"fake": FakeEmbedding})

    assert isinstance(embedding, FakeEmbedding)
    assert embedding.config is settings.embedding


def test_embedding_factory_raises_for_unknown_provider():
    settings = Settings()
    settings.embedding.provider = "missing"

    try:
        EmbeddingFactory.create(settings, registry={"fake": FakeEmbedding})
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown provider")

    assert "missing" in message
    assert "fake" in message
