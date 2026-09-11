"""Behavioral tests for the underwriting decision engine (GS-146).

Covers DecisionCriteria operator/threshold semantics, framework scoring,
and UnderwritingDecisionEngine boundary decisions (automatic approve,
manual-review refer, decline).
"""

from geo_infer_insurance.underwriting.core.underwriting_decisions import (
    DecisionCriteria,
    DecisionCriterion,
    DecisionFramework,
    DecisionType,
    UnderwritingDecisionEngine,
)


class TestDecisionCriteria:
    def test_greater_equal_threshold_semantics(self) -> None:
        criteria = DecisionCriteria(
            DecisionCriterion.PREMIUM_ADEQUACY, threshold=1.0, operator="greater_equal"
        )

        assert criteria.evaluate(1.0) is True
        assert criteria.evaluate(0.99) is False

    def test_less_equal_threshold_semantics(self) -> None:
        criteria = DecisionCriteria(
            DecisionCriterion.RISK_SCORE, threshold=0.7, operator="less_equal"
        )

        assert criteria.evaluate(0.7) is True
        assert criteria.evaluate(0.71) is False

    def test_equals_uses_tolerance(self) -> None:
        criteria = DecisionCriteria(
            DecisionCriterion.LOSS_HISTORY, threshold=0.1, operator="equals"
        )

        assert criteria.evaluate(0.1005) is True
        assert criteria.evaluate(0.2) is False

    def test_between_uses_threshold_values_window(self) -> None:
        criteria = DecisionCriteria(
            DecisionCriterion.COVERAGE_LIMITS,
            operator="between",
            threshold_values=[0.2, 0.8],
        )

        assert criteria.evaluate(0.2) is True
        assert criteria.evaluate(0.8) is True
        assert criteria.evaluate(0.9) is False

    def test_between_without_threshold_values_never_passes(self) -> None:
        criteria = DecisionCriteria(
            DecisionCriterion.COVERAGE_LIMITS, operator="between", threshold_values=[]
        )

        assert criteria.evaluate(0.5) is False

    def test_score_direction_depends_on_criteria_type(self) -> None:
        risk = DecisionCriteria(DecisionCriterion.RISK_SCORE, weight=1.0, threshold=0.7)
        adequacy = DecisionCriteria(
            DecisionCriterion.PREMIUM_ADEQUACY, weight=1.0, threshold=1.0
        )

        assert risk.get_score(0.3) == 0.7
        assert risk.get_score(1.5) == 0.0
        assert adequacy.get_score(0.5) > 0.0
        assert adequacy.get_score(2.0) == 1.0


class TestDecisionFrameworkScoring:
    def _framework(self) -> DecisionFramework:
        return DecisionFramework(
            framework_name="Scoring Test",
            decision_criteria=[
                DecisionCriteria(
                    DecisionCriterion.RISK_SCORE, weight=0.4, threshold=0.7
                ),
                DecisionCriteria(
                    DecisionCriterion.PREMIUM_ADEQUACY, weight=0.3, threshold=1.0
                ),
                DecisionCriteria(
                    DecisionCriterion.COVERAGE_LIMITS, weight=0.2, threshold=1.0
                ),
                DecisionCriteria(
                    DecisionCriterion.COMPLIANCE, weight=0.1, threshold=0.9
                ),
            ],
        )

    def test_criteria_values_read_from_assessment_data(self) -> None:
        framework = self._framework()

        results = framework.evaluate_decision_criteria(
            {"risk_score": 0.2, "premium_adequacy": 1.5}
        )

        assert results["risk_score"]["value"] == 0.2
        assert results["premium_adequacy"]["value"] == 1.5
        assert results["coverage_limits"]["value"] == 1.0
        assert results["compliance"]["value"] == 1.0

    def test_overall_score_is_weighted_average(self) -> None:
        framework = self._framework()

        results = framework.evaluate_decision_criteria(
            {"risk_score": 0.2, "premium_adequacy": 1.0, "coverage_adequacy": 1.0}
        )
        overall = framework.calculate_overall_score(results)

        # risk score 0.2 -> (1 - 0.2) * 0.4 = 0.32; others score 1.0 * weight
        expected = (0.32 + 0.3 + 0.2 + 0.1) / 1.0
        assert abs(overall - expected) < 1e-9

    def test_zero_total_weight_scores_zero(self) -> None:
        framework = DecisionFramework(
            framework_name="Empty",
            decision_criteria=[
                DecisionCriteria(DecisionCriterion.RISK_SCORE, weight=0.0)
            ],
        )

        results = framework.evaluate_decision_criteria({})
        assert framework.calculate_overall_score(results) == 0.0


