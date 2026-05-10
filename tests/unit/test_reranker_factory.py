from __future__ import annotations

from src.core.settings import Settings
from src.libs.reranker.base_reranker import BaseReranker
from src.libs.reranker.reranker_factory import NoneReranker, RerankerFactory


class FakeReranker(BaseReranker):
    def rerank(self, query, candidates, trace=None):
        return list(reversed(candidates))


def test_reranker_factory_returns_none_reranker_for_none_backend():
    settings = Settings()
    settings.retrieval.rerank_backend = "none"

    reranker = RerankerFactory.create(settings)

    assert isinstance(reranker, NoneReranker)
    assert reranker.rerank("q", ["a", "b"]) == ["a", "b"]


def test_reranker_factory_routes_backend_using_registry():
    settings = Settings()
    settings.retrieval.rerank_backend = "fake"

    reranker = RerankerFactory.create(settings, registry={"fake": FakeReranker})

    assert isinstance(reranker, FakeReranker)
    assert reranker.config is settings.retrieval


def test_reranker_factory_raises_for_unknown_backend():
    settings = Settings()
    settings.retrieval.rerank_backend = "missing"

    try:
        RerankerFactory.create(settings, registry={"fake": FakeReranker})
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown backend")

    assert "missing" in message
    assert "fake" in message
