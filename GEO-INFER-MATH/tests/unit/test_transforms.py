"""
Tests for the transforms module.
"""

import numpy as np
import pytest
from geo_infer_math.core.transforms import (
    CoordinateTransformer, geographic_to_projected, projected_to_geographic,
    utm_zone_from_lon_lat, utm_central_meridian, datum_transformation,
    affine_transformation, rotation_matrix_2d, rotation_matrix_3d,
    scale_matrix_2d, scale_matrix_3d, shear_matrix_2d
)

class TestCoordinateTransformer:
    """Test coordinate transformation functionality."""

    def test_wgs84_to_utm_transformation(self):
        """Test WGS84 to UTM transformation."""
        transformer = CoordinateTransformer('EPSG:4326', 'UTM')

        # Test point in northern hemisphere
        result = transformer.transform_point((10.0, 50.0, None))
        assert len(result) == 3
        assert result[0] > 0  # Easting should be positive
        assert result[1] > 0  # Northing should be positive

        # Test point in southern hemisphere
        result_south = transformer.transform_point((10.0, -50.0, None))
        assert result_south[0] > 0
        assert result_south[1] > 0

    def test_utm_to_wgs84_transformation(self):
        """Test UTM to WGS84 transformation."""
        transformer = CoordinateTransformer('UTM', 'EPSG:4326')

        # Test UTM point
        easting, northing = 500000, 5500000
        result = transformer.transform_point((easting, northing, None))

        assert -180 <= result[0] <= 180  # Longitude
        assert -90 <= result[1] <= 90    # Latitude

    def test_geographic_to_web_mercator(self):
        """Test geographic to Web Mercator transformation."""
        transformer = CoordinateTransformer('EPSG:4326', 'EPSG:3857')

        # Test point
        result = transformer.transform_point((10.0, 50.0, None))
        assert result[0] != 10.0  # Should be different from input
        assert result[1] != 50.0

    def test_web_mercator_to_geographic(self):
        """Test Web Mercator to geographic transformation."""
        transformer = CoordinateTransformer('EPSG:3857', 'EPSG:4326')

        # Test point
        x, y = 1113194.91, 6446275.84  # Web Mercator coordinates for (10, 50)
        result = transformer.transform_point((x, y, None))

        assert abs(result[0] - 10.0) < 0.1  # Should be close to original longitude
        assert abs(result[1] - 50.0) < 0.1  # Should be close to original latitude

    def test_transform_points_batch(self):
        """Test batch transformation of multiple points."""
        transformer = CoordinateTransformer('EPSG:4326', 'UTM')

        points = np.array([
            [10.0, 50.0],
            [11.0, 51.0],
            [12.0, 52.0]
        ])

        result = transformer.transform_points(points)

        assert result.shape == (3, 2)  # Should maintain 2D shape
        assert np.all(result[:, 0] > 0)  # All eastings positive
        assert np.all(result[:, 1] > 0)  # All northings positive

    def test_invalid_crs(self):
        """Test handling of invalid CRS specifications."""
        with pytest.raises(ValueError):
            CoordinateTransformer('INVALID', 'EPSG:4326')

class TestGeographicProjection:
    """Test geographic to projected coordinate transformations."""

    def test_geographic_to_utm(self):
        """Test geographic to UTM projection."""
        x, y = geographic_to_projected(10.0, 50.0, 'utm')

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert x > 0
        assert y > 0

    def test_projected_to_geographic(self):
        """Test projected to geographic transformation."""
        lon, lat = projected_to_geographic(500000, 5500000, 'utm')

        assert isinstance(lon, float)
        assert isinstance(lat, float)
        assert -180 <= lon <= 180
        assert -90 <= lat <= 90

    def test_invalid_projection(self):
        """Test handling of invalid projection."""
        with pytest.raises(ValueError):
            geographic_to_projected(10.0, 50.0, 'invalid')

class TestUTMUtilities:
    """Test UTM utility functions."""

    def test_utm_zone_calculation(self):
        """Test UTM zone calculation."""
        # Test various longitudes
        zone, hemisphere = utm_zone_from_lon_lat(-177, 45)  # Westernmost
        assert zone == 1
        assert hemisphere == 'N'

        zone, hemisphere = utm_zone_from_lon_lat(177, 45)  # Easternmost
        assert zone == 60
        assert hemisphere == 'N'

        zone, hemisphere = utm_zone_from_lon_lat(10, -45)  # Southern hemisphere
        assert zone == 32  # Longitude 10° is in UTM zone 32
        assert hemisphere == 'S'

    def test_utm_central_meridian(self):
        """Test UTM central meridian calculation."""
        # Zone 30 central meridian should be 0°
        meridian = utm_central_meridian(30)
        assert meridian == -3  # Zone 30: -3° to 3°

        # Zone 31 central meridian should be 3°
        meridian = utm_central_meridian(31)
        assert meridian == 3

