"""Behavioral tests for the underwriting rules engine (GS-146).

Covers RuleCondition operator semantics, UnderwritingRule evaluation
boundaries, and UnderwritingRulesEngine rule->final-decision resolution
including the refer/decline conflict paths.
"""

from datetime import datetime, timedelta

from geo_infer_insurance.underwriting.core.underwriting_rules import (
    RuleCondition,
    RuleOperator,
    RuleType,
    UnderwritingRule,
    UnderwritingRulesEngine,
)


class TestRuleConditionOperators:
    def test_comparison_operators_on_scalar_values(self) -> None:
        data = {"property": {"value": 250000}}

        assert RuleCondition(
            "property.value", RuleOperator.GREATER_THAN, 100000
        ).evaluate(data)
        assert not RuleCondition(
            "property.value", RuleOperator.GREATER_THAN, 250000
        ).evaluate(data)
        assert RuleCondition(
            "property.value", RuleOperator.LESS_EQUAL, 250000
        ).evaluate(data)
        assert RuleCondition("property.value", RuleOperator.NOT_EQUALS, 1).evaluate(
            data
        )

    def test_between_is_inclusive_on_two_element_list(self) -> None:
        data = {"risk": {"score": 0.5}}

        assert RuleCondition("risk.score", RuleOperator.BETWEEN, [0.5, 0.9]).evaluate(
            data
        )
        assert RuleCondition("risk.score", RuleOperator.BETWEEN, [0.0, 0.5]).evaluate(
            data
        )
        assert not RuleCondition(
            "risk.score", RuleOperator.BETWEEN, [0.6, 0.9]
        ).evaluate(data)
        assert not RuleCondition(
            "risk.score", RuleOperator.BETWEEN, [0.1, 0.3, 0.9]
        ).evaluate(data)

    def test_membership_operators_only_match_list_values(self) -> None:
        data = {"region": "coastal"}

        assert RuleCondition("region", RuleOperator.IN, ["coastal", "rural"]).evaluate(
            data
        )
        assert RuleCondition("region", RuleOperator.NOT_IN, ["urban"]).evaluate(data)
        assert not RuleCondition("region", RuleOperator.IN, "coastal").evaluate(data)
        assert RuleCondition("region", RuleOperator.NOT_IN, 42).evaluate(data)

    def test_contains_and_regex_operators(self) -> None:
        data = {"address": "123 Harbor Street"}

        assert RuleCondition("address", RuleOperator.CONTAINS, "harbor").evaluate(data)
        assert RuleCondition("address", RuleOperator.NOT_CONTAINS, "beach").evaluate(
            data
        )
        assert RuleCondition("address", RuleOperator.REGEX, r"^\d+ Harbor").evaluate(
            data
        )
        assert not RuleCondition("address", RuleOperator.REGEX, r"^Ave").evaluate(data)

    def test_missing_field_fails_closed(self) -> None:
        assert not RuleCondition(
            "property.value", RuleOperator.GREATER_THAN, 0
        ).evaluate({})
        assert not RuleCondition(
            "property.missing.deep", RuleOperator.EQUALS, 1
        ).evaluate({"property": {"value": 1}})

    def test_list_index_access_into_nested_data(self) -> None:
        data = {"perils": [{"name": "flood"}, {"name": "quake"}]}

        assert RuleCondition("perils.0.name", RuleOperator.EQUALS, "flood").evaluate(
            data
        )
        assert RuleCondition("perils.1.name", RuleOperator.EQUALS, "quake").evaluate(
            data
        )
        assert not RuleCondition(
            "perils.5.name", RuleOperator.EQUALS, "flood"
        ).evaluate(data)


