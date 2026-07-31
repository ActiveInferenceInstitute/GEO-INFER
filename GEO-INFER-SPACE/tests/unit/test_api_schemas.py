"""Regression tests for the SPACE FastAPI/Pydantic boundary."""

import asyncio

import pytest
import h3
from fastapi import HTTPException
from fastapi.testclient import TestClient
from geojson_pydantic import Feature, FeatureCollection, Point
from pydantic import ValidationError

from geo_infer_space.api.rest_api import app, h3_analysis_endpoint
from geo_infer_space.api.schemas import H3AnalysisRequest, InterpolationRequest
from geo_infer_space.models import DatabaseConfig, SpatialBounds, SpatialDataset
from geo_infer_space.models.data_models import SpatialMetadata


def test_space_api_app_builds_with_current_pydantic() -> None:
    assert len(app.routes) > 1


def test_space_http_surface_exposes_health_openapi_and_h3_contract() -> None:
    client = TestClient(app)

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy", "service": "GEO-INFER-SPACE"}

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "/api/v1/h3" in openapi.json()["paths"]
    assert "/api/v1/network" in openapi.json()["paths"]

    center = h3.latlng_to_cell(37.7749, -122.4194, 9)
    response = client.post(
        "/api/v1/h3",
        json={
            "operation": "grid_disk",
            "parameters": {"center_cell": center, "k": 1},
        },
    )
    assert response.status_code == 200
    assert set(response.json()["result"]["cells"]) == set(h3.grid_disk(center, 1))


def test_space_http_h3_invalid_cell_is_a_client_error() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/h3",
        json={
            "operation": "grid_disk",
            "parameters": {"center_cell": "not-a-cell", "k": 1},
        },
    )

    assert response.status_code == 400
    assert "not a valid H3 cell" in response.json()["detail"]


def test_space_http_vector_and_network_routes_return_json() -> None:
    client = TestClient(app)
    point = {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Point", "coordinates": [0, 0]},
    }
    buffer_response = client.post(
        "/api/v1/buffer",
        json={"data": point, "buffer_distance": 1},
    )
    assert buffer_response.status_code == 200
    assert buffer_response.json()["result"]["type"] == "FeatureCollection"

    network = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"length": 1},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[0, 0], [1, 0]],
                },
            },
            {
                "type": "Feature",
                "properties": {"length": 1},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[1, 0], [2, 0]],
                },
            },
        ],
    }
    network_response = client.post(
        "/api/v1/network",
        json={"network": network, "analysis_type": "connectivity"},
    )
    assert network_response.status_code == 200
    assert network_response.json()["result"]["is_connected"] is True


def test_interpolation_method_validation_remains_explicit() -> None:
    with pytest.raises(ValidationError, match="Method must be one of"):
        InterpolationRequest(
            points={"type": "FeatureCollection", "features": []},
            value_column="value",
            bounds=[0, 0, 1, 1],
            resolution=1,
            method="unsupported",
        )


def test_spatial_bounds_is_exported_from_models_package() -> None:
    assert SpatialBounds(minx=0, miny=0, maxx=1, maxy=1).area == 1


def test_database_schema_alias_is_compatible_with_config_files() -> None:
    config = DatabaseConfig(
        database="spatial", username="analyst", password="secret", schema="gis"
    )
    assert config.schema_name == "gis"
    assert config.model_dump(by_alias=True)["schema"] == "gis"


def test_single_feature_dataset_has_a_valid_degenerate_bounds() -> None:
    feature = Feature(
        type="Feature",
        geometry=Point(type="Point", coordinates=(1.0, 2.0)),
        properties={},
    )
    dataset = SpatialDataset(
        metadata=SpatialMetadata(name="point"),
        features=FeatureCollection(type="FeatureCollection", features=[feature]),
    )

    assert dataset.get_bounds().model_dump() == {
        "minx": 1.0,
        "miny": 2.0,
        "maxx": 1.0,
        "maxy": 2.0,
        "minz": None,
        "maxz": None,
    }


def test_h3_grid_disk_endpoint_uses_native_h3_and_optional_geometry() -> None:
    center = h3.latlng_to_cell(37.7749, -122.4194, 9)
    response = asyncio.run(
        h3_analysis_endpoint(
            H3AnalysisRequest(
                operation="grid_disk",
                parameters={"center_cell": center, "k": 1},
            )
        )
    )

    assert response.success is True
    assert set(response.result["cells"]) == set(h3.grid_disk(center, 1))


def test_h3_schema_accepts_direct_multipolygon_geometry() -> None:
    request = H3AnalysisRequest(
        operation="polygon_to_cells",
        geometry={
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-122.50, 37.70],
                        [-122.45, 37.70],
                        [-122.45, 37.75],
                        [-122.50, 37.75],
                        [-122.50, 37.70],
                    ]
                ],
                [
                    [
                        [-122.35, 37.75],
                        [-122.30, 37.75],
                        [-122.30, 37.80],
                        [-122.35, 37.80],
                        [-122.35, 37.75],
                    ]
                ],
            ],
        },
    )

    assert request.geometry is not None


def test_h3_invalid_cell_is_a_client_error_not_an_internal_error() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            h3_analysis_endpoint(
                H3AnalysisRequest(
                    operation="cell_to_boundary",
                    parameters={"center_cell": "not-a-cell"},
                )
            )
        )

    assert error.value.status_code == 400


def test_h3_compact_rejects_mixed_resolutions_and_boolean_k() -> None:
    client = TestClient(app)
    center = h3.latlng_to_cell(37.7749, -122.4194, 9)
    parent = h3.cell_to_parent(center, 8)

    mixed = client.post(
        "/api/v1/h3",
        json={
            "operation": "compact_cells",
            "parameters": {"cells": [center, parent]},
        },
    )
    boolean_k = client.post(
        "/api/v1/h3",
        json={
            "operation": "grid_disk",
            "parameters": {"center_cell": center, "k": True},
        },
    )

    assert mixed.status_code == 400
    assert "common resolution" in mixed.json()["detail"]
    assert boolean_k.status_code == 400


def test_h3_boundary_endpoint_returns_closed_geojson_ring() -> None:
    center = h3.latlng_to_cell(37.7749, -122.4194, 9)
    response = asyncio.run(
        h3_analysis_endpoint(
            H3AnalysisRequest(
                operation="cell_to_boundary",
                parameters={"center_cell": center},
            )
        )
    )
    ring = response.result["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]
    assert len(ring) == len(h3.cell_to_boundary(center)) + 1
