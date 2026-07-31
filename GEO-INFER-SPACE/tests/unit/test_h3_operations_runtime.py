"""Regression tests for the public H3 operation helpers."""

import pytest
import h3

from geo_infer_space.backends.h3.h3_backend import H3Backend
from geo_infer_space.backends.h3.operations import (
    cell_to_boundary,
    cell_to_coordinates,
    cells_to_geojson,
    cells_to_polygon,
    compact_cells,
    coordinate_to_cell,
    polygon_to_cells,
    uncompact_cells,
)
from geo_infer_space.utils.h3_utils import (
    cell_to_latlngjson,
    polygon_to_cells as geojson_polygon_to_cells,
)


def test_cell_to_coordinates_round_trip() -> None:
    cell = coordinate_to_cell(37.7749, -122.4194, 9)
    latitude, longitude = cell_to_coordinates(cell)

    assert abs(latitude - 37.7749) < 0.01
    assert abs(longitude + 122.4194) < 0.01


def test_cell_to_coordinates_rejects_invalid_cell() -> None:
    with pytest.raises(ValueError):
        cell_to_coordinates("not-an-h3-cell")


def test_runtime_h3_version_is_current_v4_contract() -> None:
    major, minor, patch = (int(part) for part in h3.__version__.split(".")[:3])
    assert (major, minor, patch) >= (4, 5, 0)
    assert major < 5


def test_cell_boundary_supports_native_and_geojson_coordinate_orders() -> None:
    cell = coordinate_to_cell(37.7749, -122.4194, 9)

    native = cell_to_boundary(cell)
    geojson = cell_to_boundary(cell, geo_json=True)

    assert len(native) == len(geojson) == 6
    assert geojson[0] == (native[0][1], native[0][0])


def test_h3_geojson_exports_emit_closed_lng_lat_rings() -> None:
    cell = coordinate_to_cell(37.7749, -122.4194, 9)

    feature_collection = cells_to_geojson([cell])
    ring = feature_collection["features"][0]["geometry"]["coordinates"][0]

    assert ring[0] == ring[-1]
    assert all(-180 <= point[0] <= 180 and -90 <= point[1] <= 90 for point in ring)


def test_polygon_and_reverse_polygon_wrappers_use_h3_v4_shapes() -> None:
    coords = [
        (37.70, -122.50),
        (37.70, -122.30),
        (37.80, -122.30),
        (37.80, -122.50),
    ]
    cells = polygon_to_cells(coords, 8)

    assert cells
    boundary = cells_to_polygon({cells[0]})
    assert boundary[0] == boundary[-1]


def test_geojson_polygon_preserves_holes_and_multipolygons() -> None:
    polygon_with_hole = {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.50, 37.70],
                [-122.30, 37.70],
                [-122.30, 37.80],
                [-122.50, 37.80],
                [-122.50, 37.70],
            ],
            [
                [-122.46, 37.74],
                [-122.34, 37.74],
                [-122.34, 37.76],
                [-122.46, 37.76],
                [-122.46, 37.74],
            ],
        ],
    }
    multipolygon = {
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
    }

    assert set(geojson_polygon_to_cells(polygon_with_hole, 8)) == set(
        h3.geo_to_cells(polygon_with_hole, 8)
    )
    assert set(geojson_polygon_to_cells(multipolygon, 8)) == set(
        h3.geo_to_cells(multipolygon, 8)
    )


def test_geojson_antimeridian_polygon_stays_near_dateline() -> None:
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [179.8, 10.0],
                [-179.8, 10.0],
                [-179.8, 10.2],
                [179.8, 10.2],
                [179.8, 10.0],
            ]
        ],
    }

    cells = geojson_polygon_to_cells(geometry, 7)
    longitudes = [h3.cell_to_latlng(cell)[1] for cell in cells]

    assert cells
    assert all(longitude > 150 or longitude < -150 for longitude in longitudes)


def test_pentagon_neighbors_are_the_exact_native_disk_ring() -> None:
    backend = H3Backend()
    pentagon = h3.get_pentagons(0)[0]

    assert set(backend.get_cell_neighbors(pentagon)) == set(h3.grid_disk(pentagon, 1)) - {
        pentagon
    }


def test_compaction_round_trip_matches_native_h3() -> None:
    parent = h3.latlng_to_cell(37.7749, -122.4194, 7)
    children = set(h3.cell_to_children(parent, 9))
    compacted = set(compact_cells(children))

    assert compacted == set(h3.compact_cells(children))
    assert set(uncompact_cells(compacted, 9)) == children


def test_geojson_utility_does_not_mutate_inputs_or_properties() -> None:
    flat_polygon = {
        "type": "Polygon",
        "coordinates": [
            [-122.50, 37.70],
            [-122.30, 37.70],
            [-122.30, 37.80],
            [-122.50, 37.80],
            [-122.50, 37.70],
        ],
    }
    original_coordinates = list(flat_polygon["coordinates"])
    properties = {"cell": {"label": "sample"}}
    cell = coordinate_to_cell(37.7749, -122.4194, 9)

    assert geojson_polygon_to_cells(flat_polygon, 8)
    assert flat_polygon["coordinates"] == original_coordinates

    cell_to_latlngjson([cell], properties)
    assert properties == {"cell": {"label": "sample"}}


def test_public_space_h3_exports_cover_the_native_helpers() -> None:
    from geo_infer_space.utils import (
        cell_to_latlngjson as exported_cell_to_latlngjson,
        geojson_to_h3 as exported_geojson_to_h3,
        grid_ring as exported_grid_ring,
    )

    assert exported_cell_to_latlngjson is cell_to_latlngjson
    assert callable(exported_geojson_to_h3)
    cell = coordinate_to_cell(37.7749, -122.4194, 9)
    assert set(exported_grid_ring(cell, 1)) == set(h3.grid_disk(cell, 1)) - {cell}