class TestUnderwritingRuleEvaluation:
    def _rule(self, **overrides) -> UnderwritingRule:
        defaults = dict(
            rule_id="r1",
            name="Test Rule",
            description="rule under test",
            rule_type=RuleType.ELIGIBILITY,
            conditions=[
                RuleCondition("property.value", RuleOperator.LESS_EQUAL, 1000000)
            ],
            action="approve",
            priority=5,
        )
        defaults.update(overrides)
        return UnderwritingRule(**defaults)

    def test_passing_rule_returns_its_action_and_parameters(self) -> None:
        rule = self._rule(action_parameters={"max_limit": 900000})

        result = rule.evaluate({"property": {"value": 500000}})

        assert result["passed"] is True
        assert result["action"] == "approve"
        assert result["action_parameters"] == {"max_limit": 900000}
        assert result["condition_results"] == [True]

    def test_failing_condition_suppresses_action(self) -> None:
        result = self._rule().evaluate({"property": {"value": 2000000}})

        assert result["passed"] is False
        assert result["action"] is None
        assert result["action_parameters"] == {}

    def test_inactive_rule_reports_not_active_without_action(self) -> None:
        result = self._rule(is_active=False).evaluate({"property": {"value": 10}})

        assert result["passed"] is False
        assert result["action"] is None
        assert result["reason"] == "Rule not active or effective"

    def test_expired_rule_is_not_effective(self) -> None:
        rule = self._rule(expiration_date=datetime.now() - timedelta(days=1))

        result = rule.evaluate({"property": {"value": 10}})

        assert result["passed"] is False
        assert result["action"] is None

    def test_product_applicability_gates_evaluation(self) -> None:
        rule = self._rule(applicable_products=["commercial"])

        in_scope = rule.evaluate(
            {"property": {"value": 10}, "product_type": "commercial"}
        )
        out_of_scope = rule.evaluate(
            {"property": {"value": 10}, "product_type": "residential"}
        )

        assert in_scope["passed"] is True
        assert out_of_scope["reason"] == "Rule not applicable"
        assert out_of_scope["action"] is None

    def test_region_applicability_gates_evaluation(self) -> None:
        rule = self._rule(applicable_regions=["ca"])

        assert (
            rule.evaluate({"property": {"value": 10}, "region": "ca"})["passed"] is True
        )
        out_of_scope = rule.evaluate({"property": {"value": 10}, "region": "ny"})
        assert out_of_scope["reason"] == "Rule not applicable"
        assert out_of_scope["action"] is None


