"""Pydantic v2 compatibility base for legacy LOG schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as _PydanticBaseModel, ConfigDict
from pydantic._internal._model_construction import ModelMetaclass


class _LegacyConfigMetaclass(ModelMetaclass):
    """Translate legacy ``Config.schema_extra`` before Pydantic builds a model."""

    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any):
        legacy_config = namespace.pop("Config", None)
        if legacy_config is not None:
            schema_extra = getattr(legacy_config, "schema_extra", None)
            namespace["model_config"] = ConfigDict(
                json_schema_extra=schema_extra
            ) if schema_extra is not None else ConfigDict()
        return super().__new__(mcls, name, bases, namespace, **kwargs)


class BaseModel(_PydanticBaseModel, metaclass=_LegacyConfigMetaclass):
    """Pydantic v2 model that accepts the module's historical Config blocks."""
