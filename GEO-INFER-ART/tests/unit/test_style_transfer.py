#!/usr/bin/env python
"""
Unit tests for the StyleTransfer class in geo_infer_art.core.aesthetics.style_transfer.
"""

import os
import tempfile
import unittest
import numpy as np
import pytest
import geopandas as gpd
from shapely.geometry import Polygon
from PIL import Image

from geo_infer_art.core.aesthetics.style_transfer import StyleTransfer


class TestStyleTransfer(unittest.TestCase):
    """Test suite for the StyleTransfer class."""

    def setUp(self):
        """Set up test fixtures."""
        self._tmpdir = tempfile.TemporaryDirectory()
        self.test_dir = self._tmpdir.name

        # Create a simple test image as content
        self.content_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Light gray
        self.content_image[30:70, 30:70] = [100, 100, 100]  # Dark gray square
        self.content_image_path = os.path.join(self.test_dir, "content.png")
        Image.fromarray(self.content_image).save(self.content_image_path)

        # Create a simple test image as style
        self.style_image = np.ones((100, 100, 3), dtype=np.uint8) * 150  # Gray
        self.style_image[20:40, 20:80] = [200, 50, 50]  # Red bar
        self.style_image[60:80, 20:80] = [50, 200, 50]  # Green bar
        self.style_image_path = os.path.join(self.test_dir, "style.png")
        Image.fromarray(self.style_image).save(self.style_image_path)

        # Create a simple GeoDataFrame for testing
        geometries = [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        ]
        self.geo_data = gpd.GeoDataFrame(
            {"name": ["Region A", "Region B"]}, geometry=geometries, crs="EPSG:4326"
        )

    def tearDown(self):
        """Clean up after tests."""
        self._tmpdir.cleanup()

    def test_init_with_content_and_style(self):
        """Test initialization with content and style images."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            self.fail("TensorFlow is required by the declared ART test dependencies")

        style_transfer = StyleTransfer(
            style_image=self.style_image_path, content_image=self.content_image_path
        )

        self.assertIsNotNone(style_transfer.style_image)
        self.assertIsNotNone(style_transfer.content_image)

    def test_get_predefined_style_path(self):
        """Test getting a predefined style path."""
        # Test a valid predefined style
        style_resource = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "src",
            "geo_infer_art",
            "data",
            "styles",
            StyleTransfer.PREDEFINED_STYLES["watercolor"],
        )
        if os.path.isfile(style_resource):
            style_path = StyleTransfer.get_predefined_style_path("watercolor")
            self.assertTrue(os.path.exists(style_path))
        else:
            with self.assertRaises(FileNotFoundError):
                StyleTransfer.get_predefined_style_path("watercolor")

        # Test an invalid style name
        with self.assertRaises(ValueError):
            StyleTransfer.get_predefined_style_path("nonexistent_style")

    def test_load_style_image(self):
        """Test loading a style image."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            self.fail("TensorFlow is required by the declared ART test dependencies")

        style_transfer = StyleTransfer()

        # Test loading from file path
        style_transfer.load_style_image(self.style_image_path)
        self.assertIsNotNone(style_transfer.style_image)

        # Test loading from numpy array
        style_transfer.load_style_image(self.style_image)
        self.assertIsNotNone(style_transfer.style_image)

        # Test loading from PIL Image
        pil_image = Image.fromarray(self.style_image)
        style_transfer.load_style_image(pil_image)
        self.assertIsNotNone(style_transfer.style_image)

    @pytest.mark.slow
    def test_apply_style_transfer(self):
        """Test applying style transfer to geospatial data."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            self.fail("TensorFlow is required by the declared ART test dependencies")

        # Test with a real fixture image; predefined package assets are optional.
        try:
            styled_image = StyleTransfer.apply(
                geo_data=self.geo_data,
                style=self.style_image_path,
                iterations=5,  # Use low iterations for faster test
            )

            self.assertIsInstance(styled_image, Image.Image)

            # Save and check output
            output_path = os.path.join(self.test_dir, "output.png")
            styled_image.save(output_path)
            self.assertTrue(os.path.exists(output_path))

        except Exception as e:
            self.fail(f"Style transfer test failed: {str(e)}")

    @pytest.mark.slow
    def test_apply_with_custom_weights(self):
        """Test applying style transfer with custom weights."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            self.fail("TensorFlow is required by the declared ART test dependencies")

        try:
            # Apply with custom weights
            styled_image = StyleTransfer.apply(
                geo_data=self.geo_data,
                style=self.style_image_path,
                content_image=self.content_image_path,
                style_weight=1e-3,
                content_weight=1e3,
                iterations=3,  # Use low iterations for faster test
            )

            self.assertIsInstance(styled_image, Image.Image)

        except Exception as e:
            self.fail(f"Style transfer with custom weights failed: {str(e)}")

    def test_apply_with_invalid_inputs(self):
        """Test applying style transfer with invalid inputs."""
        # Skip test if TensorFlow is not available
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            self.fail("TensorFlow is required by the declared ART test dependencies")

        # Test with invalid style
        with self.assertRaises(ValueError):
            StyleTransfer.apply(geo_data=self.geo_data, style="nonexistent_style")

        # Test with invalid geo_data
        with self.assertRaises(ValueError):
            StyleTransfer.apply(geo_data="not_geo_data", style="watercolor")


if __name__ == "__main__":
    unittest.main()
