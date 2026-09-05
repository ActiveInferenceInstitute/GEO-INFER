"""Regression tests: governance APIs must accept dataclass entities, not only dicts.

Performance evaluation and scenario planning used to assume every entity was a
dict, crashing with AttributeError when handed core GovernanceEntity objects.
"""

from geo_infer_metagov.core.multi_level import (
    GovernanceLevel,
    MultiLevelGovernanceFramework,
)
from geo_infer_metagov.core.performance import PerformanceEvaluator
from geo_infer_metagov.core.scenarios import Scenario, ScenarioPlanner
from geo_infer_metagov.utils.helpers import entity_field

from geo_infer_metagov.core.multi_level import GovernanceEntity, GovernanceStructure


def _make_structure() -> GovernanceStructure:
    framework = MultiLevelGovernanceFramework(
        governance_levels=['local', 'regional'],
    )
    return framework.design_governance_structure(
        spatial_scope={'name': 'Basin', 'area_km2': 1200},
        stakeholder_groups=[
            {'id': 'g1', 'name': 'Agency', 'category': 'government'},
            {'id': 'g2', 'name': 'Community', 'category': 'community'},
        ],
        decision_domains=['water_allocation', 'flood_management'],
        time_horizons=[1, 5],
    )


class TestEntityField:
    def test_reads_dict_and_object_identically(self) -> None:
        entity = GovernanceEntity(
            entity_id='e1', name='Agency', governance_level=GovernanceLevel.LOCAL,
            jurisdiction={}, responsibilities=[], authority_domain='water',
            capacity=0.8,
        )
        assert entity_field(entity, 'capacity', 0.5) == 0.8
        assert entity_field({'capacity': 0.8}, 'capacity', 0.5) == 0.8
        assert entity_field({}, 'capacity', 0.5) == 0.5
        assert entity_field(entity, 'nonexistent', 'fallback') == 'fallback'


class TestPerformanceOnDataclassEntities:
    def test_evaluate_real_governance_structure(self) -> None:
        structure = _make_structure()
        assert structure.entities, "design must produce GovernanceEntity objects"
        assert isinstance(structure.entities[0], GovernanceEntity)
        evaluator = PerformanceEvaluator()
        metrics = evaluator.evaluate_governance_performance(
            governance_structure=structure.__dict__,
            performance_data={'process_efficiency': 0.6, 'resource_efficiency': 0.6},
        )
        assert 0.0 <= metrics.overall_score <= 1.0
        assert 'efficiency' in metrics.dimension_scores


class TestScenariosOnDataclassEntities:
    def test_scenario_modifications_and_evaluation(self) -> None:
        structure = _make_structure()
        system = ScenarioPlanner()
        scenario = Scenario(
            scenario_id='sc_1',
            name='Budget stress',
            description='Reduced budget',
            assumptions={'budget_change': -0.5},
            modifications={'capacity': 0.8, 'resource_budget': 0.5},
        )
        result = system.evaluate_scenario(scenario, structure.__dict__)
        evaluation = result['evaluation']
        assert isinstance(evaluation, dict)
        assert 0.0 <= evaluation.get('performance_score', 0.0) <= 1.0
