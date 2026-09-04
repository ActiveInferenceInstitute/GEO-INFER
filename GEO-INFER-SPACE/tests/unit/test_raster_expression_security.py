"""Map algebra evaluates arithmetic without exposing Python or filesystem APIs."""

from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from geo_infer_space.analytics.raster import map_algebra

pytestmark = pytest.mark.unit


def _raster(path: Path, *, x: float = 0) -> Path:
    """Write a real two-by-two input grid with one nodata cell."""
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=2,
        height=2,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(x, 2, 1, 1),
        nodata=-9999,
    ) as dst:
        dst.write(np.array([[1, 2], [0, -9999]], dtype="float32"), 1)
    return path


@pytest.mark.parametrize(
    "expression",
    [
        "np.save('unexpected.npy', b1)",
        "b1.__class__",
        "np.__dict__",
        "[x for x in b1]",
        "__import__('os')",
        "np.load('input.npy')",
    ],
)
def test_rejects_non_arithmetic_expression(tmp_path, expression, monkeypatch):
    """Unsupported expressions fail without producing output or side effects."""
    monkeypatch.chdir(tmp_path)
    source = _raster(tmp_path / "source.tif")
    output = tmp_path / "output.tif"
    with pytest.raises(ValueError, match="expression"):
        map_algebra([str(source)], expression, str(output))
    assert not output.exists()


def test_expression_preserves_nodata_and_broadcasts_scalars(tmp_path):
    """Arithmetic and constants retain missing-data masks in the output."""
    source = _raster(tmp_path / "source.tif")
    output = tmp_path / "out.tif"
    map_algebra([str(source)], "np.where(b1 > 0, b1 * 2, 0)", str(output))
    with rasterio.open(output) as result:
        np.testing.assert_array_equal(result.read(1), [[2, 4], [0, -9999]])
    map_algebra([str(source)], "3", str(output))
    with rasterio.open(output) as result:
        np.testing.assert_array_equal(result.read(1), [[3, 3], [3, -9999]])


def test_misaligned_rasters_are_rejected(tmp_path):
    """Equal array shapes cannot mask incompatible spatial transforms."""
    a = _raster(tmp_path / "a.tif")
    b = _raster(tmp_path / "b.tif", x=10)
    with pytest.raises(ValueError, match="aligned"):
        map_algebra([str(a), str(b)], "b1 + b2", str(tmp_path / "out.tif"))


def test_expression_cannot_use_positional_output_buffers():
    """Allowed NumPy functions cannot mutate input bands through out arguments."""
    from geo_infer_space.analytics.raster import _evaluate_expression

    band = np.array([[1.0, 2.0]])
    with pytest.raises(ValueError, match="argument count"):
        _evaluate_expression("np.minimum(b1, 0, b1)", {"b1": band}, -9999)
    np.testing.assert_array_equal(band, [[1.0, 2.0]])
