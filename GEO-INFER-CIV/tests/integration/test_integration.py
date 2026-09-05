"""Integration tests for GEO-INFER-CIV.

Exercises a civic-engagement workflow end to end: participation records
feed engagement, participation-index, and representation analysis, and a
cost-benefit appraisal scores the resulting proposal.
"""

import pytest

from geo_infer_civ import (
    CostBenefitAnalyzer,
    CostBenefitItem,
    ParticipantRecord,
    ParticipationAnalyzer,
    ParticipationMethod,
)

TARGET_POPULATION = 100
POPULATION_DEMOGRAPHICS = {"north": 0.5, "south": 0.3, "east": 0.2}


@pytest.fixture(name="records")
def _records():
    methods = list(ParticipationMethod)
    groups = ["north", "south", "north", "east", "south", "north"]
    return [
        ParticipantRecord(
            participant_id=f"p{index}",
            method=methods[index % len(methods)],
            timestamp=1_700_000_000.0 + index * 3600,
            demographic_group=group,
            location=(41.0 + index * 0.01, -124.0 - index * 0.01),
            sentiment_score=0.5 - index * 0.1,
        )
        for index, group in enumerate(groups)
    ]


@pytest.fixture(name="analyzer")
def _analyzer(records):
    analyzer = ParticipationAnalyzer()
    analyzer.add_records(records)
    return analyzer


class TestParticipationAnalysis:
    def test_summary_counts_every_record(self, analyzer, records):
        """Ingested records are all reflected in the summary."""
        summary = analyzer.get_participation_summary()
        assert summary["total_records"] == len(records)
        assert summary["unique_participants"] == len(records)

    def test_engagement_score_components_are_normalized(self, analyzer):
        """Every reported engagement component is a proper ratio."""
        score = analyzer.compute_engagement_score(TARGET_POPULATION)
        assert 0.0 <= score.overall_score <= 1.0
        assert 0.0 <= score.diversity_index <= 1.0
        assert score.reach_ratio == pytest.approx(6 / TARGET_POPULATION)

    def test_engagement_rises_with_participation(self, records):
        """More participants over the same population raises reach."""
        few = ParticipationAnalyzer()
        few.add_records(records[:2])
        many = ParticipationAnalyzer()
        many.add_records(records)
        assert (
            many.compute_engagement_score(TARGET_POPULATION).reach_ratio
            > few.compute_engagement_score(TARGET_POPULATION).reach_ratio
        )

    def test_participation_index_is_relative_to_baseline(self, analyzer):
        """The index is actual-rate / baseline-rate: 1.0 at baseline, >1 above."""
        index = analyzer.compute_participation_index(TARGET_POPULATION)
        assert isinstance(index, float)
        assert index > 0.0
        # 6 unique participants over 100 residents = 0.06 actual rate.
        assert index == pytest.approx(0.06 / 0.10)
        # Turnout above the baseline must score above 1.0.
        assert (
            analyzer.compute_participation_index(TARGET_POPULATION, baseline_rate=0.05) > 1.0
        )

    def test_representation_covers_every_group(self, analyzer):
        """Each demographic group in the population is reported on."""
        report = analyzer.analyze_representation(POPULATION_DEMOGRAPHICS)
        assert set(report.group_proportions) == {"north", "south", "east"}
        assert report.group_proportions["north"] == pytest.approx(0.5, abs=0.01)

    def test_representation_identifies_a_skewed_group(self, analyzer):
        """A group that turns out far below its share is flagged."""
        report = analyzer.analyze_representation({"north": 0.1, "south": 0.1, "east": 0.8})
        assert "east" in report.underrepresented_groups
        assert "north" in report.overrepresented_groups

    def test_clearing_records_resets_the_summary(self, analyzer):
        """Cleared state is genuinely empty, not stale."""
        analyzer.clear_records()
        assert analyzer.get_participation_summary()["total_records"] == 0


class TestCostBenefitAppraisal:
    def test_net_positive_proposal_is_scored_positive(self):
        """Benefits exceeding costs produce a positive net position."""
        analyzer = CostBenefitAnalyzer(discount_rate=0.05)
        analyzer.add_items(
            [
                CostBenefitItem("construction", 250_000.0, is_benefit=False),
                CostBenefitItem(
                    "flood avoidance", 900_000.0, is_benefit=True, time_horizon_years=10
                ),
            ]
        )
        assert analyzer.analyze().net_present_value > 0

    def test_net_negative_proposal_is_scored_negative(self):
        """Costs exceeding benefits produce a negative net position."""
        analyzer = CostBenefitAnalyzer(discount_rate=0.05)
        analyzer.add_items(
            [
                CostBenefitItem("construction", 900_000.0, is_benefit=False),
                CostBenefitItem("minor saving", 10_000.0, is_benefit=True),
            ]
        )
        assert analyzer.analyze().net_present_value < 0

    def test_discounting_reduces_deferred_benefit_value(self):
        """A higher discount rate lowers a far-future benefit's present value."""
        def npv(rate):
            analyzer = CostBenefitAnalyzer(discount_rate=rate)
            analyzer.add_item(
                CostBenefitItem(
                    "deferred", 1_000_000.0, is_benefit=True, time_horizon_years=20
                )
            )
            return analyzer.analyze().net_present_value

        assert npv(0.01) > npv(0.15)

    def test_probability_weights_the_risk_adjusted_result_only(self):
        """Probability discounts risk-adjusted NPV while leaving raw NPV alone.

        Raw NPV is deliberately unadjusted; the probability of occurrence
        belongs to the risk-adjusted figure.
        """
        def result(probability):
            analyzer = CostBenefitAnalyzer(discount_rate=0.05)
            analyzer.add_item(
                CostBenefitItem("uncertain", 500_000.0, is_benefit=True, probability=probability)
            )
            return analyzer.analyze()

        certain, uncertain = result(1.0), result(0.25)
        assert certain.risk_adjusted_npv > uncertain.risk_adjusted_npv
        assert certain.net_present_value == uncertain.net_present_value
        assert uncertain.risk_adjusted_npv == pytest.approx(
            certain.risk_adjusted_npv * 0.25, rel=1e-6
        )
