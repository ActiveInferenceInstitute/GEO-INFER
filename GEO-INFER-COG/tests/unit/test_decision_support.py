"""
Unit tests for SpatialDecisionSupport, DecisionAlternative, and DecisionRecommendation.
"""

import numpy as np
import pytest

from geo_infer_cog.decision.support import (
    DecisionAlternative,
    DecisionRecommendation,
    DecisionStrategy,
    SpatialDecisionSupport,
)
from geo_infer_cog.models.user_profiles import UserCognitiveProfile


def _make_profile(**overrides) -> UserCognitiveProfile:
    defaults = dict(
        user_id='user_1',
        spatial_expertise=0.5,
        cognitive_load_preference='moderate',
        cognitive_style='balanced',
        spatial_reasoning_style='balanced',
    )
    defaults.update(overrides)
    return UserCognitiveProfile(**defaults)


class TestDecisionAlternative:
    """Test DecisionAlternative data class."""

    def test_cognitive_compatibility_moderate_user(self) -> None:
        alt = DecisionAlternative(
            alternative_id='a1',
            description='Option A',
            spatial_context={},
            cognitive_factors={'complexity_level': 0.5, 'cognitive_load': 0.5},
            risk_assessment={'overall_risk': 0.5},
        )
        profile = _make_profile()
        score = alt.calculate_cognitive_compatibility(profile)
        assert 0.0 <= score <= 1.0

    def test_expert_has_higher_compatibility_with_complex(self) -> None:
        # Use extreme values so that the novice score stays well below 1.0 ceiling
        alt = DecisionAlternative(
            alternative_id='a1',
            description='Complex option',
            spatial_context={},
            cognitive_factors={'complexity_level': 0.9, 'cognitive_load': 0.9},
            risk_assessment={'overall_risk': 0.9},
        )
        expert = _make_profile(spatial_expertise=0.9, cognitive_load_preference='high')
        novice = _make_profile(spatial_expertise=0.1, cognitive_load_preference='low')
        expert_score = alt.calculate_cognitive_compatibility(expert)
        novice_score = alt.calculate_cognitive_compatibility(novice)
        assert expert_score > novice_score


class TestDecisionRecommendation:
    """Test DecisionRecommendation formatting."""

    def test_to_display_format_visualizer(self) -> None:
        rec = DecisionRecommendation(
            alternative_id='a1',
            recommendation_score=0.85,
            confidence_level=0.9,
            primary_rationale='Best overall score',
        )
        profile = _make_profile(cognitive_style='visualizer')
        display = rec.to_display_format(profile)
        assert display['visual_indicators'] is True
        assert display['text_summary'] == 'brief'

    def test_to_display_format_low_load_preference(self) -> None:
        rec = DecisionRecommendation(
            alternative_id='a1',
            recommendation_score=0.7,
            confidence_level=0.8,
            primary_rationale='Good option',
        )
        profile = _make_profile(cognitive_load_preference='low')
        display = rec.to_display_format(profile)
        assert any('Simplified' in c for c in display['user_considerations'])


class TestDecisionStrategy:
    """Test DecisionStrategy enum."""

    def test_strategy_values(self) -> None:
        assert DecisionStrategy.PROSPECT_THEORY.value == 'prospect_theory'
        assert DecisionStrategy.CONSERVATIVE.value == 'conservative'


