"""
Unit tests for validation utilities.
"""

import pytest

from geo_infer_cog.utils.validation import (
    validate_spatial_data,
    validate_geometry,
    validate_point_coordinates,
    validate_linestring_coordinates,
    validate_polygon_coordinates,
    validate_cognitive_model,
    validate_user_profile,
    validate_configuration,
    do_edges_intersect,
    check_data_completeness,
    generate_default_config,
)


class TestGeometryValidation:
    """Test geometry validation functions."""

    def test_valid_point(self) -> None:
        result = validate_point_coordinates([-74.0060, 40.7128])
        assert result['valid'] is True
        assert result['coordinate_ranges']['longitude'] == -74.0060

    def test_invalid_longitude(self) -> None:
        result = validate_point_coordinates([200.0, 40.0])
        assert result['valid'] is False
        assert any('Longitude' in e for e in result['errors'])

    def test_invalid_latitude(self) -> None:
        result = validate_point_coordinates([0.0, 100.0])
        assert result['valid'] is False
        assert any('Latitude' in e for e in result['errors'])

    def test_too_few_coordinates(self) -> None:
        result = validate_point_coordinates([10.0])
        assert result['valid'] is False

    def test_valid_linestring(self) -> None:
        coords = [[0.0, 0.0], [1.0, 1.0], [2.0, 0.0]]
        result = validate_linestring_coordinates(coords)
        assert result['valid'] is True
        assert result['coordinate_count'] == 3
        assert len(result['segment_lengths']) == 2

    def test_degenerate_linestring_segment_warns(self) -> None:
        coords = [[0.0, 0.0], [0.0, 0.0], [1.0, 1.0]]
        result = validate_linestring_coordinates(coords)
        assert any('Degenerate' in w for w in result['warnings'])

    def test_valid_polygon(self) -> None:
        coords = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        result = validate_polygon_coordinates(coords)
        assert result['valid'] is True
        assert result['ring_count'] == 1

    def test_validate_geometry_point(self) -> None:
        geom = {'type': 'Point', 'coordinates': [-73.0, 40.0]}
        result = validate_geometry(geom)
        assert result['valid'] is True
        assert result['geometry_type'] == 'Point'

    def test_validate_geometry_missing_type(self) -> None:
        result = validate_geometry({'coordinates': [0, 0]})
        assert result['valid'] is False

    def test_validate_geometry_missing_coordinates(self) -> None:
        result = validate_geometry({'type': 'Point'})
        assert result['valid'] is False


class TestEdgeIntersection:
    """Test edge intersection detection."""

    def test_intersecting_edges(self) -> None:
        assert do_edges_intersect([0, 0], [1, 1], [0, 1], [1, 0]) is True

    def test_non_intersecting_edges(self) -> None:
        assert do_edges_intersect([0, 0], [1, 0], [0, 1], [1, 1]) is False


class TestSpatialDataValidation:
    """Test high-level spatial data validation."""

    def test_valid_spatial_data(self) -> None:
        data = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [-73.0, 40.0]},
        }
        result = validate_spatial_data(data)
        assert result['valid'] is True

    def test_missing_type_field(self) -> None:
        result = validate_spatial_data({'geometry': {'type': 'Point', 'coordinates': [0, 0]}})
        assert result['valid'] is False
        assert any('Missing required field' in e for e in result['errors'])


class TestCognitiveModelValidation:
    """Test cognitive model configuration validation."""

    def test_valid_config(self) -> None:
        config = {
            'attention_capacity': 0.8,
            'focus_radius': 0.5,
            'saliency_threshold': 0.3,
        }
        result = validate_cognitive_model(config, model_type='perception')
        assert result['valid'] is True

    def test_out_of_range_parameter(self) -> None:
        config = {'attention_capacity': 2.0}
        result = validate_cognitive_model(config)
        assert result['valid'] is False
        assert any('out of range' in e for e in result['errors'])

    def test_reasoning_model_invalid_type(self) -> None:
        config = {'reasoning_type': 'magic'}
        result = validate_cognitive_model(config, model_type='reasoning')
        assert result['valid'] is False


class TestUserProfileValidation:
    """Test user profile validation."""

    def test_valid_profile(self) -> None:
        result = validate_user_profile({
            'user_id': 'u1',
            'spatial_expertise': 0.7,
            'cognitive_style': 'visualizer',
            'cognitive_load_preference': 'low',
        })
        assert result['valid'] is True

    def test_missing_user_id(self) -> None:
        result = validate_user_profile({'spatial_expertise': 0.5})
        assert result['valid'] is False

    def test_expertise_out_of_range(self) -> None:
        result = validate_user_profile({'user_id': 'u1', 'spatial_expertise': 1.5})
        assert result['valid'] is False

    def test_invalid_categorical_field(self) -> None:
        result = validate_user_profile({
            'user_id': 'u1',
            'cognitive_style': 'telepathic',
        })
        assert result['valid'] is False


class TestConfigurationValidation:
    """Test module configuration validation."""

    def test_generate_default_config_cog(self) -> None:
        config = generate_default_config('cog')
        assert 'core' in config
        assert 'models' in config
        assert 'api' in config
        assert config['core']['cognitive_framework'] == 'bayesian_attention'

    def test_data_completeness_score(self) -> None:
        data = {
            'geometry': {'type': 'Point', 'coordinates': [0, 0]},
            'properties': {'id': 'test', 'name': 'Test Place'},
        }
        result = check_data_completeness(data)
        assert result['completeness_score'] > 0.0
