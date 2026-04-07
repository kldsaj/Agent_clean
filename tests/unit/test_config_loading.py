"""
Unit tests for configuration loading and validation.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.settings import (
    Settings,
    SettingsValidationError,
    load_settings,
    validate_settings,
    _dict_to_dataclass,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


_MINIMAL_VALID = {
    "llm": {"provider": "openai", "model": "gpt-4o-mini"},
    "embedding": {"provider": "openai", "model": "text-embedding-3-small"},
    "vector_store": {"backend": "chroma"},
    "retrieval": {"rerank_backend": "cross_encoder", "fusion_algorithm": "rrf"},
    "evaluation": {"backends": ["ragas"]},
    "observability": {"enabled": True, "logging": {"log_level": "INFO"}},
    "dashboard": {"enabled": True},
    "storage": {},
}


def _write_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)


# ─── validate_settings tests ───────────────────────────────────────────────────


@pytest.mark.unit
def test_validate_settings_passes_for_valid_data():
    validate_settings(_MINIMAL_VALID)  # Should not raise


@pytest.mark.unit
def test_validate_settings_missing_sections():
    data = dict(_MINIMAL_VALID)
    del data["llm"]
    del data["embedding"]
    with pytest.raises(SettingsValidationError) as exc_info:
        validate_settings(data)
    msg = str(exc_info.value)
    assert "llm" in msg or "embedding" in msg


@pytest.mark.unit
def test_validate_settings_invalid_rerank_backend():
    data = dict(_MINIMAL_VALID)
    data["retrieval"] = {"rerank_backend": "invalid_reranker", "fusion_algorithm": "rrf"}
    with pytest.raises(SettingsValidationError) as exc_info:
        validate_settings(data)
    assert "rerank_backend" in str(exc_info.value)


@pytest.mark.unit
def test_validate_settings_invalid_fusion_algorithm():
    data = dict(_MINIMAL_VALID)
    data["retrieval"] = {"rerank_backend": "none", "fusion_algorithm": "cosine"}
    with pytest.raises(SettingsValidationError) as exc_info:
        validate_settings(data)
    assert "fusion_algorithm" in str(exc_info.value)


@pytest.mark.unit
def test_validate_settings_case_insensitive_rerank():
    """rerank_backend validation should be case-insensitive."""
    data = dict(_MINIMAL_VALID)
    data["retrieval"] = {"rerank_backend": "CROSS_ENCODER", "fusion_algorithm": "RRF"}
    validate_settings(data)  # Should not raise


# ─── load_settings tests ──────────────────────────────────────────────────────


@pytest.mark.unit
def test_load_settings_success():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "settings.yaml"
        _write_yaml(config_path, _MINIMAL_VALID)

        settings = load_settings(str(config_path))

        assert isinstance(settings, Settings)
        assert settings.llm.provider == "openai"
        assert settings.llm.model == "gpt-4o-mini"
        assert settings.embedding.model == "text-embedding-3-small"
        assert settings.retrieval.rerank_backend == "cross_encoder"
        assert settings.retrieval.fusion_algorithm == "rrf"
        assert settings.observability.enabled is True


@pytest.mark.unit
def test_load_settings_absolute_path():
    """Absolute config_path is used as-is without path manipulation."""
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "settings.yaml"
        _write_yaml(config_path, _MINIMAL_VALID)

        settings = load_settings(str(config_path))  # absolute path

        assert isinstance(settings, Settings)
        assert settings.llm.provider == "openai"


@pytest.mark.unit
def test_load_settings_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_settings("/nonexistent/path/settings.yaml")


@pytest.mark.unit
def test_load_settings_missing_required_section():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "settings.yaml"
        _write_yaml(config_path, {"llm": {}})  # Only llm, missing others

        with pytest.raises(SettingsValidationError):
            load_settings(str(config_path))


@pytest.mark.unit
def test_load_settings_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "settings.yaml"
        config_path.write_text("", encoding="utf-8")

        with pytest.raises(SettingsValidationError) as exc_info:
            load_settings(str(config_path))
        assert "empty" in str(exc_info.value)


@pytest.mark.unit
def test_load_settings_extra_fields_ignored():
    """Extra top-level fields that are not dataclass fields are silently ignored."""
    data = dict(_MINIMAL_VALID)
    data["completely_unknown_field"] = {"foo": "bar"}
    data["llm"]["unknown_llm_field"] = "ignored"

    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "settings.yaml"
        _write_yaml(config_path, data)
        settings = load_settings(str(config_path))
        assert settings.llm.provider == "openai"  # Known field parsed correctly


# ─── _dict_to_dataclass tests ─────────────────────────────────────────────────


@pytest.mark.unit
def test_dict_to_dataclass_nested():
    from src.core.settings import LLMConfig
    data = {"provider": "azure", "model": "gpt-4o", "api_key": "secret"}
    result = _dict_to_dataclass(data, LLMConfig)
    assert isinstance(result, LLMConfig)
    assert result.provider == "azure"
    assert result.model == "gpt-4o"
    assert result.api_key == "secret"


@pytest.mark.unit
def test_dict_to_dataclass_defaults():
    """Fields not in the dict get their dataclass defaults."""
    from src.core.settings import LLMConfig
    data = {"provider": "openai"}
    result = _dict_to_dataclass(data, LLMConfig)
    assert result.model == "gpt-4o-mini"  # class default
    assert result.api_version == "2024-06-01"  # class default
