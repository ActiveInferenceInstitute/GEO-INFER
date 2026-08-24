"""Unit tests for Crescent City civic-intel ingestion and hazard policy-prior plating.

Covers parsing the ``crescent-city-geo-intel/v1`` contract (surfacing the
hazard-relevant domain subset) and the deterministic hazard prior that weights
policy selection away from notified municipal hazards.
"""

from typing import Any, Dict, List

import numpy as np
import pytest

from geo_infer_act import (
    CivicIntelBounds,
    CrescentCityIntel,
    HazardDomain,
    hazard_policy_prior,
    parse_crescent_city_intel,
)
from geo_infer_act.core.policy_selection import PolicySelector


def _hazard_contract_fixture() -> Dict[str, Any]:
    """A small inline crescent-city-geo-intel/v1 contract with a hazard subset."""
    return {
        "schema": "crescent-city-geo-intel/v1",
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
        "generatedAt": "2026-08-23T21:38:42.863Z",
        "domainCount": 12,
        "domains": [
            {
                "id": "emergency-management",
                "name": "Emergency Management",
                "tags": ["tsunami", "seismic", "evacuation"],
                "sections": [],
            },
            {
                "id": "business-development",
                "name": "Business Development",
                "tags": ["crabbing", "harbor"],
                "sections": [],
            },
        ],
        "hazard": {
            "relevantDomains": [
                {
                    "id": "emergency-management",
                    "name": "Emergency Management",
                    "icon": "🌊",
                    "hazardTags": ["seismic", "tsunami"],
                    "topics": [
                        {
                            "name": "Tsunami Preparedness & Evacuation",
                            "tags": ["tsunami", "seismic"],
                            "sections": [
                                {
                                    "sectionNumber": "§ 8.04",
                                    "relevance": "Health and Safety - emergency management authority",
                                }
                            ],
                        }
                    ],
                }
            ],
            "relevantDomainCount": 1,
        },
    }


class TestParseCrescentCityIntel:
    """Tests for lowering the geo-intel contract into an ACT record."""

    def test_parse_surfaces_hazard_subset(self) -> None:
        """The tsunami/seismic hazard domain is surfaced by the parser."""
        parsed = parse_crescent_city_intel(source=_hazard_contract_fixture())

        assert parsed["schema"] == "crescent-city-geo-intel/v1"
        assert parsed["city"] == "Crescent City"
        assert parsed["bounds"] == {
            "west": -124.408,
            "south": 41.458,
            "east": -123.536,
            "north": 42.006,
        }
        hazard_domains = parsed["hazardDomains"]
        assert len(hazard_domains) == 1
        assert hazard_domains[0]["id"] == "emergency-management"
        assert "tsunami" in hazard_domains[0]["hazardTags"]
        assert "seismic" in hazard_domains[0]["hazardTags"]

    def test_parse_surfaces_topic_sections(self) -> None:
        """The municipal code section nested under the hazard topic is retained."""
        parsed = parse_crescent_city_intel(source=_hazard_contract_fixture())
        topic = parsed["hazardDomains"][0]["topics"][0]
        assert topic["name"] == "Tsunami Preparedness & Evacuation"
        assert topic["sections"][0]["sectionNumber"] == "§ 8.04"

    def test_parse_is_deterministic_across_seeds(self) -> None:
        """Parsing output is identical regardless of the accepted seed."""
        base = parse_crescent_city_intel(
            seed=0, source=_hazard_contract_fixture()
        )
        reseeded = parse_crescent_city_intel(
            seed=42, source=_hazard_contract_fixture()
        )
        assert base["city"] == reseeded["city"]
        assert base["hazardDomains"] == reseeded["hazardDomains"]
        assert base["bounds"] == reseeded["bounds"]

    def test_parse_graceful_when_absent(self) -> None:
        """A missing contract degrades to an empty record rather than raising."""
        parsed = parse_crescent_city_intel(source="/nonexistent/geo-intel.json")
        assert parsed["city"] == ""
        assert parsed["hazardDomains"] == []
        assert parsed["bounds"] == {}

    def test_parse_rejects_non_schema_contract(self) -> None:
        """A contract without the supported schema id yields an empty record."""
        parsed = parse_crescent_city_intel(source={"schema": "other/v1", "anchor": {}})
        assert parsed["city"] == ""
        assert parsed["hazardDomains"] == []

    def test_typed_view_constructs(self) -> None:
        """The typed dataclass view is directly constructible."""
        domain = HazardDomain(
            id="emergency-management",
            name="Emergency Management",
            hazardTags=["tsunami", "seismic"],
        )
        bounds = CivicIntelBounds(west=-124.408, south=41.458, east=-123.536, north=42.006)
        record = CrescentCityIntel(
            city="Crescent City",
            hazardDomains=[domain],
            bounds=bounds,
            schema="crescent-city-geo-intel/v1",
        )
        assert record.as_dict()["city"] == "Crescent City"
        assert record.as_dict()["bounds"]["north"] == 42.006