class TestDecisionEngineBoundaries:
    def _engine(self) -> UnderwritingDecisionEngine:
        return UnderwritingDecisionEngine()

    def _strong_application(self) -> dict:
        return {
            "risk_score": 0.1,
            "premium_adequacy": 1.5,
            "coverage_adequacy": 1.0,
            "compliance_score": 1.0,
        }

    def _weak_application(self) -> dict:
        return {
            "risk_score": 1.0,
            "premium_adequacy": 0.2,
            "coverage_adequacy": 0.2,
            "compliance_score": 0.2,
        }

    def test_strong_application_auto_approves(self) -> None:
        engine = self._engine()

        result = engine.make_decision(self._strong_application())

        assert result["decision"] == "approve"
        assert result["decision_type"] == DecisionType.AUTOMATIC.value
        assert result["requires_review"] is False
        assert result["overall_score"] >= 0.8

    def test_mid_band_score_refers_for_manual_review(self) -> None:
        engine = self._engine()
        # risk 0.7 -> (1 - 0.7) * 0.4 = 0.12; adequacy 1.0 -> 0.3; coverage
        # 1.0 -> 0.2; compliance 1.0 -> 0.1 => overall 0.72 (review band).
        result = engine.make_decision(
            {
                "risk_score": 0.7,
                "premium_adequacy": 1.0,
                "coverage_adequacy": 1.0,
                "compliance_score": 1.0,
            }
        )

        assert result["decision"] == "refer"
        assert result["decision_type"] == DecisionType.MANUAL_REVIEW.value
        assert result["requires_review"] is True

    def test_weak_application_declines(self) -> None:
        engine = self._engine()

        result = engine.make_decision(self._weak_application())

        assert result["decision"] == "decline"
        assert result["overall_score"] < 0.6

    def test_decision_record_stored_in_history_with_explanation(self) -> None:
        engine = self._engine()

        result = engine.make_decision(self._strong_application())

        assert len(engine.decision_history) == 1
        assert "Overall Decision Score" in result["explanation"]
        assert result["decision_id"].startswith("dec_")

    def test_unknown_framework_falls_back_to_standard(self) -> None:
        engine = self._engine()

        result = engine.make_decision(
            self._strong_application(), framework_name="missing"
        )

        assert result["framework_used"] == "missing"
        assert result["decision"] == "approve"

    def test_conservative_framework_declines_moderate_risk(self) -> None:
        engine = self._engine()
        moderate = {
            "risk_score": 0.55,
            "premium_adequacy": 1.0,
            "loss_ratio": 0.15,
        }

        standard = engine.make_decision(moderate, framework_name="standard")
        conservative = engine.make_decision(moderate, framework_name="conservative")

        assert conservative["decision"] == "decline"
        assert conservative["overall_score"] < standard["overall_score"]

    def test_custom_framework_is_selectable(self) -> None:
        engine = self._engine()
        framework = DecisionFramework(
            framework_name="Strict Capital",
            decision_criteria=[
                DecisionCriteria(
                    DecisionCriterion.RISK_SCORE,
                    weight=1.0,
                    threshold=0.3,
                    operator="less_equal",
                )
            ],
            auto_decision_threshold=0.9,
            manual_review_threshold=0.4,
        )
        assert engine.add_framework(framework) is True

        result = engine.make_decision(
            {"risk_score": 0.1}, framework_name="strict capital"
        )

        assert engine.get_framework("strict capital") is framework
        assert result["decision"] == "approve"

    def test_analytics_aggregate_stored_decisions(self) -> None:
        engine = self._engine()
        engine.make_decision(self._strong_application())
        engine.make_decision(self._weak_application())

        analytics = engine.get_decision_analytics()

        assert analytics["total_decisions"] == 2
        assert sum(analytics["decision_distribution"].values()) == 2
        assert 0.0 <= analytics["average_confidence"] <= 1.0
        assert set(analytics["framework_usage"]) == {"standard"}

    def test_health_check_reports_state(self) -> None:
        engine = self._engine()

        health = engine.health_check()

        assert health["status"] == "operational"
        assert health["total_frameworks"] >= 3
