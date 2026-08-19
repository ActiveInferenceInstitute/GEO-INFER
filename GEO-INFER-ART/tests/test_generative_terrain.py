"""Behavior tests for GenerativeMap procedural terrain.

The terrain generators are deliberately generative, not measured; these
tests pin the two properties that makes it defensible -- determinism, and
relief that actually varies with the region's declared scale.
"""

import numpy as np
import pytest

from geo_infer_art.core.generation.generative_map import GenerativeMap


class TestRegionTerrain:
    def test_output_shape_matches_resolution(self):
        """The generated grid is square at the requested resolution."""
        terrain = GenerativeMap._generate_region_terrain("alps", resolution=64)
        assert terrain.shape == (64, 64)

    def test_generation_is_deterministic(self):
        """The same region renders identically across calls."""
        first = GenerativeMap._generate_region_terrain("everest", resolution=32)
        second = GenerativeMap._generate_region_terrain("everest", resolution=32)
        np.testing.assert_array_equal(first, second)

    def test_different_regions_differ(self):
        """Distinct regions produce distinct relief."""
        alps = GenerativeMap._generate_region_terrain("alps", resolution=32)
        sahara = GenerativeMap._generate_region_terrain("sahara", resolution=32)
        assert not np.array_equal(alps, sahara)

    def test_relief_amplitude_tracks_region_scale(self):
        """A high-relief region varies more than a low-relief one."""
        everest = GenerativeMap._generate_region_terrain("everest", resolution=64)
        sahara = GenerativeMap._generate_region_terrain("sahara", resolution=64)
        assert everest.std() > sahara.std()

    def test_output_is_finite(self):
        """Generated relief contains no NaN or infinity."""
        terrain = GenerativeMap._generate_region_terrain("amazon", resolution=32)
        assert np.all(np.isfinite(terrain))

    def test_unknown_region_is_rejected(self):
        """An unsupported region name raises rather than inventing terrain."""
        with pytest.raises(ValueError, match="Unknown region"):
            GenerativeMap._generate_region_terrain("atlantis", resolution=32)

    def test_global_rng_is_not_consumed(self):
        """Generation does not disturb the process-global random state."""
        np.random.seed(1234)
        expected = np.random.random()
        np.random.seed(1234)
        GenerativeMap._generate_region_terrain("alps", resolution=32)
        assert np.random.random() == expected


class TestBboxTerrain:
    def test_generation_is_deterministic(self):
        """The same extent renders identically across calls."""
        bbox = (-1.0, 50.0, 1.0, 52.0)
        first = GenerativeMap._generate_bbox_terrain(bbox, resolution=32)
        second = GenerativeMap._generate_bbox_terrain(bbox, resolution=32)
        np.testing.assert_array_equal(first, second)

    def test_different_extents_differ(self):
        """Distinct bounding boxes produce distinct relief."""
        a = GenerativeMap._generate_bbox_terrain((-1.0, 50.0, 1.0, 52.0), resolution=32)
        b = GenerativeMap._generate_bbox_terrain((10.0, 20.0, 12.0, 22.0), resolution=32)
        assert not np.array_equal(a, b)

    def test_larger_extent_has_gentler_relief(self):
        """Relief amplitude falls as the covered area grows."""
        small = GenerativeMap._generate_bbox_terrain((0.0, 0.0, 0.5, 0.5), resolution=64)
        large = GenerativeMap._generate_bbox_terrain((0.0, 0.0, 20.0, 20.0), resolution=64)
        assert small.std() > large.std()

    @pytest.mark.parametrize(
        "bbox",
        [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 1.0, 0.0), (0.0, 0.0, 0.0, 0.0)],
    )
    def test_invalid_bbox_is_rejected(self, bbox):
        """A degenerate or inverted box raises instead of returning noise."""
        with pytest.raises(ValueError, match="Invalid bounding box"):
            GenerativeMap._generate_bbox_terrain(bbox, resolution=32)
