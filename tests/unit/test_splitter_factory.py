from __future__ import annotations

from src.core.settings import Settings
from src.libs.splitter.base_splitter import BaseSplitter
from src.libs.splitter.splitter_factory import SplitterFactory


class FakeSplitter(BaseSplitter):
    def split_text(self, text, trace=None):
        return text.split("|")


def test_splitter_factory_routes_backend_using_registry():
    settings = Settings()
    settings.ingestion.splitter_backend = "fake"

    splitter = SplitterFactory.create(settings, registry={"fake": FakeSplitter})

    assert isinstance(splitter, FakeSplitter)
    assert splitter.config is settings.ingestion


def test_splitter_factory_raises_for_unknown_backend():
    settings = Settings()
    settings.ingestion.splitter_backend = "missing"

    try:
        SplitterFactory.create(settings, registry={"fake": FakeSplitter})
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown backend")

    assert "missing" in message
    assert "fake" in message