class TestSpatialDecisionSupport:
    """Test SpatialDecisionSupport class."""

    @pytest.fixture
    def support(self) -> SpatialDecisionSupport:
        return SpatialDecisionSupport(decision_framework='prospect_theory')

    def test_init_defaults(self, support: SpatialDecisionSupport) -> None:
        assert support.decision_framework == 'prospect_theory'
        assert support.cognitive_bias_mitigation is True

    def test_prospect_theory_evaluation(self, support: SpatialDecisionSupport) -> None:
        alts = [
            DecisionAlternative(
                alternative_id='opt_a',
                description='Option A',
                spatial_context={},
                expected_outcomes={'cost': 0.8, 'benefit': 0.6},
                uncertainty_measures={'overall_uncertainty': 0.2},
            ),
        ]
        evaluations = support._apply_prospect_theory(alts, ['cost', 'benefit'])
        assert 'opt_a' in evaluations
        assert isinstance(evaluations['opt_a'], float)

    def test_prospect_theory_loss_aversion(self) -> None:
        support = SpatialDecisionSupport(decision_framework='prospect_theory')
        gain = DecisionAlternative(
            alternative_id='gain',
            description='Gain',
            spatial_context={},
            expected_outcomes={'val': 1.0},
            uncertainty_measures={},
        )
        loss = DecisionAlternative(
            alternative_id='loss',
            description='Loss',
            spatial_context={},
            expected_outcomes={'val': -1.0},
            uncertainty_measures={},
        )
        evals = support._apply_prospect_theory([gain, loss], ['val'])
        # Loss aversion: absolute value of loss evaluation should exceed gain
        assert abs(evals['loss']) > abs(evals['gain'])

    def test_bias_detection_status_quo(self) -> None:
        support = SpatialDecisionSupport()
        alt = DecisionAlternative(
            alternative_id='a1',
            description='Big change',
            spatial_context={},
            risk_assessment={'change_magnitude': 0.9},
        )
        biases = support._detect_cognitive_biases(alt, [])
        assert 'status_quo_bias' in biases

    def test_bias_mitigation_reduces_change_magnitude(self) -> None:
        support = SpatialDecisionSupport()
        alt = DecisionAlternative(
            alternative_id='a1',
            description='Big change',
            spatial_context={},
            risk_assessment={'change_magnitude': 1.0},
        )
        mitigated = support._mitigate_detected_biases(alt, ['status_quo_bias'])
        assert mitigated.risk_assessment['change_magnitude'] < 1.0

    def test_get_status(self, support: SpatialDecisionSupport) -> None:
        status = support.get_status()
        assert status['system_type'] == 'spatial_decision_support'
        assert status['decision_framework'] == 'prospect_theory'
        assert status['status'] == 'active'

    def test_analyze_decision_returns_result(self) -> None:
        """Regression: analyze_decision must return the analysis dict, not None."""
        support = SpatialDecisionSupport()
        profile = _make_profile()
        result = support.analyze_decision(
            decision_problem={'description': 'site selection'},
            spatial_alternatives=[
                {
                    'id': 'a1',
                    'description': 'Site A',
                    'spatial_context': {},
                    'cognitive_factors': {'complexity_level': 0.4},
                    'uncertainty_measures': {},
                    'expected_outcomes': {},
                    'risk_assessment': {'overall_risk': 0.3},
                }
            ],
            decision_criteria=['accessibility'],
            stakeholder_profiles=[profile],
        )
        assert isinstance(result, dict)
        assert result['decision_problem'] == {'description': 'site selection'}
        assert len(result['alternatives']) == 1
        assert isinstance(result['recommendations'], list)
        assert result['decision_framework'] == 'prospect_theory'

    def test_analyze_decision_dispatches_declared_strategies(self) -> None:
        """Every DecisionStrategy value with an implementation is dispatched."""
        support = SpatialDecisionSupport()
        profile = _make_profile()
        kwargs = dict(
            decision_problem={'description': 'x'},
            spatial_alternatives=[{'id': 'a1', 'description': 'Site A', 'spatial_context': {}}],
            decision_criteria=['cost'],
            stakeholder_profiles=[profile],
        )
        for framework in ('prospect_theory', 'cognitive_weighted',
                          'bayesian_decision', 'multi_criteria'):
            support.decision_framework = framework
            result = support.analyze_decision(**kwargs)
            assert isinstance(result, dict)
            assert result['decision_framework'] == framework