class TestHazardPolicyPrior:
    """Tests for mapping hazard domains into PolicySelector preferences."""

    def test_prior_lowers_hazard_preferences(self) -> None:
        """Tsunami and seismic states are less preferred than the baseline."""
        parsed = parse_crescent_city_intel(source=_hazard_contract_fixture())
        prior = hazard_policy_prior(parsed)

        assert prior["deterministic"] is True
        assert prior["hazardTags"] == ["seismic", "tsunami"]
        assert prior["dominantHazard"] == "tsunami"
        preferences = prior["preferences"]
        # Axis: [baseline(all-clear), seismic, tsunami]
        assert preferences[0] == pytest.approx(
            np.max(preferences), rel=1e-6
        )
        assert preferences[2] < preferences[1] < preferences[0]
        assert preferences[0] >= 0.5
        assert float(np.sum(preferences)) == pytest.approx(1.0, abs=1e-9)

    def test_prior_accepts_raw_contract_dict(self) -> None:
        """The prior consumes a raw contract even without a prior parse."""
        prior = hazard_policy_prior(_hazard_contract_fixture())
        assert prior["hazardTags"] == ["seismic", "tsunami"]
        assert prior["deterministic"] is True

    def test_prior_empty_when_no_hazard_signal(self) -> None:
        """A contract without hazard domains yields a baseline-only prior."""
        flat = {"schema": "crescent-city-geo-intel/v1", "anchor": {"name": "X"}, "hazard": {}}
        prior = hazard_policy_prior(parse_crescent_city_intel(source=flat))
        assert prior["hazardTags"] == []
        assert prior["dominantHazard"] is None
        assert len(prior["preferences"]) == 1
        assert float(prior["preferences"][0]) == pytest.approx(1.0)

    def test_prior_deterministic_repeat(self) -> None:
        """Seed-default reproduction is stable across calls."""
        contract = _hazard_contract_fixture()
        first = hazard_policy_prior(parse_crescent_city_intel(source=contract))
        second = hazard_policy_prior(parse_crescent_city_intel(source=contract))
        np.testing.assert_array_equal(first["preferences"], second["preferences"])

    def test_seeded_hedge_is_reproducible(self) -> None:
        """A seeded hedge is stable while a deterministic default stays fixed."""
        contract = _hazard_contract_fixture()
        parsed = parse_crescent_city_intel(source=contract)
        base = hazard_policy_prior(parsed, seed=None)
        hedged_a = hazard_policy_prior(parsed, seed=7, hedge_share=0.2)
        hedged_b = hazard_policy_prior(parsed, seed=7, hedge_share=0.2)
        np.testing.assert_array_equal(hedged_a["preferences"], hedged_b["preferences"])
        assert hedged_a["deterministic"] is False
        assert not np.allclose(base["preferences"], hedged_a["preferences"])


class TestPolicyCoupling:
    """Verify the hazard prior drives a deterministic lowest-EFE selection."""

    def test_deterministic_selection_avoids_notified_hazards(self) -> None:
        """The policy predicting the all-clear state wins under the hazard prior."""
        parsed = parse_crescent_city_intel(source=_hazard_contract_fixture())
        prior = hazard_policy_prior(parsed)

        policies: List[Dict[str, Any]] = [
            {
                "id": "maintain_normal_ops",
                "predicted_beliefs": [1.0, 0.0, 0.0],
            },
            {
                "id": "shore_up_structures",
                "predicted_beliefs": [0.0, 1.0, 0.0],
            },
            {
                "id": "approach_waterfront",
                "predicted_beliefs": [0.0, 0.0, 1.0],
            },
        ]
        beliefs = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        selector = PolicySelector(selection_mode="deterministic", random_seed=11)

        result = selector.select_policy(beliefs, policies, preferences=prior)
        evaluation = selector.evaluate_policy_set(
            beliefs, policies, preferences=prior
        )

        assert result["selected_index"] == 0
        assert result["policy"]["id"] == "maintain_normal_ops"
        assert evaluation["best_policy_idx"] == 0
        # The safe policy has the lowest expected free energy.
        energies = evaluation["expected_free_energies"]
        assert energies[0] < energies[1]
        assert energies[0] < energies[2]

    def test_deterministic_rule_matches_manual_efe(self) -> None:
        """Selection equals argmin of the computed expected free energies."""
        parsed = parse_crescent_city_intel(source=_hazard_contract_fixture())
        prior = hazard_policy_prior(parsed)
        policies = [
            {"id": "safe", "predicted_beliefs": [1.0, 0.0, 0.0]},
            {"id": "hazard", "predicted_beliefs": [0.0, 0.0, 1.0]},
        ]
        beliefs = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        selector = PolicySelector(selection_mode="deterministic")
        result = selector.select_policy(beliefs, policies, preferences=prior)
        assert result["selected_index"] == int(
            np.argmin(result["all_free_energies"])
        )
        assert result["policy"]["id"] == "safe"