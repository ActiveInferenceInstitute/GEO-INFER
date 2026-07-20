"""Shared Pydantic model base for GEO-INFER-LOG schemas."""

from pydantic import BaseModel as _PydanticBaseModel


class BaseModel(_PydanticBaseModel):
    """Common model base used by logistics request and response schemas."""
