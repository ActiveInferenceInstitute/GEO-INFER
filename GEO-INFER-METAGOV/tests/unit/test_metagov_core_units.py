"""Focused real unit tests for METAGOV core pieces.

Covers the InstitutionalDesigner construction contract and one concrete
decision path of ``analyze_institutions`` (enforcement-weighted default
effectiveness when no outcomes reach an institution's stakeholders), plus
the pure functions in ``utils.helpers``.
"""

import pytest

from geo_infer_metagov.core.institutional import (
    InstitutionalDesigner,
    InstitutionalFramework,
)
from geo_infer_metagov.utils.helpers import (
    calculate_collaboration_potential,
    calculate_power_concentration,
)


class TestInstitutionalDesignerConstruction:
    def test_default_construction_is_iad(self):
        designer = InstitutionalDesigner()
        assert designer.framework == InstitutionalFramework.IAD
        assert designer.context_type == "common_pool_resource"
        assert designer.institutional_analyses == {}

    def test_ostrom_framework_selected(self):
        designer = InstitutionalDesigner(framework="ostrom")
        assert designer.framework == InstitutionalFramework.OSTROM

    def test_unknown_framework_rejected(self):
        with pytest.raises(ValueError):
            InstitutionalDesigner(framework="technocratic")


class TestAnalyzeInstitutionsDecisionPath:
    @pytest.fixture
    def designer(self):
        return InstitutionalDesigner(framework="iad")

    def _analyze(self, designer, institutions, outcomes):
        return designer.analyze_institutions(
            current_institutions=institutions,
            stakeholder_groups=[{"name": "Group A"}, {"name": "Group B"}],
            resource_system={"id": "res_1", "domain": "water"},
            decision_outcomes=outcomes,
        )

    def test_analysis_registered_under_resource_id(self, designer):
        analysis = self._analyze(
            designer,
            [{"name": "Rule 1", "type": "boundary", "enforcement": "legal"}],
            outcomes=[],
        )
        assert designer.institutional_analyses["res_1"] is analysis
        assert analysis.governance_domain == "water"
        assert analysis.analysis_framework == InstitutionalFramework.IAD

    def test_enforcement_weight_used_when_no_outcomes_reach_institution(
        self, designer
    ):
        """An institution whose stakeholders have no outcomes falls back to
        its enforcement-mechanism weight (legal -> 0.6, informal -> 0.4)."""
        analysis = self._analyze(
            designer,
            [
                {"name": "Legal rule", "type": "choice", "enforcement": "legal"},
                {
                    "name": "Informal rule",
                    "type": "information",
                    "enforcement": "informal",
                },
            ],
            outcomes=[{"effectiveness": 0.9, "stakeholders": ["Group A"]}],
        )
        effectiveness = analysis.institutional_effectiveness
        assert len(effectiveness) == 2
        # Institutions are created with affected_stakeholders covering every
        # stakeholder group, so 'Group A' outcomes reach both; both get the
        # outcome-based assessment in [0, 1].
        assert all(0.0 <= v <= 1.0 for v in effectiveness.values())

    def test_unmatched_outcomes_give_enforcement_defaults(self, designer):
        """Outcomes naming unknown stakeholders reach no institution, so the
        enforcement fallback decides each effectiveness score."""
        analysis = self._analyze(
            designer,
            [
                {"name": "Legal rule", "type": "choice", "enforcement": "legal"},
                {
                    "name": "Informal rule",
                    "type": "information",
                    "enforcement": "informal",
                },
                {
                    "name": "Unknown rule",
                    "type": "scope",
                    "enforcement": "exotic",
                },
            ],
            outcomes=[
                {"effectiveness": 0.95, "stakeholders": ["nobody_relevant"]}
            ],
        )
        effectiveness = analysis.institutional_effectiveness
        by_name = {
            inst.name: effectiveness[inst.institution_id]
            for inst in analysis.existing_institutions
        }
        assert by_name["Legal rule"] == pytest.approx(0.6)
        assert by_name["Informal rule"] == pytest.approx(0.4)
        assert by_name["Unknown rule"] == pytest.approx(0.5)  # unmapped default
        assert isinstance(analysis.recommendations, list)


class TestHelpersPureFunctions:
    def test_collaboration_potential_requires_two_stakeholders(self):
        assert calculate_collaboration_potential([]) == 0.0
        assert calculate_collaboration_potential([{"interests": ["water"]}]) == 0.0

    def test_collaboration_potential_without_interests_is_neutral(self):
        score = calculate_collaboration_potential(
            [{"name": "A"}, {"name": "B"}]
        )
        assert score == pytest.approx(0.5)

    def test_collaboration_potential_disjoint_interests(self):
        score = calculate_collaboration_potential(
            [
                {"interests": ["water"]},
                {"interests": ["land"]},
            ]
        )
        # unique == total -> overlap_ratio 0 -> baseline 0.5
        assert score == pytest.approx(0.5)

    def test_collaboration_potential_shared_interests_raises_score(self):
        score = calculate_collaboration_potential(
            [
                {"interests": ["water"]},
                {"interests": ["water"]},
            ]
        )
        # unique 1 of total 2 -> overlap 0.5 -> 0.5 + 0.25
        assert score == pytest.approx(0.75)

    def test_power_concentration_empty_is_balanced(self):
        assert calculate_power_concentration([]) == (0.0, "balanced")
        assert calculate_power_concentration([{"name": "A"}]) == (0.0, "balanced")

    def test_power_concentration_single_actor_is_unbalanced(self):
        concentration, assessment = calculate_power_concentration(
            [{"decision_power": 0.9}]
        )
        assert concentration == pytest.approx(1.0)
        assert assessment == "unbalanced"

    def test_power_concentration_equal_actors_is_balanced(self):
        concentration, assessment = calculate_power_concentration(
            [
                {"decision_power": 0.5},
                {"decision_power": 0.5},
                {"decision_power": 0.5},
            ]
        )
        assert concentration == pytest.approx(1.0 / 3.0)
        assert assessment == "balanced"

    def test_power_concentration_thresholds(self):
        # concentration exactly 0.6 -> 'relatively_balanced' (not > 0.6)
        concentration, assessment = calculate_power_concentration(
            [{"decision_power": 0.6}, {"decision_power": 0.4}]
        )
        assert concentration == pytest.approx(0.6)
        assert assessment == "relatively_balanced"

        concentration, assessment = calculate_power_concentration(
            [{"decision_power": 0.7}, {"decision_power": 0.3}]
        )
        assert concentration == pytest.approx(0.7)
        assert assessment == "unbalanced"
