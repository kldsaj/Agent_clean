from __future__ import annotations

from src.core.settings import Settings
from src.libs.llm.base_llm import BaseLLM
from src.libs.llm.llm_factory import LLMFactory


class FakeLLM(BaseLLM):
    def chat(self, messages):
        return "ok"


def test_llm_factory_routes_provider_using_registry():
    settings = Settings()
    settings.llm.provider = "fake"

    llm = LLMFactory.create(settings, registry={"fake": FakeLLM})

    assert isinstance(llm, FakeLLM)
    assert llm.config is settings.llm


def test_llm_factory_raises_for_unknown_provider():
    settings = Settings()
    settings.llm.provider = "missing"

    try:
        LLMFactory.create(settings, registry={"fake": FakeLLM})
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown provider")

    assert "missing" in message
    assert "fake" in message
