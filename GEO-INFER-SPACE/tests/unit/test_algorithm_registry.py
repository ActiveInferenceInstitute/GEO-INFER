"""Tests for the processing algorithm registry (item 6)."""

from __future__ import annotations

import pytest

from geo_infer_space.core.algorithm_registry import (
    AlgorithmRegistry,
    ParameterSpec,
    ProcessingAlgorithm,
    ProcessingContext,
    build_reference_registry,
)


def _grid_layer() -> dict:
    """A tiny GeoJSON layer for bounds/count reference tests."""
    return {
        "id": "grid",
        "geojson": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [2, 0], [2, 1], [0, 1], [0, 0]]],
                    },
                }
            ],
        },
    }


def test_register_and_get() -> None:
    reg = AlgorithmRegistry()
    alg = ProcessingAlgorithm(
        id="demo",
        name="Demo",
        description="A demo algorithm",
        run=lambda ctx: 42,
    )
    reg.register(alg)
    assert reg.contains("demo")
    assert reg.get("demo").id == "demo"
    assert reg.get("demo").name == "Demo"


def test_register_duplicate_raises() -> None:
    reg = AlgorithmRegistry()
    alg = ProcessingAlgorithm(id="dup", name="D", description="D", run=lambda ctx: 1)
    reg.register(alg)
    with pytest.raises(ValueError):
        reg.register(alg)


def test_get_unknown_raises() -> None:
    reg = AlgorithmRegistry()
    with pytest.raises(KeyError):
        reg.get("nope")
    assert reg.contains("nope") is False


def test_list_sorted_by_id() -> None:
    def mk(aid: str) -> ProcessingAlgorithm:
        return ProcessingAlgorithm(id=aid, name=aid, description=aid, run=lambda ctx: aid)

    reg = AlgorithmRegistry([mk("z"), mk("a"), mk("m")])
    assert [a.id for a in reg.list()] == ["a", "m", "z"]


def test_run_dispatches() -> None:
    reg = AlgorithmRegistry()
    reg.register(
        ProcessingAlgorithm(id="double", name="Double", description="D", run=lambda ctx: 21 * 2)
    )
    assert reg.run("double", ProcessingContext()) == 42


def test_run_unknown_raises() -> None:
    reg = AlgorithmRegistry()
    with pytest.raises(KeyError):
        reg.run("missing", ProcessingContext())


def test_context_log() -> None:
    ctx = ProcessingContext()
    ctx.log("hello")
    ctx.log("world")
    assert ctx.logs == ["hello", "world"]


def test_reference_registry_has_builtins() -> None:
    reg = build_reference_registry()
    ids = {a.id for a in reg.list()}
    assert {"calculate-bounds", "count-features"} <= ids


def test_reference_count_features() -> None:
    reg = build_reference_registry()
    ctx = ProcessingContext(layers=[_grid_layer()], parameters={"layer": "grid"})
    result = reg.run("count-features", ctx)
    assert result == 1
    assert ctx.logs == ["Feature count: 1"]


def test_reference_bounds() -> None:
    reg = build_reference_registry()
    ctx = ProcessingContext(layers=[_grid_layer()], parameters={"layer": "grid"})
    result = reg.run("calculate-bounds", ctx)
    assert result == [0.0, 0.0, 2.0, 1.0]


def test_reference_bounds_missing_layer_logs() -> None:
    reg = build_reference_registry()
    ctx = ProcessingContext(layers=[_grid_layer()], parameters={"layer": "not-here"})
    result = reg.run("calculate-bounds", ctx)
    assert result is None
    assert any("not found" in log for log in ctx.logs)


def test_parameter_spec_fields() -> None:
    spec = ParameterSpec(id="layer", label="Layer", required=True)
    assert spec.id == "layer"
    assert spec.required is True
    assert spec.type == "auto"
