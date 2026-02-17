"""Tests for API custom exceptions."""

import pytest
from geo_infer_api.core.exceptions import (
    APIError,
    ValidationError,
    NotFoundError,
    ConflictError,
    GeometryError,
    ProcessingError,
    BadRequestError,
)


class TestAPIError:
    def test_base_error(self):
        err = APIError(status_code=500, detail="Server error")
        assert err.status_code == 500
        assert err.error_code == "API_500"
        result = err.to_dict()
        assert result["error"]["code"] == "API_500"
        assert result["error"]["message"] == "Server error"

    def test_custom_error_code(self):
        err = APIError(status_code=400, detail="Bad", error_code="CUSTOM")
        assert err.error_code == "CUSTOM"

    def test_additional_info(self):
        err = APIError(400, "Bad", additional_info={"field": "name"})
        result = err.to_dict()
        assert result["error"]["field"] == "name"


class TestValidationError:
    def test_validation_error(self):
        err = ValidationError("Invalid email", field="email", value="bad")
        assert err.status_code == 422
        result = err.to_dict()
        assert result["error"]["field"] == "email"


class TestNotFoundError:
    def test_not_found(self):
        err = NotFoundError("User", "123")
        assert err.status_code == 404
        assert "123" in err.detail

    def test_not_found_no_id(self):
        err = NotFoundError("Feature")
        assert "not found" in err.detail


class TestConflictError:
    def test_conflict(self):
        err = ConflictError("User", "duplicate email", "u123")
        assert err.status_code == 409
        result = err.to_dict()
        assert result["error"]["conflict_reason"] == "duplicate email"


class TestGeometryError:
    def test_geometry_error(self):
        err = GeometryError("Invalid polygon", geometry_type="Polygon", operation="buffer")
        assert err.status_code == 400
        result = err.to_dict()
        assert result["error"]["geometry_type"] == "Polygon"


class TestProcessingError:
    def test_processing_error(self):
        err = ProcessingError("Timeout", operation="intersection", processing_stage="compute")
        assert err.status_code == 500
        result = err.to_dict()
        assert result["error"]["operation"] == "intersection"


class TestBadRequestError:
    def test_bad_request(self):
        err = BadRequestError("Missing param", field="bbox")
        assert err.status_code == 400
        result = err.to_dict()
        assert result["error"]["field"] == "bbox"
