"""CONTRACT-DRIFT SYNC-CHECK for bundled Crescent City geo-intel seeds."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = "crescent-city-geo-intel/v1"
PRODUCER_CONTRACT = "docxology/crescent-city-intel/pages-data/geo-intel.json"
SEED_PATHS = {
    # Canonical packaged copy (post-consolidation single source; the former
    # RISK duplicate was removed and is pinned by object identity below).
    "BAYES": REPO_ROOT
    / "GEO-INFER-BAYES/src/geo_infer_bayes/crescent-city-geo-intel.json",
    "PLACE": REPO_ROOT
    / (
        "GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/"
        "data/crescent-city-geo-intel.json"
    ),
}
EXPECTED_HAZARD_DOMAIN_IDS = frozenset(
    {
        "climate-environment",
        "emergency-management",
        "environmental-protection",
        "event-planning",
    }
)


def _drift_message(detail: str) -> str:
    return (
        f"{detail} Re-sync every bundled seed from the producer repository path "
        f"{PRODUCER_CONTRACT}."
    )


def _read_seed_bytes(consumer: str, path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AssertionError(
            _drift_message(
                f"{consumer} seed {path.relative_to(REPO_ROOT)} cannot be read: {exc}."
            )
        ) from exc


def _load_seed(consumer: str, path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(_read_seed_bytes(consumer, path))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AssertionError(
            _drift_message(
                f"{consumer} seed {path.relative_to(REPO_ROOT)} is invalid JSON: {exc}."
            )
        ) from exc

    assert isinstance(payload, dict), _drift_message(
        f"{consumer} seed {path.relative_to(REPO_ROOT)} must contain a JSON object."
    )
    return payload


def _hazard_surface(
    consumer: str, seed: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], frozenset[str]]:
    hazard = seed.get("hazard")
    assert isinstance(hazard, dict), _drift_message(
        f"{consumer} seed must contain a hazard object."
    )

    domains = hazard.get("relevantDomains")
    assert isinstance(domains, list), _drift_message(
        f"{consumer} seed hazard.relevantDomains must be a list."
    )

    domain_ids: list[str] = []
    typed_domains: list[dict[str, Any]] = []
    for index, domain in enumerate(domains):
        assert isinstance(domain, dict), _drift_message(
            f"{consumer} seed hazard.relevantDomains[{index}] must be an object."
        )
        domain_id = domain.get("id")
        assert isinstance(domain_id, str) and domain_id, _drift_message(
            f"{consumer} seed hazard.relevantDomains[{index}] needs a non-empty id."
        )
        hazard_tags = domain.get("hazardTags")
        assert isinstance(hazard_tags, list) and all(
            isinstance(tag, str) for tag in hazard_tags
        ), _drift_message(
            f"{consumer} seed hazard domain {domain_id!r} needs a string hazardTags list."
        )
        domain_ids.append(domain_id)
        typed_domains.append(domain)

    assert len(domain_ids) == len(set(domain_ids)), _drift_message(
        f"{consumer} seed contains duplicate hazard domain IDs: {domain_ids!r}."
    )
    return hazard, typed_domains, frozenset(domain_ids)


def test_bundled_crescent_city_seeds_are_byte_identical() -> None:
    seed_bytes = {
        consumer: _read_seed_bytes(consumer, path)
        for consumer, path in SEED_PATHS.items()
    }
    digests = {
        consumer: hashlib.sha256(content).hexdigest()
        for consumer, content in seed_bytes.items()
    }

    assert len(set(seed_bytes.values())) == 1, _drift_message(
        f"Bundled Crescent City seed bytes diverged; SHA-256 by consumer: {digests}."
    )


@pytest.mark.parametrize(
    ("consumer", "seed_path"),
    SEED_PATHS.items(),
    ids=SEED_PATHS,
)
def test_seed_matches_v1_anchor_and_hazard_shape(
    consumer: str, seed_path: Path
) -> None:
    seed = _load_seed(consumer, seed_path)
    assert seed.get("schema") == SCHEMA, _drift_message(
        f"{consumer} seed schema must be {SCHEMA!r}, got {seed.get('schema')!r}."
    )

    anchor = seed.get("anchor")
    assert isinstance(anchor, dict), _drift_message(
        f"{consumer} seed must contain an anchor object."
    )
    bounds = anchor.get("bounds")
    assert isinstance(bounds, dict), _drift_message(
        f"{consumer} seed anchor.bounds must be an object."
    )

    coordinates: dict[str, float] = {}
    for name, source in (
        ("latitude", anchor),
        ("longitude", anchor),
        ("west", bounds),
        ("south", bounds),
        ("east", bounds),
        ("north", bounds),
    ):
        value = source.get(name)
        assert (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        ), _drift_message(f"{consumer} seed anchor {name} must be a finite number.")
        coordinates[name] = float(value)

    latitude = coordinates["latitude"]
    longitude = coordinates["longitude"]
    west = coordinates["west"]
    south = coordinates["south"]
    east = coordinates["east"]
    north = coordinates["north"]
    assert -180.0 <= west < east <= 180.0, _drift_message(
        f"{consumer} seed longitude bounds are invalid: west={west}, east={east}."
    )
    assert -90.0 <= south < north <= 90.0, _drift_message(
        f"{consumer} seed latitude bounds are invalid: south={south}, north={north}."
    )
    assert west <= longitude <= east and south <= latitude <= north, _drift_message(
        f"{consumer} seed anchor ({latitude}, {longitude}) lies outside its bounds."
    )

    hazard, domains, _ = _hazard_surface(consumer, seed)
    relevant_count = hazard.get("relevantDomainCount")
    assert isinstance(relevant_count, int) and not isinstance(
        relevant_count, bool
    ), _drift_message(
        f"{consumer} seed hazard.relevantDomainCount must be an integer."
    )
    assert relevant_count == len(domains), _drift_message(
        f"{consumer} seed declares {relevant_count} relevant domains but contains "
        f"{len(domains)}."
    )
    assert relevant_count >= 4, _drift_message(
        f"{consumer} seed exposes only {relevant_count} hazard domains; expected at least 4."
    )

    hazard_tags = {
        tag.casefold().replace("-", " ")
        for domain in domains
        for tag in domain.get("hazardTags", [])
        if isinstance(tag, str)
    }
    assert any("flood" in tag for tag in hazard_tags), _drift_message(
        f"{consumer} seed hazard surface no longer covers flood."
    )
    assert any("sea level" in tag for tag in hazard_tags), _drift_message(
        f"{consumer} seed hazard surface no longer covers sea-level risk."
    )


def test_bundled_seeds_share_canonical_hazard_domain_ids() -> None:
    domain_ids_by_consumer = {
        consumer: _hazard_surface(consumer, _load_seed(consumer, path))[2]
        for consumer, path in SEED_PATHS.items()
    }

    assert len(set(domain_ids_by_consumer.values())) == 1, _drift_message(
        "Bundled seed hazard domain IDs diverged: "
        f"{domain_ids_by_consumer!r}."
    )
    actual_ids = next(iter(domain_ids_by_consumer.values()))
    assert actual_ids == EXPECTED_HAZARD_DOMAIN_IDS, _drift_message(
        "Bundled seed hazard domain IDs no longer match the canonical v1 surface: "
        f"expected {sorted(EXPECTED_HAZARD_DOMAIN_IDS)!r}, got {sorted(actual_ids)!r}."
    )


def test_consumer_modules_resolve_canonical_schema_objects() -> None:
    """RISK/ACT pin the canonical schema via identity, not bundled copies."""
    import geo_infer_act.core.civic_intel as act_civic
    import geo_infer_bayes.civic_intel as bayes_civic
    import geo_infer_risk.civic_intel as risk_civic

    assert bayes_civic.CRESCENT_CITY_INTEL_SCHEMA == SCHEMA
    assert act_civic.CRESCENT_CITY_INTEL_SCHEMA is (
        bayes_civic.CRESCENT_CITY_INTEL_SCHEMA
    )
    assert act_civic.SUPPORTED_SCHEMA is bayes_civic.CRESCENT_CITY_INTEL_SCHEMA
    assert risk_civic.CRESCENT_CITY_GEO_INTEL_SCHEMA is (
        bayes_civic.CRESCENT_CITY_INTEL_SCHEMA
    )
    assert risk_civic.load_crescent_city_contract is (
        bayes_civic.load_crescent_city_contract
    )
    assert act_civic.load_crescent_city_contract is (
        bayes_civic.load_crescent_city_contract
    )
