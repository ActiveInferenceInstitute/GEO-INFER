"""Regression tests for the SPACE FastAPI/Pydantic boundary."""

import pytest
from geojson_pydantic import Feature, FeatureCollection, Point
from pydantic import ValidationError

from geo_infer_space.api.rest_api import app
from geo_infer_space.api.schemas import InterpolationRequest
from geo_infer_space.models import DatabaseConfig, SpatialBounds, SpatialDataset
from geo_infer_space.models.data_models import SpatialMetadata


def test_space_api_app_builds_with_current_pydantic() -> None:
    assert len(app.routes) > 1


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
