import pytest
import h3
from geo_infer_space.utils.h3_utils import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

def test_geo_to_h3():
    h3_index = geo_to_h3(40.7128, -74.0060, 8)
    assert isinstance(h3_index, str)
    assert len(h3_index) == 15

def test_h3_to_geo():
    lat, lon = h3_to_geo('882a107289fffff')
    assert isinstance(lat, float)
    assert isinstance(lon, float)

def test_h3_to_geo_boundary():
    boundary = h3_to_geo_boundary('882a107289fffff')
    assert isinstance(boundary, tuple)
    assert len(boundary) == 6

def test_polyfill():
    polygon = {
        'type': 'Polygon',
        'coordinates': [[[ -74.01, 40.71], [-74.01, 40.72],
                         [-74.00, 40.72], [-74.00, 40.71],
                         [-74.01, 40.71]]]
    }
    indices = polyfill(polygon, 9)  # Use res 9 for small polygon
    assert isinstance(indices, list)
    assert len(indices) > 0 