class TestDatumTransformation:
    """Test datum transformation functionality."""

    def test_wgs84_to_nad83(self):
        """Test WGS84 to NAD83 transformation."""
        x, y, z = datum_transformation(1000000, 2000000, 100, 'WGS84', 'NAD83')

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)

    def test_nad83_to_wgs84(self):
        """Test NAD83 to WGS84 transformation."""
        x, y, z = datum_transformation(1000000, 2000000, 100, 'NAD83', 'WGS84')

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)

class TestAffineTransformations:
    """Test affine transformation functions."""

    def test_affine_transformation_2d(self):
        """Test 2D affine transformation."""
        points = np.array([[1, 2], [3, 4], [5, 6]])
        matrix = np.array([[2, 0], [0, 2]])  # Scaling by 2
        translation = np.array([10, 20])

        result = affine_transformation(points, matrix, translation)

        expected = np.array([[12, 24], [16, 28], [20, 32]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_affine_transformation_3d(self):
        """Test 3D affine transformation."""
        points = np.array([[1, 2, 3], [4, 5, 6]])
        matrix = np.eye(3)  # Identity matrix
        translation = np.array([10, 20, 30])

        result = affine_transformation(points, matrix, translation)

        expected = np.array([[11, 22, 33], [14, 25, 36]])
        np.testing.assert_array_almost_equal(result, expected)

class TestTransformationMatrices:
    """Test transformation matrix generation."""

    def test_rotation_matrix_2d(self):
        """Test 2D rotation matrix generation."""
        angle = np.pi / 4  # 45 degrees
        matrix = rotation_matrix_2d(angle)

        assert matrix.shape == (2, 2)
        assert abs(matrix[0, 0] - np.cos(angle)) < 1e-10
        assert abs(matrix[0, 1] - (-np.sin(angle))) < 1e-10
        assert abs(matrix[1, 0] - np.sin(angle)) < 1e-10
        assert abs(matrix[1, 1] - np.cos(angle)) < 1e-10

    def test_rotation_matrix_3d(self):
        """Test 3D rotation matrix generation."""
        angle = np.pi / 2
        matrix_x = rotation_matrix_3d('x', angle)
        matrix_y = rotation_matrix_3d('y', angle)
        matrix_z = rotation_matrix_3d('z', angle)

        assert matrix_x.shape == (3, 3)
        assert matrix_y.shape == (3, 3)
        assert matrix_z.shape == (3, 3)

        # Test that matrices are orthogonal (Q^T * Q = I)
        np.testing.assert_array_almost_equal(matrix_x.T @ matrix_x, np.eye(3))
        np.testing.assert_array_almost_equal(matrix_y.T @ matrix_y, np.eye(3))
        np.testing.assert_array_almost_equal(matrix_z.T @ matrix_z, np.eye(3))

    def test_scale_matrix_2d(self):
        """Test 2D scaling matrix generation."""
        sx, sy = 2.0, 3.0
        matrix = scale_matrix_2d(sx, sy)

        expected = np.array([[2, 0], [0, 3]])
        np.testing.assert_array_equal(matrix, expected)

    def test_scale_matrix_3d(self):
        """Test 3D scaling matrix generation."""
        sx, sy, sz = 2.0, 3.0, 4.0
        matrix = scale_matrix_3d(sx, sy, sz)

        expected = np.array([[2, 0, 0], [0, 3, 0], [0, 0, 4]])
        np.testing.assert_array_equal(matrix, expected)

    def test_shear_matrix_2d(self):
        """Test 2D shear matrix generation."""
        shx, shy = 1.0, 2.0
        matrix = shear_matrix_2d(shx, shy)

        expected = np.array([[1, 1], [2, 1]])
        np.testing.assert_array_equal(matrix, expected)

    def test_invalid_axis_rotation(self):
        """Test handling of invalid rotation axis."""
        with pytest.raises(ValueError):
            rotation_matrix_3d('invalid', np.pi/2)
