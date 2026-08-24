"""Tests for Crescent City civic-intel ingestion and hazard priors.

The default-path tests read the real package resource copied from the
``crescent-city-intel`` v1 producer. Injected-contract tests exercise the same
parser with concrete civic domains and municipal-code references.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from geo_infer_bayes import (
    HazardCategoricalPrior,
    build_hazard_categorical_prior,
    build_hazard_prior_table,
    load_crescent_city_intel,
)
from geo_infer_bayes.civic_intel import (
    CRESCENT_CITY_INTEL_SCHEMA,
    DEFAULT_HAZARD_TAG_WEIGHTS,
    HazardPriorTable,
)


def _section(number: str, relevance: str) -> dict[str, str]:
    return {"sectionNumber": number, "relevance": relevance}


def _civic_domain(
    domain_id: str,
    name: str,
    tags: list[str],
    sections: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "id": domain_id,
        "name": name,
        "icon": "⚠️",
        "description": f"Crescent City {name.lower()} policy.",
        "updatedAt": "2026-08-23",
        "topicCount": 1,
        "tags": tags,
        "sections": sections,
    }


def _hazard_domain(
    domain_id: str,
    name: str,
    tags: list[str],
    sections: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "id": domain_id,
        "name": name,
        "icon": "⚠️",
        "hazardTags": tags,
        "topics": [
            {
                "name": f"{name} municipal policy",
                "tags": tags,
                "sections": sections,
            }
        ],
    }


def _injected_contract() -> dict[str, object]:
    emergency_sections = [
        _section("§ 8.04", "Emergency management authority"),
        _section("§ 9.04", "Emergency powers"),
        _section("§ 15.04", "Seismic construction requirements"),
    ]
    flood_sections = [
        _section("§ 15.04", "Flood-zone construction standards"),
        _section("§ 16.04", "Flood-hazard subdivision review"),
        _section("§ 17.04", "Flood overlay district"),
        _section("§ 17.08", "Flood-zone development standards"),
    ]
    domains = [
        _civic_domain("flood-policy", "Flood Policy", ["flood"], flood_sections),
        _civic_domain(
            "emergency-management",
            "Emergency Management",
            ["tsunami", "seismic"],
            emergency_sections,
        ),
    ]
    relevant_domains = [
        _hazard_domain("flood-policy", "Flood Policy", ["flood"], flood_sections),
        _hazard_domain(
            "emergency-management",
            "Emergency Management",
            ["tsunami", "seismic"],
            emergency_sections,
        ),
    ]
    return {
        "schema": CRESCENT_CITY_INTEL_SCHEMA,
        "anchor": {
            "name": "Crescent City",
            "guid": "CR4919",
            "municipality": "Crescent City, CA",
            "county": "Del Norte County",
            "state": "California",
            "latitude": 41.76,
            "longitude": -124.2,
            "bounds": {
                "west": -124.408,
                "south": 41.458,
                "east": -123.536,
                "north": 42.006,
            },
        },
        "generatedAt": "2026-08-23T00:00:00.000Z",
        "domainCount": len(domains),
        "domains": domains,
        "hazard": {
            "relevantDomains": relevant_domains,
            "relevantDomainCount": len(relevant_domains),
        },
    }


def test_public_ingestion_and_prior_exports_are_importable() -> None:
    assert callable(load_crescent_city_intel)
    assert callable(build_hazard_prior_table)
    assert callable(build_hazard_categorical_prior)
    assert HazardCategoricalPrior.__module__ == "geo_infer_bayes.civic_intel"


def test_bundled_contract_loads_full_civic_and_hazard_surface() -> None:
    intel = load_crescent_city_intel(seed=17)

    assert set(intel) == {"city", "domains", "hazardDomains", "bounds"}
    assert intel["city"] is not None
    assert intel["city"]["name"] == "Crescent City"
    assert intel["city"]["county"] == "Del Norte County"
    assert intel["city"]["latitude"] == pytest.approx(41.76)
    assert intel["city"]["longitude"] == pytest.approx(-124.2)
    assert len(intel["domains"]) == 12
    assert {domain["id"] for domain in intel["hazardDomains"]} == {
        "climate-environment",
        "emergency-management",
        "environmental-protection",
        "event-planning",
    }
    all_hazard_tags = [
        tag
        for domain in intel["hazardDomains"]
        for tag in domain.get("hazardTags", [])
    ]
    assert any("flood" in tag for tag in all_hazard_tags)
    assert any("sea level" in tag for tag in all_hazard_tags)
    assert intel["bounds"] == {
        "west": -124.408,
        "south": 41.458,
        "east": -123.536,
        "north": 42.006,
    }


def test_injected_mapping_and_real_json_path_use_the_same_parser(tmp_path: Path) -> None:
    contract = _injected_contract()
    from_mapping = load_crescent_city_intel(source=contract)

    json_path = tmp_path / "geo-intel.json"
    json_path.write_text(json.dumps(contract), encoding="utf-8")
    from_path = load_crescent_city_intel(source=json_path)

    assert from_mapping == from_path
    assert [domain["id"] for domain in from_mapping["domains"]] == [
        "flood-policy",
        "emergency-management",
    ]


def test_parser_returns_independent_normalized_data() -> None:
    contract = _injected_contract()
    intel = load_crescent_city_intel(source=contract)
    domains = contract["domains"]
    assert isinstance(domains, list)
    first_domain = domains[0]
    assert isinstance(first_domain, dict)
    first_domain["name"] = "Changed after parsing"

    assert intel["domains"][0]["name"] == "Flood Policy"


def test_missing_contract_is_a_stable_empty_surface(tmp_path: Path) -> None:
    missing = tmp_path / "absent-geo-intel.json"

    assert load_crescent_city_intel(source=missing) == {
        "city": None,
        "domains": [],
        "hazardDomains": [],
        "bounds": None,
    }


def test_wrong_schema_and_inconsistent_counts_fail_closed(tmp_path: Path) -> None:
    wrong_schema = _injected_contract()
    wrong_schema["schema"] = "crescent-city-geo-intel/v2"
    with pytest.raises(ValueError, match="unexpected Crescent City intel schema"):
        load_crescent_city_intel(source=wrong_schema)

    wrong_count = _injected_contract()
    wrong_count["domainCount"] = 12
    with pytest.raises(ValueError, match="domainCount"):
        load_crescent_city_intel(source=wrong_count)

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid Crescent City intel JSON"):
        load_crescent_city_intel(source=invalid_json)


def test_seed_validation_does_not_advance_a_caller_generator() -> None:
    generator = np.random.default_rng(11)
    expected = np.random.default_rng(11).random()

    load_crescent_city_intel(seed=generator)

    assert generator.random() == expected
    with pytest.raises(TypeError, match="seed must be"):
        load_crescent_city_intel(seed="11")


def test_bundled_hazard_prior_table_counts_only_hazard_topic_sections() -> None:
    table = build_hazard_prior_table(load_crescent_city_intel())

    assert table == {
        "climate-environment": {
            "hazardTags": [
                "climate adaptation",
                "flood zone",
                "sea level rise",
                "wildfire smoke",
            ],
            "sectionCount": 5,
        },
        "emergency-management": {
            "hazardTags": ["seismic", "tsunami"],
            "sectionCount": 3,
        },
        "environmental-protection": {
            "hazardTags": ["erosion", "flood zone", "tsunami zone"],
            "sectionCount": 6,
        },
        "event-planning": {
            "hazardTags": ["tsunami drill"],
            "sectionCount": 2,
        },
    }


def test_default_prior_is_neutral_across_tags_and_section_weighted() -> None:
    table = build_hazard_prior_table(load_crescent_city_intel(source=_injected_contract()))
    prior = build_hazard_categorical_prior(table)

    assert DEFAULT_HAZARD_TAG_WEIGHTS["tsunami"] == 1.0
    assert DEFAULT_HAZARD_TAG_WEIGHTS["seismic"] == 1.0
    assert DEFAULT_HAZARD_TAG_WEIGHTS["flood"] == 1.0
    assert prior.domains == ("emergency-management", "flood-policy")
    assert prior.concentration == pytest.approx((4.0, 5.0))
    assert prior.as_probability_table() == pytest.approx(
        {"emergency-management": 4.0 / 9.0, "flood-policy": 5.0 / 9.0}
    )


def test_custom_hazard_weights_change_categorical_prior_concentration() -> None:
    table = build_hazard_prior_table(load_crescent_city_intel(source=_injected_contract()))
    prior = build_hazard_categorical_prior(
        table,
        hazard_weights={"tsunami": 3.0, "seismic": 1.0, "flood": 2.0},
    )

    assert prior.concentration == pytest.approx((7.0, 9.0))
    assert prior.probabilities == pytest.approx((7.0 / 16.0, 9.0 / 16.0))


def test_categorical_prior_sampling_replays_without_global_rng_state() -> None:
    table = build_hazard_prior_table(load_crescent_city_intel(source=_injected_contract()))
    prior = build_hazard_categorical_prior(table)

    assert prior.sample(64, seed=29) == prior.sample(64, seed=29)
    assert prior.sample(64, seed=29) != prior.sample(64, seed=30)

    np.random.seed(5)
    expected = np.random.random()
    np.random.seed(5)
    prior.sample(8, seed=3)
    assert np.random.random() == expected


def test_empty_and_invalid_prior_tables_are_explicit() -> None:
    empty = build_hazard_categorical_prior({})
    assert empty == HazardCategoricalPrior((), (), ())
    assert empty.sample(0, seed=1) == []
    with pytest.raises(ValueError, match="empty hazard categorical prior"):
        empty.sample(seed=1)

    no_tags: HazardPriorTable = {"emergency-management": {"hazardTags": [], "sectionCount": 3}}
    with pytest.raises(ValueError, match="hazardTags must not be empty"):
        build_hazard_categorical_prior(no_tags)

    with pytest.raises(ValueError, match="base_concentration must be positive"):
        build_hazard_categorical_prior(
            {"flood-policy": {"hazardTags": ["flood"], "sectionCount": 1}},
            base_concentration=0.0,
        )
