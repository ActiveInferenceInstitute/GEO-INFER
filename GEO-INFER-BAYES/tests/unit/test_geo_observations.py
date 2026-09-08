"""Tests for Crescent City hazard-observation ingestion (BAYES core).

The default-path tests read the real bundled snapshot copied from the
``crescent-city-intel`` producer's committed pages seed (a live composite
WARNING envelope with 15 monitors).  Fixture tests exercise the same loader
with synthesized real and unavailable envelopes; failure tests pin the
fail-closed validation contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geo_infer_bayes.geo_observations import (
    CRESCENT_CITY_OBSERVATIONS_SCHEMA,
    GEO_INTEL_CONTRACT_SCHEMA_REF,
    VALID_OBSERVATION_STATUSES,
    load_crescent_city_geo_observations,
)


def _unavailable_envelope() -> dict[str, object]:
    """A structurally valid envelope in the honest empty/unavailable state."""
    return {
        "schema": CRESCENT_CITY_OBSERVATIONS_SCHEMA,
        "anchor": {
            "name": "Crescent City",
            "guid": "CR4919",
            "municipality": "Crescent City, CA",
            "county": "Del Norte County",
            "state": "California",
            "latitude": 41.76,
            "longitude": -124.2,
        },
        "generatedAt": "2026-09-08T00:00:00.000Z",
        "composite": None,
        "monitors": [],
        "hazardSummary": [],
        "freshness": {
            "contractSchema": GEO_INTEL_CONTRACT_SCHEMA_REF,
            "contractGeneratedAt": None,
        },
    }


class TestBundledSnapshot:
    """Default-path loads read the reviewed bundled producer snapshot."""

    def test_bundled_load_returns_valid_envelope(self) -> None:
        envelope = load_crescent_city_geo_observations()
        assert envelope is not None
        assert envelope["schema"] == CRESCENT_CITY_OBSERVATIONS_SCHEMA
        anchor = envelope["anchor"]
        assert anchor["name"] == "Crescent City"
        assert anchor["county"] == "Del Norte County"
        assert anchor["latitude"] == pytest.approx(41.76)
        assert anchor["longitude"] == pytest.approx(-124.2)

    def test_bundled_snapshot_carries_live_composite(self) -> None:
        envelope = load_crescent_city_geo_observations()
        assert envelope is not None
        composite = envelope["composite"]
        assert composite is not None
        assert composite["level"] in {"CALM", "WATCH", "WARNING", "EMERGENCY"}
        assert composite["assessedAt"] is not None

    def test_bundled_snapshot_preserves_producer_monitor_ordering(self) -> None:
        envelope = load_crescent_city_geo_observations()
        assert envelope is not None
        monitors = envelope["monitors"]
        assert len(monitors) == 15
        assert monitors[0]["id"] == "noaa-tsunami"
        ids = [monitor["id"] for monitor in monitors]
        assert len(ids) == len(set(ids))
        assert "uscg-broadcast-notice-to-mariners" in ids

    def test_bundled_snapshot_freshness_refs_intel_contract(self) -> None:
        envelope = load_crescent_city_geo_observations()
        assert envelope is not None
        freshness = envelope["freshness"]
        assert freshness["contractSchema"] == GEO_INTEL_CONTRACT_SCHEMA_REF
        assert freshness["contractGeneratedAt"] is not None

    def test_bundled_load_is_deterministic(self) -> None:
        first = load_crescent_city_geo_observations()
        second = load_crescent_city_geo_observations()
        assert first == second

    def test_hazard_summary_entries_are_wellformed(self) -> None:
        envelope = load_crescent_city_geo_observations()
        assert envelope is not None
        for entry in envelope["hazardSummary"]:
            assert isinstance(entry["tag"], str) and entry["tag"]
            assert entry["domainCount"] >= 0
            assert entry["topicCount"] >= 0


class TestInjectedSources:
    """Mapping and path injection mirror the civic-intel loader semantics."""

    def test_injected_mapping_passes_through_after_validation(self) -> None:
        fixture = _unavailable_envelope()
        envelope = load_crescent_city_geo_observations(fixture)
        assert envelope is not None
        assert envelope["composite"] is None
        assert envelope["monitors"] == []

    def test_injected_path_load(self, tmp_path: Path) -> None:
        fixture = _unavailable_envelope()
        path = tmp_path / "geo-observations.json"
        path.write_text(json.dumps(fixture), encoding="utf-8")
        envelope = load_crescent_city_geo_observations(path)
        assert envelope is not None
        assert envelope["schema"] == CRESCENT_CITY_OBSERVATIONS_SCHEMA

    def test_missing_path_yields_none(self, tmp_path: Path) -> None:
        assert load_crescent_city_geo_observations(tmp_path / "absent.json") is None


class TestFailClosedValidation:
    """Structural violations fail closed; missing sources stay None."""

    def test_wrong_schema_id_rejected(self) -> None:
        fixture = _unavailable_envelope()
        fixture["schema"] = "crescent-city-geo-observations/v2"
        with pytest.raises(ValueError, match="expected schema"):
            load_crescent_city_geo_observations(fixture)

    def test_unrecognized_monitor_status_rejected(self) -> None:
        fixture = _unavailable_envelope()
        fixture["monitors"] = [
            {"id": "noaa-tsunami", "label": "NOAA Tsunami", "status": "OFFLINE"}
        ]
        with pytest.raises(ValueError, match="unrecognized status"):
            load_crescent_city_geo_observations(fixture)

    def test_missing_required_field_rejected(self) -> None:
        fixture = _unavailable_envelope()
        del fixture["freshness"]
        with pytest.raises(ValueError, match="missing required field"):
            load_crescent_city_geo_observations(fixture)

    def test_wrong_freshness_contract_ref_rejected(self) -> None:
        fixture = _unavailable_envelope()
        fixture["freshness"] = {
            "contractSchema": "crescent-city-geo-intel/v0",
            "contractGeneratedAt": None,
        }
        with pytest.raises(ValueError, match="contractSchema"):
            load_crescent_city_geo_observations(fixture)

    def test_nonfinite_anchor_coordinate_rejected(self) -> None:
        fixture = _unavailable_envelope()
        fixture["anchor"] = {
            "name": "Crescent City",
            "guid": "CR4919",
            "municipality": "Crescent City, CA",
            "county": "Del Norte County",
            "state": "California",
            "latitude": "41.76",
            "longitude": -124.2,
        }
        with pytest.raises(ValueError, match="latitude"):
            load_crescent_city_geo_observations(fixture)

    def test_malformed_json_file_fails_closed(self, tmp_path: Path) -> None:
        path = tmp_path / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(ValueError):
            load_crescent_city_geo_observations(path)

    def test_status_enum_is_the_producer_set(self) -> None:
        assert VALID_OBSERVATION_STATUSES == frozenset(
            {"ok", "empty", "unavailable", "stale"}
        )
