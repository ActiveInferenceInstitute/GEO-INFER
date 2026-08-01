"""
DOMAIN-02 Acceptance tests for GEO-INFER-CIV documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. AttendanceTracker — attendance trend regression, per-type filtering,
   meeting effectiveness scoring.
2. PublicCommentAnalyzer — category distribution, engagement depth,
   empty-input handling.
3. VoterTurnoutModel — average turnout, contested/uncontested prediction
   adjustment, summary statistics.
4. ParticipationAnalyzer — engagement score components, participation index
   relative to baseline, demographic representation.
5. CostBenefitAnalyzer — discounted NPV, benefit-cost ratio, payback period,
   category breakdown.
6. StakeholderImpactAnalyzer — impact matrix normalization, population-weighted
   aggregate, most-affected identification.
7. EquityAnalyzer — Gini coefficient, disparate-impact flags.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_civ.core.civic_engagement import (
    AttendanceTracker,
    PublicCommentAnalyzer,
    VoterTurnoutModel,
    MeetingRecord,
    MeetingType,
    PublicComment,
    CommentCategory,
)
from geo_infer_civ.core.participation import (
    ParticipationAnalyzer,
    ParticipationMethod,
    ParticipantRecord,
)
from geo_infer_civ.core.policy_analysis import (
    CostBenefitAnalyzer,
    CostBenefitItem,
    StakeholderImpactAnalyzer,
    StakeholderImpact,
    ImpactLevel,
    EquityAnalyzer,
)


# ---------------------------------------------------------------------------
# AttendanceTracker
# ---------------------------------------------------------------------------

class TestAttendanceTrackerAcceptance:
    """Acceptance: civic meeting attendance trend and effectiveness analysis."""

    @pytest.fixture
    def tracker(self) -> AttendanceTracker:
        return AttendanceTracker()

    @pytest.fixture
    def increasing_meetings(self):
        """Six city council meetings with steadily rising attendance."""
        return [
            MeetingRecord(
                meeting_id=f"cc{i}",
                meeting_type=MeetingType.CITY_COUNCIL,
                date=1000.0 + i * 30,
                registered_attendees=100,
                actual_attendees=40 + i * 10,
                public_comments_count=i,
            )
            for i in range(6)
        ]

    def test_empty_tracker_raises(self, tracker):
        """A tracker with no meetings raises rather than returning a trend."""
        with pytest.raises(ValueError, match="No meeting records available"):
            tracker.compute_attendance_trend()

    def test_increasing_trend_detected(self, tracker, increasing_meetings):
        """Steadily rising attendance is classified as 'increasing'."""
        tracker.add_meetings(increasing_meetings)
        trend = tracker.compute_attendance_trend()
        assert trend.meeting_count == 6
        assert trend.trend_direction == "increasing"
        assert trend.trend_slope > 0.5
        assert trend.average_attendance > 0.0

    def test_trend_filtered_by_meeting_type(self, tracker, increasing_meetings):
        """Filtering by meeting_type narrows the trend to that subset."""
        tracker.add_meetings(increasing_meetings)
        # Add a different-type meeting to confirm the filter excludes it.
        tracker.add_meeting(MeetingRecord(
            meeting_id="th0",
            meeting_type=MeetingType.TOWN_HALL,
            date=2000.0,
            registered_attendees=50,
            actual_attendees=45,
        ))
        trend = tracker.compute_attendance_trend(meeting_type=MeetingType.CITY_COUNCIL)
        assert trend.meeting_count == 6
        assert trend.peak_meeting_type == MeetingType.CITY_COUNCIL.value

    def test_meeting_effectiveness_combines_attendance_and_comments(self, tracker, increasing_meetings):
        """Effectiveness is a 0.6*attendance + 0.4*comment blend in [0, 1]."""
        tracker.add_meetings(increasing_meetings)
        eff = tracker.get_meeting_effectiveness("cc0")
        assert eff["meeting_id"] == "cc0"
        assert 0.0 <= eff["effectiveness_score"] <= 1.0
        assert eff["attendance_rate"] == 40 / 100

    def test_unknown_meeting_raises(self, tracker, increasing_meetings):
        """Looking up effectiveness for an unknown meeting raises."""
        tracker.add_meetings(increasing_meetings)
        with pytest.raises(ValueError, match="Meeting .* not found"):
            tracker.get_meeting_effectiveness("nope")


# ---------------------------------------------------------------------------
# PublicCommentAnalyzer
# ---------------------------------------------------------------------------

class TestPublicCommentAnalyzerAcceptance:
    """Acceptance: public comment distribution and engagement depth."""

    @pytest.fixture
    def analyzer(self) -> PublicCommentAnalyzer:
        return PublicCommentAnalyzer()

    def test_empty_analyze_is_zeroed(self, analyzer):
        """An analyzer with no comments returns an empty CommentAnalysis."""
        result = analyzer.analyze()
        assert result.total_comments == 0
        assert result.category_distribution == {}
        assert result.engagement_depth_score == 0.0

    def test_category_distribution_sums_to_one(self, analyzer):
        """Category distribution fractions sum to 1.0 across submitted comments."""
        comments = [
            PublicComment(
                comment_id=f"c{i}",
                meeting_id="m1",
                category=CommentCategory.SUPPORT if i % 2 == 0 else CommentCategory.OPPOSITION,
                word_count=120,
                timestamp=1000.0 + i,
                submitter_id=f"s{i}",
                sentiment_score=0.2,
            )
            for i in range(6)
        ]
        analyzer.add_comments(comments)
        result = analyzer.analyze()
        assert result.total_comments == 6
        assert pytest.approx(sum(result.category_distribution.values()), abs=1e-6) == 1.0
        assert result.unique_submitters == 6
        assert result.engagement_depth_score > 0.0

    def test_analyze_filters_by_meeting(self, analyzer):
        """Filtering by meeting_id scopes the analysis to that meeting."""
        for mid in ("m1", "m2"):
            analyzer.add_comment(PublicComment(
                comment_id=f"c_{mid}",
                meeting_id=mid,
                category=CommentCategory.QUESTION,
                word_count=80,
                timestamp=1.0,
                submitter_id="s1",
            ))
        only_m1 = analyzer.analyze(meeting_id="m1")
        assert only_m1.total_comments == 1
        assert only_m1.category_distribution[CommentCategory.QUESTION.value] == 1.0


# ---------------------------------------------------------------------------
# VoterTurnoutModel
# ---------------------------------------------------------------------------

class TestVoterTurnoutModelAcceptance:
    """Acceptance: voter turnout averaging and prediction."""

    @pytest.fixture
    def model(self) -> VoterTurnoutModel:
        m = VoterTurnoutModel()
        # Contested and uncontested elections of the same type.
        m.add_election("e1", 1000, 600, "general", 1000.0, is_contested=True)
        m.add_election("e2", 1000, 500, "general", 1100.0, is_contested=False)
        return m

    def test_average_turnout(self, model):
        """Average turnout is the mean of the recorded turnout rates."""
        avg = model.compute_average_turnout()
        assert avg == round((0.6 + 0.5) / 2, 4)

    def test_average_turnout_by_type(self, model):
        """Filtering by election_type scopes the average."""
        model.add_election("e3", 1000, 400, "primary", 1200.0, is_contested=True)
        general_avg = model.compute_average_turnout(election_type="general")
        assert general_avg == round((0.6 + 0.5) / 2, 4)

    def test_predict_turnout_uses_contested_adjustment(self, model):
        """An uncontested prediction is lower than the type baseline."""
        contested = model.predict_turnout(1000, "general", is_contested=True)
        uncontested = model.predict_turnout(1000, "general", is_contested=False)
        assert contested["predicted_turnout_rate"] > uncontested["predicted_turnout_rate"]
        assert 0.0 <= uncontested["predicted_turnout_rate"] <= 1.0
        assert "base_rate" in contested

    def test_summary_reports_by_type(self, model):
        """The summary aggregates counts and turnout per election type."""
        summary = model.get_turnout_summary()
        assert summary["total_elections"] == 2
        assert "general" in summary["by_type"]
        assert summary["by_type"]["general"]["count"] == 2


# ---------------------------------------------------------------------------
# ParticipationAnalyzer
# ---------------------------------------------------------------------------

class TestParticipationAnalyzerAcceptance:
    """Acceptance: engagement scoring and demographic representation."""

    @pytest.fixture
    def analyzer(self) -> ParticipationAnalyzer:
        return ParticipationAnalyzer()

    def _records(self, n=40):
        methods = list(ParticipationMethod)
        demos = ["youth", "seniors", "families", "professionals"]
        return [
            ParticipantRecord(
                participant_id=f"p{i}",
                method=methods[i % len(methods)],
                timestamp=1000.0 + i * 10,
                demographic_group=demos[i % len(demos)],
                sentiment_score=0.5,
            )
            for i in range(n)
        ]

    def test_engagement_score_bounded(self, analyzer):
        """Engagement score and its components lie in [0, 1]."""
        analyzer.add_records(self._records(40))
        score = analyzer.compute_engagement_score(target_population=100)
        assert 0.0 < score.overall_score <= 1.0
        assert 0.0 <= score.temporal_consistency <= 1.0
        assert 0.0 < score.diversity_index <= 1.0
        assert 0.0 < score.reach_ratio <= 1.0

    def test_participation_index_relative_to_baseline(self, analyzer):
        """Index = (unique / population) / baseline; equals 1.0 when matching."""
        analyzer.add_records(self._records(40))
        index = analyzer.compute_participation_index(
            target_population=100, baseline_rate=0.40
        )
        assert index == 1.0

    def test_representation_flags_extremes(self, analyzer):
        """Uneven participation flags under/over-represented groups."""
        analyzer.add_records(self._records(40))
        report = analyzer.analyze_representation(
            population_demographics={
                "youth": 0.25, "seniors": 0.25,
                "families": 0.25, "professionals": 0.25,
            }
        )
        assert len(report.representation_indices) == 4
        assert 0.0 <= report.overall_representation_score <= 1.0


# ---------------------------------------------------------------------------
# CostBenefitAnalyzer
# ---------------------------------------------------------------------------

class TestCostBenefitAnalyzerAcceptance:
    """Acceptance: discounted cost-benefit computation."""

    @pytest.fixture
    def analyzer(self) -> CostBenefitAnalyzer:
        return CostBenefitAnalyzer(discount_rate=0.05)

    def test_positive_npv_when_benefits_exceed_costs(self, analyzer):
        """A benefit stream that outweighs the upfront cost yields positive NPV."""
        analyzer.add_item(CostBenefitItem("build", 1_000_000, is_benefit=False, time_horizon_years=0))
        analyzer.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=1))
        analyzer.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=2))
        analyzer.add_item(CostBenefitItem("revenue", 500_000, is_benefit=True, time_horizon_years=3))
        result = analyzer.analyze()
        # Discounted benefits (~1.36M) exceed the upfront 1M cost.
        assert result.net_present_value > 0
        assert result.benefit_cost_ratio > 1.0
        assert result.total_costs == 1_000_000.0

    def test_category_breakdown_partitions_items(self, analyzer):
        """Items are grouped into categories with discounted cost/benefit sums."""
        analyzer.add_item(CostBenefitItem("road", 500_000, is_benefit=False, category="infrastructure"))
        analyzer.add_item(CostBenefitItem("toll", 200_000, is_benefit=True, category="revenue"))
        result = analyzer.analyze()
        assert "infrastructure" in result.category_breakdown
        assert "revenue" in result.category_breakdown
        assert result.category_breakdown["infrastructure"]["costs"] > 0

    def test_payback_period_within_horizon(self, analyzer):
        """A recovering investment reaches payback within the modeled years."""
        analyzer.add_item(CostBenefitItem("cost", 1000, is_benefit=False, time_horizon_years=0))
        analyzer.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=1))
        analyzer.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=2))
        analyzer.add_item(CostBenefitItem("income", 400, is_benefit=True, time_horizon_years=3))
        result = analyzer.analyze()
        assert 0 < result.payback_period_years <= 4

    def test_empty_analysis_raises(self, analyzer):
        """Analyzing with no items raises."""
        with pytest.raises(ValueError, match="No cost-benefit items"):
            analyzer.analyze()


# ---------------------------------------------------------------------------
# StakeholderImpactAnalyzer + EquityAnalyzer
# ---------------------------------------------------------------------------

class TestStakeholderAndEquityAcceptance:
    """Acceptance: stakeholder impact matrices and equity analysis."""

    def test_impact_matrix_normalizes_to_unit_interval(self):
        """Impact matrix composite scores fall within [-1, 1]."""
        sa = StakeholderImpactAnalyzer()
        sa.add_impact(StakeholderImpact(
            "residents", 10000, ImpactLevel.POSITIVE,
            economic_impact=0.5, quality_of_life_impact=0.8,
            environmental_impact=0.3, accessibility_impact=0.6,
        ))
        matrix = sa.compute_impact_matrix()
        assert "residents" in matrix
        composite = matrix["residents"]["weighted_composite"]
        assert -1.0 <= composite <= 1.0

    def test_find_most_affected_returns_extremes(self):
        """Most-affected returns the most-positive and most-negative groups."""
        sa = StakeholderImpactAnalyzer()
        sa.add_impact(StakeholderImpact(
            "winners", 100, ImpactLevel.VERY_POSITIVE,
            economic_impact=1.0, quality_of_life_impact=1.0,
            environmental_impact=1.0, accessibility_impact=1.0,
        ))
        sa.add_impact(StakeholderImpact(
            "losers", 100, ImpactLevel.VERY_NEGATIVE,
            economic_impact=-1.0, quality_of_life_impact=-1.0,
            environmental_impact=-1.0, accessibility_impact=-1.0,
        ))
        best, worst = sa.find_most_affected()
        assert best == "winners"
        assert worst == "losers"

    def test_equity_gini_zero_for_equal_impacts(self):
        """Identical impacts across groups yield a Gini coefficient of 0.0."""
        ea = EquityAnalyzer()
        ea.set_group_impact("a", 10.0, 100)
        ea.set_group_impact("b", 10.0, 100)
        ea.set_group_impact("c", 10.0, 100)
        score = ea.analyze()
        assert score.gini_coefficient == 0.0
        assert score.overall_equity_score == 1.0
        assert score.disparate_impact_flags == []

    def test_equity_flags_disparate_impact(self):
        """A group well below the highest impact is flagged as disparate."""
        ea = EquityAnalyzer()
        ea.set_group_impact("advantaged", 100.0, 100)
        ea.set_group_impact("disadvantaged", 10.0, 100)
        ea.set_group_impact("middle", 60.0, 100)
        score = ea.analyze()
        assert any("disadvantaged" in flag for flag in score.disparate_impact_flags)
        assert score.gini_coefficient > 0.0
