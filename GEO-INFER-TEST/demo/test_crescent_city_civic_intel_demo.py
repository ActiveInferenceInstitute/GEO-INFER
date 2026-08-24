"""Tests for the Crescent City civic-intel end-to-end consumer example.

Pins the pure :func:`crescent_city_civic_intel_demo.build_summary` digest to
the same bundled ``crescent-city-geo-intel/v1`` seed the demo consumes at
runtime, so a future contract or module change is surfaced here in one place
instead of silently diverging between RISK, BAYES and ACT.

Real modules only: the summary is generated through the actual civic-intel
ingestors and the deterministic ACT ``PolicySelector``, never against a stand-in.
"""

from __future__ import annotations

import pytest

from demo.crescent_city_civic_intel_demo import (
    build_geo_parity,
    build_summary,
    bundled_contract_path,
    geo_views_agree,
    load_bundled_contract,
)

_HAZARD_DOMAIN_IDS = {
    "emergency-management",
    "environmental-protection",
    "event-planning",
    "climate-environment",
}

_EXPECTED_SCHEMA = "crescent-city-geo-intel/v1"

_EXPECTED_BOUNDS = {
    "west": -124.408,
    "south": 41.458,
    "east": -123.536,
    "north": 42.006,
}


def _seed_summary() -> dict[str, object]:
    """Build the digest exactly once from the byte-identical bundled seed."""
    return build_summary(load_bundled_contract())


def _seed_parity() -> dict[str, object]:
    """Build the geo-parity digest exactly once from the bundled seed."""
    return build_geo_parity(load_bundled_contract())


def test_bundled_seed_is_the_expected_schema() -> None:
    """The resolved bundled seed is a crescent-city-geo-intel/v1 contract."""
    contract = load_bundled_contract()
    assert contract["schema"] == _EXPECTED_SCHEMA
    # The seed resolves to an existing bundled copy on disk.
    assert bundled_contract_path().exists()


def test_summary_is_deterministic_across_calls() -> None:
    """Repeated digests over the same seed are byte-for-byte identical."""
    contract = load_bundled_contract()
    assert build_summary(contract) == build_summary(contract)


def test_geo_parity_is_deterministic_across_calls() -> None:
    """Repeated parity digests over the same seed are byte-for-byte identical."""
    contract = load_bundled_contract()
    assert build_geo_parity(contract) == build_geo_parity(contract)


def test_geo_views_agree_on_the_bundled_seed() -> None:
    """Every importable module lowers the seed to an agreeing geo view."""
    contract = load_bundled_contract()
    assert geo_views_agree(contract) is True


def test_geo_parity_surfaces_all_three_modules() -> None:
    """RISK, BAYES and ACT are all sighted and none is skipped."""
    parity = _seed_parity()
    assert parity["sighted"] == ["risk", "bayes", "act"]
    assert parity["skipped"] == []
    assert set(parity["moduleViews"]) == {"risk", "bayes", "act"}


def test_geo_parity_contract_schema_agrees_everywhere() -> None:
    """The contract schema and every module view schema match v1."""
    parity = _seed_parity()
    assert parity["contractSchema"] == _EXPECTED_SCHEMA
    assert parity["schemaAgreement"] is True
    for view in parity["moduleViews"].values():
        assert view["schema"] == _EXPECTED_SCHEMA


def test_geo_parity_bounds_agree_with_the_contract_anchor() -> None:
    """Every module view reproduces the contract's WGS84 bounds."""
    parity = _seed_parity()
    assert parity["bounds"] == _EXPECTED_BOUNDS
    assert parity["boundsAgreement"] is True


def test_geo_parity_anchor_agrees_with_the_contract_anchor() -> None:
    """Every module view reproduces the Crescent City anchor identity."""
    parity = _seed_parity()
    anchor = parity["anchor"]
    assert anchor["name"] == "Crescent City"
    assert anchor["county"] == "Del Norte County"
    assert anchor["state"] == "California"
    assert anchor["latitude"] == pytest.approx(41.76)
    assert anchor["longitude"] == pytest.approx(-124.2)
    assert parity["anchorAgreement"] is True


def test_geo_parity_nominal_domain_points_agree() -> None:
    """The four hazard-domain points surface across module views."""
    parity = _seed_parity()
    domain_ids = {domain["id"] for domain in parity["domains"]}
    assert domain_ids == _HAZARD_DOMAIN_IDS
    assert parity["domainPointsAgreement"] is True


