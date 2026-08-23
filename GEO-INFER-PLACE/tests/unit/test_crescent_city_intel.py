#!/usr/bin/env python3
"""
Test suite for CrescentCityIntelMapper — the civic-intel bridge from the
crescent-city-intel platform's machine-readable contract (schema
``crescent-city-geo-intel/v1``) onto the Del Norte H3 canvas.

Covers:
- Contract loading (packaged seed, missing-path degradation)
- 12 civic-domain surface + hazard-relevant subset
- H3 cell generation across the Del Norte bounds
- Hazard-intent surface shaping

All tests use the real mapper + the packaged (committed) seed; no mocks.
"""

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict

# Package source root (conftest normally adds this, but keep the import
# self-sufficient for direct invocation too).
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_PACKAGED_SEED = (
    _SRC
    / "geo_infer_place"
    / "locations"
    / "del_norte_county"
    / "data"
    / "crescent-city-geo-intel.json"
)


def _seed_json() -> Dict[str, Any]:
    """Load the real packaged seed (the test fixture)."""
    with open(_PACKAGED_SEED, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _mapper(seed_path: Path) -> Any:
    from geo_infer_place.locations.del_norte_county.crescent_city_intel import (
        CrescentCityIntelMapper,
    )

    return CrescentCityIntelMapper(seed_path=seed_path)


class TestContractLoad(unittest.TestCase):
    """Contract loading from the packaged seed + degradation paths."""

    def test_contract_has_v1_schema_and_12_domains(self) -> None:
        seed = _seed_json()
        assert seed["schema"] == "crescent-city-geo-intel/v1"
        assert seed["domainCount"] == 12

    def test_mapper_loads_packaged_seed(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        assert mapper.loaded is True
        assert len(mapper.domains()) == 12
        assert mapper.source_path == _PACKAGED_SEED

    def test_mapper_graceful_when_seed_missing(self) -> None:
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="test_intel_"))
        seed_path = tmp / "missing-geo-intel.json"
        mapper = _mapper(seed_path)
        assert mapper.loaded is False
        assert mapper.error is not None
        assert mapper.domains() == []
        assert mapper.hazard_domains() == []

    def test_mapper_rejects_wrong_schema(self) -> None:
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="test_intel_bad_"))
        seed_path = tmp / "bad.json"
        seed_path.write_text(json.dumps({"schema": "wrong/v1", "domains": []}))
        mapper = _mapper(seed_path)
        assert mapper.loaded is False


class TestContactPublicSurface(unittest.TestCase):
    """Civic-domain + hazard surface projection."""

    def test_domain_ids_have_unique_slugs(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        ids = mapper.domain_ids()
        assert len(ids) == 12
        assert len(set(ids)) == 12

    def test_hazard_domains_flagged(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        hazard = mapper.hazard_domains()
        assert len(hazard) >= 1
        # Emergency-management is the flagship tsunami/preparedness domain.
        assert "emergency-management" in [d["id"] for d in hazard]

    def test_bounds_are_valid_del_norte_extent(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        b = mapper.bounds()
        assert b["west"] < b["east"] < -123
        assert b["south"] < b["north"]

    def test_generate_h3_cells_produces_grid(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        cells = mapper.generate_h3_cells()
        assert len(cells) > 0
        first = next(iter(cells.values()))
        assert first["intel_present"] is True
        assert isinstance(first["hazard_tags"], list)

    def test_hazard_surface_shapes_domains(self) -> None:
        mapper = _mapper(_PACKAGED_SEED)
        surface = mapper.generate_hazard_surface()
        assert surface["status"] == "ok"
        assert len(surface["domains"]) >= 1
        for domain in surface["domains"]:
            assert "hazardTags" in domain
            assert "topics" in domain


if __name__ == "__main__":
    unittest.main()