class TestRulesEngineDecisions:
    def _engine(self) -> UnderwritingRulesEngine:
        return UnderwritingRulesEngine()

    def _data(self, value: float, **extra) -> dict:
        property_data = {"value": value, "year_built": 2005}
        property_data.update(extra)
        return {"property": property_data}

    def _engine_with_value_limits_only(self) -> UnderwritingRulesEngine:
        engine = self._engine()
        for rule_id in (
            "coverage_limit_check",
            "high_risk_location",
            "property_age_limit",
        ):
            assert engine.remove_rule(rule_id) is True
        return engine

    def test_default_rules_conflict_to_refer_on_plain_application_data(self) -> None:
        """Default rule set yields a conservative refer for plain data.

        The bundled coverage-limit and flood-zone rules fail whenever the
        corresponding fields are absent, while the approve-scoped property
        value rules pass, so the conflict path fires.
        """
        engine = self._engine()

        result = engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})

        final = result["final_decision"]
        assert final["action"] == "refer"
        assert final["failed_rules"] >= 1
        assert final["approval_rules"] >= 1
        assert result["total_rules_evaluated"] == len(engine.rules)

    def test_coverage_limit_rule_compares_against_a_literal_string(self) -> None:
        """The bundled coverage_limit_check rule fails even for tiny limits.

        Its condition compares coverage.limit against the literal string
        "property.value" instead of resolving that field, so the comparison
        raises and the condition fails closed.
        """
        engine = self._engine()
        condition = engine.rules["coverage_limit_check"].conditions[0]

        assert condition.field == "coverage.limit"
        assert condition.value == "property.value"
        assert (
            condition.evaluate(
                {"coverage": {"limit": 1}, "property": {"value": 10_000_000}}
            )
            is False
        )

        # At the engine level the rule therefore always lands in failed_rules,
        # regardless of the coverage limit supplied.
        result = engine.evaluate_rules(
            {**self._data(500000), "coverage": {"limit": 1}}, {"risk_score": 0.4}
        )
        by_id = {r["rule_id"]: r for r in result["rule_results"]}
        assert by_id["coverage_limit_check"]["passed"] is False

    def test_absent_flood_zone_fails_the_high_risk_rule(self) -> None:
        """high_risk_location matches only flood_zone "A"; absence fails it."""
        engine = self._engine()
        condition = engine.rules["high_risk_location"].conditions[0]

        assert condition.field == "property.flood_zone"
        assert condition.evaluate({"property": {}}) is False
        assert condition.evaluate({"property": {"flood_zone": "B"}}) is False
        assert condition.evaluate({"property": {"flood_zone": "A"}}) is True

        plain = engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})
        by_id_plain = {r["rule_id"]: r for r in plain["rule_results"]}
        assert by_id_plain["high_risk_location"]["passed"] is False

        flagged = engine.evaluate_rules(
            self._data(500000, flood_zone="A"), {"risk_score": 0.4}
        )
        by_id_flagged = {r["rule_id"]: r for r in flagged["rule_results"]}
        assert by_id_flagged["high_risk_location"]["passed"] is True
        assert by_id_flagged["high_risk_location"]["action"] == "refer"

    def test_boundary_values_pass_both_property_value_limits(self) -> None:
        engine = self._engine_with_value_limits_only()

        for boundary in (10000, 10000000):
            result = engine.evaluate_rules(self._data(boundary), {"risk_score": 0.4})
            assert result["final_decision"]["action"] == "approve", boundary

    def test_value_outside_limits_never_approves(self) -> None:
        engine = self._engine_with_value_limits_only()

        below = engine.evaluate_rules(self._data(9999), {"risk_score": 0.4})
        above = engine.evaluate_rules(self._data(10000001), {"risk_score": 0.4})

        assert below["final_decision"]["action"] == "refer"
        assert above["final_decision"]["action"] == "refer"

    def test_all_approval_rules_failing_declines(self) -> None:
        engine = self._engine_with_value_limits_only()
        assert engine.remove_rule("min_property_value") is True

        result = engine.evaluate_rules(self._data(10000001), {"risk_score": 0.4})

        final = result["final_decision"]
        assert final["action"] == "decline"
        assert final["failed_rules"] == 1

    def test_conflicting_rules_refer_for_manual_review(self) -> None:
        engine = self._engine()
        # Max-value rule fails (value above $10M) while min-value rule still
        # passes with an approve action -> conservative refer.
        result = engine.evaluate_rules(
            self._data(20000000, flood_zone="A"), {"risk_score": 0.4}
        )

        final = result["final_decision"]
        assert final["action"] == "refer"
        assert "conflict" in final["reason"].lower()
        assert final["failed_rules"] >= 1

    def test_failing_only_rule_declines(self) -> None:
        engine = self._engine()
        assert engine.remove_rule("max_property_value") is True

        result = engine.evaluate_rules(self._data(5000), {"risk_score": 0.4})

        final = result["final_decision"]
        assert final["action"] == "decline"
        assert final["failed_rules"] >= 1

    def test_removed_rule_no_longer_evaluates(self) -> None:
        engine = self._engine()
        total_before = len(engine.rules)
        assert engine.remove_rule("high_risk_location") is True
        assert engine.remove_rule("high_risk_location") is False

        result = engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})

        assert result["total_rules_evaluated"] == total_before - 1

    def test_added_rule_with_higher_priority_wins_final_action(self) -> None:
        engine = self._engine_with_value_limits_only()
        custom = UnderwritingRule(
            rule_id="custom_refer_all",
            name="Refer All",
            description="test rule",
            rule_type=RuleType.RISK_LIMIT,
            conditions=[RuleCondition("property.value", RuleOperator.GREATER_THAN, 0)],
            action="refer",
            priority=99,
        )
        assert engine.add_rule(custom) is True

        result = engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})

        final = result["final_decision"]
        assert final["action"] == "refer"
        assert final["passed_rules"] >= 1
        assert "custom_refer_all" in [r["rule_id"] for r in result["rule_results"]]

    def test_rule_applicable_product_narrows_evaluation(self) -> None:
        engine = self._engine()
        engine.add_rule(
            UnderwritingRule(
                rule_id="residential_only",
                name="Residential Only",
                description="only residential",
                rule_type=RuleType.ELIGIBILITY,
                conditions=[
                    RuleCondition("property.value", RuleOperator.GREATER_THAN, 0)
                ],
                applicable_products=["residential"],
                priority=50,
            )
        )

        residential = engine.evaluate_rules(
            {**self._data(500000), "product_type": "residential"}, {"risk_score": 0.4}
        )
        commercial = engine.evaluate_rules(
            {**self._data(500000), "product_type": "commercial"}, {"risk_score": 0.4}
        )

        residential_ids = [r["rule_id"] for r in residential["rule_results"]]
        assert "residential_only" in residential_ids
        commercial_ids = [r["rule_id"] for r in commercial["rule_results"]]
        assert "residential_only" not in commercial_ids

    def test_evaluation_metrics_track_evaluations(self) -> None:
        engine = self._engine()

        engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})
        engine.evaluate_rules(self._data(500000), {"risk_score": 0.4})

        assert engine.evaluation_metrics["total_evaluations"] == 2
        assert engine.evaluation_metrics["average_evaluation_time"] >= 0.0

    def test_update_rule_changes_behavior(self) -> None:
        engine = self._engine()
        engine.update_rule("max_property_value", {"priority": 1})

        assert engine.rules["max_property_value"].priority == 1
        assert engine.update_rule("does_not_exist", {"priority": 1}) is False