def test_geo_parity_section_references_agree_per_domain() -> None:
    """Hazard-weighted municipal-code section refs match across all modules."""
    parity = _seed_parity()
    assert parity["sectionAgreement"] is True
    for domain_id in _HAZARD_DOMAIN_IDS:
        refs = parity["section_refs"][domain_id]
        assert isinstance(refs, list) and refs
        # Every sighted module surfaces the identical ordered ref list.
        for view in parity["moduleViews"].values():
            assert view["sections"][domain_id] == refs


def test_geo_parity_match_is_true_on_the_seed() -> None:
    """Full parity (schema, bounds, anchor, domains, sections) holds."""
    parity = _seed_parity()
    assert parity["match"] is True


def test_summary_surfaces_crescent_city_anchor() -> None:
    """The anchor block carries Crescent City identity and WGS84 geometry."""
    summary = _seed_summary()
    anchor = summary["anchor"]
    assert isinstance(anchor, dict)
    assert anchor["name"] == "Crescent City"
    assert anchor["county"] == "Del Norte County"
    assert anchor["state"] == "California"
    assert anchor["latitude"] == pytest.approx(41.76)
    assert anchor["longitude"] == pytest.approx(-124.2)


def test_summary_lists_the_four_hazard_domains() -> None:
    """The contract hazard subset surfaces exactly the four expected domains."""
    summary = _seed_summary()
    domains = summary["hazard_domains"]
    assert isinstance(domains, list)
    assert {d["id"] for d in domains} == _HAZARD_DOMAIN_IDS


def test_risk_weights_follow_municipal_code_evidence() -> None:
    """RISK weights normalize section evidence (flood zone peaks at 1.0)."""
    risk = _seed_summary()["risk"]
    assert isinstance(risk, dict)
    assert risk["available"] is True
    weights = risk["weights"]
    assert isinstance(weights, dict)
    assert weights["flood zone"] == pytest.approx(1.0, abs=1e-3)
    assert weights["tsunami"] == pytest.approx(0.5, abs=1e-3)
    assert weights["tsunami drill"] == pytest.approx(0.333, abs=1e-3)
    # The most-evidenced tag is the normalisation anchor.
    assert risk["top"] == ("flood zone", pytest.approx(1.0, abs=1e-3))


def test_bayes_prior_is_a_normalized_categorical_table() -> None:
    """BAYES prior probabilities are deterministic and sum to one."""
    bayes = _seed_summary()["bayes"]
    assert isinstance(bayes, dict)
    assert bayes["available"] is True
    probabilities = bayes["prior"]
    assert isinstance(probabilities, dict)
    assert set(probabilities) == _HAZARD_DOMAIN_IDS
    assert sum(probabilities.values()) == pytest.approx(1.0, abs=1e-3)
    assert probabilities["environmental-protection"] == pytest.approx(0.35, abs=1e-3)
    assert probabilities["event-planning"] == pytest.approx(0.15, abs=1e-3)


def test_act_decision_avoids_the_dominant_hazard() -> None:
    """ACT picks the deterministic all-clear action under the hazard prior."""
    act = _seed_summary()["act"]
    assert isinstance(act, dict)
    assert act["available"] is True
    assert act["dominantHazard"] == "tsunami"
    assert act["decision"]["policy_id"] == "maintain_baseline_ops"
    # The all-clear state is the most preferred axis of the prior vector.
    assert act["preferences"][0] == max(act["preferences"])


def test_geo_parity_is_embedded_in_the_summary() -> None:
    """The summary carries the geo-parity block alongside the module sections."""
    summary = _seed_summary()
    assert "geo_parity" in summary


def test_render_summary_mentions_every_module() -> None:
    """The human-readable summary text covers anchor, domains, all modules and parity."""
    from demo.crescent_city_civic_intel_demo import render_summary

    rendered = render_summary(_seed_summary())
    assert "Crescent City" in rendered
    assert "hazard domains (4)" in rendered
    assert "RISK" in rendered
    assert "BAYES" in rendered
    assert "ACT" in rendered
    assert "maintain_baseline_ops" in rendered
    assert "geo view parity" in rendered
    assert "modules sighted" in rendered
    assert "match         : yes" in rendered
