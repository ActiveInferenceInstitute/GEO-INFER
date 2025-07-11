import pytest
import h3
from geo_infer_space.utils.h3_utils import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

def test_geo_to_h3():
    h3_index = geo_to_h3(40.7128, -74.0060, 8)
    assert isinstance(h3_index, str)
    assert len(h3_index) == 15

def test_h3_to_geo():
    lat, lon = h3_to_geo('88283082bfffffff')
    assert isinstance(lat, float)
    assert isinstance(lon, float)

def test_h3_to_geo_boundary():
    boundary = h3_to_geo_boundary('88283082bfffffff')
    assert isinstance(boundary, list)
    assert len(boundary) == 6

def test_polyfill():
    polygon = {
        'type': 'Polygon',
        'coordinates': [[[ -74.01, 40.71], [-74.01, 40.72],
                         [-74.00, 40.72], [-74.00, 40.71],
                         [-74.01, 40.71]]]
    }
    indices = polyfill(polygon, 8)
    assert isinstance(indices, list)
    assert len(indices) > 0 