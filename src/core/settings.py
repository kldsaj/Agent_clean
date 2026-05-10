"""
Settings — Configuration loading and validation.

Loads config/settings.yaml, parses it into typed dataclasses,
and validates that required fields are present.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, fields as _dataclass_fields
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# ─── Dataclasses ────────────────────────────────────────────────────────────


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    # azure-specific
    endpoint: str = ""
    api_version: str = "2024-06-01"
    deployment_name: str = ""


@dataclass
class EmbeddingConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    batch_size: int = 100
    api_key: str = ""


@dataclass
class VisionLLMConfig:
    provider: str = "azure"
    model: str = "gpt-4o"
    api_key: str = ""


@dataclass
class VectorStoreConfig:
    backend: str = "chroma"
    persist_directory: str = "./data/db/chroma"
    collection_name: str = "default"


@dataclass
class RetrievalConfig:
    sparse_backend: str = "bm25"
    top_k_dense: int = 20
    top_k_sparse: int = 20
    fusion_algorithm: str = "rrf"
    rerank_backend: str = "cross_encoder"
    top_k_final: int = 5


@dataclass
class IngestionConfig:
    splitter_backend: str = "recursive"
    chunk_size: int = 512
    chunk_overlap: int = 50
    batch_size: int = 50
    max_workers: int = 4


@dataclass
class EvaluationConfig:
    backends: List[str] = field(default_factory=lambda: ["ragas", "custom"])


@dataclass
class LoggingConfig:
    log_file: str = "logs/traces.jsonl"
    log_level: str = "INFO"


@dataclass
class ObservabilityConfig:
    enabled: bool = True
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    detail_level: str = "standard"


@dataclass
class DashboardConfig:
    enabled: bool = True
    port: int = 8501
    traces_dir: str = "./logs"
    auto_refresh: bool = True
    refresh_interval: int = 5


@dataclass
class StorageConfig:
    data_dir: str = "./data"
    documents_dir: str = "./data/documents"
    images_dir: str = "./data/images"
    db_dir: str = "./data/db"
    cache_dir: str = "./cache"
    ingestion_history_db: str = "./data/db/ingestion_history.db"
    image_index_db: str = "./data/db/image_index.db"


@dataclass
class Settings:
    """Root settings container."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vision_llm: VisionLLMConfig = field(default_factory=VisionLLMConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


# ─── Validation ──────────────────────────────────────────────────────────────


class SettingsValidationError(ValueError):
    """Raised when required configuration fields are missing or invalid."""

    pass


# Required top-level section names
_REQUIRED_SECTIONS = frozenset([
    "llm",
    "embedding",
    "vector_store",
    "retrieval",
    "evaluation",
    "observability",
    "dashboard",
    "storage",
])


def validate_settings(data: Dict[str, Any]) -> None:
    """
    Validate that all required sections and fields are present.

    Raises SettingsValidationError with a clear message indicating
    which field is missing and what the expected path looks like.
    """
    missing: List[str] = []

    for section in _REQUIRED_SECTIONS:
        if section not in data:
            missing.append(section)
        elif isinstance(data[section], dict) and not data[section]:
            # Section present but empty — still accept it; defaults will fill in
            pass

    if missing:
        raise SettingsValidationError(
            f"Missing required configuration section(s): {', '.join(missing)}. "
            f"Please ensure config/settings.yaml contains all of: {', '.join(sorted(_REQUIRED_SECTIONS))}"
        )

    # Semantic validation: rerank_backend must be one of the allowed values
    rerank_backend = (
        data.get("retrieval", {}).get("rerank_backend", "cross_encoder")
    )
    allowed_rerank = frozenset(["none", "cross_encoder", "llm"])
    if rerank_backend.lower() not in allowed_rerank:
        raise SettingsValidationError(
            f"Invalid rerank_backend '{rerank_backend}'. "
            f"Must be one of: {', '.join(sorted(allowed_rerank))}"
        )

    # fusion_algorithm must be one of the allowed values
    fusion = data.get("retrieval", {}).get("fusion_algorithm", "rrf")
    allowed_fusion = frozenset(["rrf", "weighted_sum"])
    if fusion.lower() not in allowed_fusion:
        raise SettingsValidationError(
            f"Invalid fusion_algorithm '{fusion}'. "
            f"Must be one of: {', '.join(sorted(allowed_fusion))}"
        )


def _dict_to_dataclass(data: Dict[str, Any], cls: type) -> Any:
    """Recursively convert a nested dict to a matching dataclass instance.

    Uses typing.get_type_hints() to resolve forward-reference string
    annotations (required when 'from __future__ import annotations' is used).
    """
    import dataclasses
    import typing

    # get_type_hints resolves string annotations like "LLMConfig" -> LLMConfig class
    hints = typing.get_type_hints(cls)

    kwargs: Dict[str, Any] = {}
    for key, value in data.items():
        if key not in hints:
            continue

        field_type = hints[key]
        origin = getattr(field_type, "__origin__", None)

        if origin is list:
            item_type = field_type.__args__[0]
            item_origin = getattr(item_type, "__origin__", None)
            kwargs[key] = [
                _dict_to_dataclass(v, item_type)
                if (isinstance(v, dict) and dataclasses.is_dataclass(item_type))
                else v
                for v in value
            ]
        elif dataclasses.is_dataclass(field_type) and isinstance(value, dict):
            # Nested dataclass: recurse
            kwargs[key] = _dict_to_dataclass(value, field_type)
        else:
            kwargs[key] = value

    return cls(**kwargs)


def load_settings(config_path: str | Path = "config/settings.yaml") -> Settings:
    """
    Load and validate settings from a YAML configuration file.

    Args:
        config_path: Path to config/settings.yaml. Relative paths are resolved
            from the project root (directory containing main.py).

    Returns:
        A validated Settings instance.

    Raises:
        FileNotFoundError: config_path does not exist.
        SettingsValidationError: A required section or field is missing / invalid.
        yaml.YAMLError: The YAML file is malformed.
    """
    config_path = Path(config_path)

    # Resolve relative paths from the project root (one level above src/)
    if not config_path.is_absolute():
        # Resolve from project root: main.py lives at <project_root>/main.py
        # settings.py is at <project_root>/src/core/settings.py
        # So project_root = settings.py parent.parent.parent
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / config_path

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if raw is None:
        raise SettingsValidationError(
            f"Configuration file is empty: {config_path}"
        )

    # Validate required structure
    validate_settings(raw)

    # Parse into typed Settings dataclass
    settings = _dict_to_dataclass(raw, Settings)

    # Environment variable expansion for api_key fields
    if not settings.llm.api_key:
        settings.llm.api_key = os.environ.get("OPENAI_API_KEY", "")

    return settings
