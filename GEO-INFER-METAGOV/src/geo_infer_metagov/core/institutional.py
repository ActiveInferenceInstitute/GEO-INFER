"""Institutional design and analysis using IAD framework and Ostrom's principles."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InstitutionalFramework(Enum):
    """Institutional analysis frameworks."""
    IAD = "iad"  # Institutional Analysis and Development
    OSTROM = "ostrom"  # Ostrom's design principles


@dataclass
class Institution:
    """Represents a governance institution or rule."""
    institution_id: str
    name: str
    rule_type: str  # boundary, position, choice, information, aggregation, payoff, scope
    description: str
    affected_stakeholders: List[str]
    enforcement_mechanism: str
    effectiveness_rating: float = 0.5


@dataclass
class InstitutionalAnalysis:
    """Results of institutional analysis."""
    governance_domain: str
    analysis_framework: InstitutionalFramework
    existing_institutions: List[Institution]
    institutional_effectiveness: Dict[str, float]
    design_principles_assessment: Dict[str, float]
    recommendations: List[str]


class InstitutionalDesigner:
    """
    Institutional analysis and design using formal frameworks.
    
    Implements the Institutional Analysis and Development (IAD) framework
    developed by Elinor Ostrom and colleagues, as well as Ostrom's design
    principles for sustainable institutions.
    
    References:
    - Ostrom, E. (1990). Governing the Commons: The Evolution of Institutions
    - McGinnis, M. D. (2011). An Introduction to IAD and the Language of the Ostrom Workshop
    - Dietz, T., et al. (2003). The Drama of the Commons
    """
    
    def __init__(self, framework: str = 'iad', context_type: str = 'common_pool_resource'):
        """
        Initialize institutional designer.
        
        Parameters:
        -----------
        framework : str
            Institutional analysis framework (iad, ostrom)
        context_type : str
            Context type (common_pool_resource, public_goods, etc.)
        """
        self.framework = InstitutionalFramework(framework)
        self.context_type = context_type
        self.institutional_analyses: Dict[str, InstitutionalAnalysis] = {}
    
    def analyze_institutions(
        self,
        current_institutions: List[Dict[str, Any]],
        stakeholder_groups: List[Dict[str, Any]],
        resource_system: Dict[str, Any],
        decision_outcomes: List[Dict[str, Any]]
    ) -> InstitutionalAnalysis:
        """
        Analyze existing institutions using IAD framework.
        
        Parameters:
        -----------
        current_institutions : List[Dict[str, Any]]
            Current institutional rules
        stakeholder_groups : List[Dict[str, Any]]
            Stakeholder groups affected
        resource_system : Dict[str, Any]
            Resource system being governed
        decision_outcomes : List[Dict[str, Any]]
            Observed governance outcomes
            
        Returns:
        --------
        InstitutionalAnalysis
            Comprehensive institutional analysis
        """
        # Convert institutions to Institution objects
        institutions = [
            Institution(
                institution_id=f"inst_{i}",
                name=inst.get('name', f'Institution {i}'),
                rule_type=inst.get('type', 'unspecified'),
                description=inst.get('description', ''),
                affected_stakeholders=[sg.get('name', f'stakeholder_{j}') for j, sg in enumerate(stakeholder_groups)],
                enforcement_mechanism=inst.get('enforcement', 'informal')
            )
            for i, inst in enumerate(current_institutions)
        ]
        
        # Assess institutional effectiveness
        effectiveness = self._assess_effectiveness(
            institutions=institutions,
            outcomes=decision_outcomes
        )
        
        # Assess design principles
        principles_assessment = self._assess_design_principles(
            institutions=institutions,
            resource_system=resource_system
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            effectiveness=effectiveness,
            principles_assessment=principles_assessment
        )
        
        analysis = InstitutionalAnalysis(
            governance_domain=resource_system.get('domain', 'general'),
            analysis_framework=self.framework,
            existing_institutions=institutions,
            institutional_effectiveness=effectiveness,
            design_principles_assessment=principles_assessment,
            recommendations=recommendations
        )
        
        self.institutional_analyses[resource_system.get('id', 'analysis_0')] = analysis
        logger.info(f"Institutional analysis completed for {resource_system.get('domain', 'domain')}")
        
        return analysis
    
    def _assess_effectiveness(
        self,
        institutions: List[Institution],
        outcomes: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Assess effectiveness of institutions."""
        effectiveness = {}
        
        for inst in institutions:
            # Calculate effectiveness based on outcomes
            outcome_scores = [
                outcome.get('effectiveness', 0.5)
                for outcome in outcomes
                if any(stake in outcome.get('stakeholders', []) for stake in inst.affected_stakeholders)
            ]
            
            effectiveness[inst.institution_id] = sum(outcome_scores) / len(outcome_scores) if outcome_scores else 0.5
        
        return effectiveness
    
    def _assess_design_principles(
        self,
        institutions: List[Institution],
        resource_system: Dict[str, Any]
    ) -> Dict[str, float]:
        """Assess design principles for institutions."""
        principles = {
            'clear_boundaries': 0.7,
            'congruence': 0.6,
            'collective_choice_arrangements': 0.5,
            'monitoring': 0.7,
            'graduated_sanctions': 0.4,
            'conflict_resolution': 0.5,
            'right_to_organize': 0.8,
            'nested_enterprises': 0.3
        }
        
        return principles
    
    def _generate_recommendations(
        self,
        effectiveness: Dict[str, float],
        principles_assessment: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for institutional improvement."""
        recommendations = []
        
        # Identify low-scoring principles
        low_principles = [k for k, v in principles_assessment.items() if v < 0.5]
        
        if 'clear_boundaries' in low_principles:
            recommendations.append('Clarify user and resource boundaries')
        if 'congruence' in low_principles:
            recommendations.append('Align rules with local conditions')
        if 'monitoring' in low_principles:
            recommendations.append('Strengthen monitoring mechanisms')
        if 'conflict_resolution' in low_principles:
            recommendations.append('Establish conflict resolution procedures')
        
        return recommendations
    
    def apply_ostrom_principles(
        self,
        principle_set: List[str],
        resource_system: Dict[str, Any],
        governance_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply Ostrom's design principles for sustainable institutions.
        
        Parameters:
        -----------
        principle_set : List[str]
            Subset of Ostrom's 8 principles to apply
        resource_system : Dict[str, Any]
            Resource system characteristics
        governance_context : Dict[str, Any]
            Governance context and constraints
            
        Returns:
        --------
        Dict[str, Any]
            Designed institutions based on Ostrom's principles
        """
        designed_institutions = {}
        
        principle_descriptions = {
            'clear_boundaries': 'Clearly defined boundaries of resource and users',
            'congruence': 'Rules aligned with local conditions and user needs',
            'collective_choice_arrangements': 'Users participate in governance decisions',
            'monitoring': 'Effective monitoring of resource use and users',
            'graduated_sanctions': 'Proportional sanctions for rule violations',
            'conflict_resolution': 'Accessible, low-cost conflict resolution',
            'right_to_organize': 'External authorities respect right to self-organize',
            'nested_enterprises': 'Governance organized in nested tiers'
        }
        
        for principle in principle_set:
            if principle in principle_descriptions:
                designed_institutions[principle] = {
                    'description': principle_descriptions[principle],
                    'implementation_strategy': self._design_principle_implementation(
                        principle=principle,
                        resource_system=resource_system,
                        governance_context=governance_context
                    ),
                    'expected_outcomes': self._predict_principle_outcomes(principle)
                }
        
        return {
            'governance_design': designed_institutions,
            'resource_system': resource_system,
            'design_coherence': self._assess_design_coherence(designed_institutions)
        }
    
    def _design_principle_implementation(
        self,
        principle: str,
        resource_system: Dict[str, Any],
        governance_context: Dict[str, Any]
    ) -> List[str]:
        """Design implementation strategy for a principle."""
        strategies = {
            'clear_boundaries': [
                'Map resource extent and use rights',
                'Define membership criteria',
                'Register users in governance system'
            ],
            'congruence': [
                'Conduct local ecological assessment',
                'Align rules with seasonal patterns',
                'Adapt rules based on resource variability'
            ],
            'collective_choice_arrangements': [
                'Establish governance assemblies',
                'Create decision-making committees',
                'Enable user participation in rule-making'
            ],
            'monitoring': [
                'Deploy monitoring systems',
                'Train monitors from local community',
                'Establish regular monitoring schedules'
            ],
            'graduated_sanctions': [
                'Define violation categories',
                'Establish proportional penalties',
                'Document sanction procedures'
            ],
            'conflict_resolution': [
                'Establish arbitration mechanisms',
                'Create mediation procedures',
                'Document dispute resolution processes'
            ],
            'right_to_organize': [
                'Secure legal recognition of organization',
                'Establish collaborative relationships with authorities',
                'Document governance agreements'
            ],
            'nested_enterprises': [
                'Organize governance in tiers',
                'Define inter-tier coordination',
                'Establish information flows between tiers'
            ]
        }
        
        return strategies.get(principle, ['Develop implementation strategy for ' + principle])
    
    def _predict_principle_outcomes(self, principle: str) -> Dict[str, Any]:
        """Predict outcomes from implementing a principle."""
        return {
            'sustainability_impact': 0.7 if principle in ['clear_boundaries', 'monitoring'] else 0.5,
            'equity_impact': 0.6 if principle in ['collective_choice_arrangements', 'conflict_resolution'] else 0.4,
            'efficiency_impact': 0.8 if principle in ['congruence', 'monitoring'] else 0.5,
            'implementation_difficulty': 0.6
        }
    
    def _assess_design_coherence(self, designed_institutions: Dict[str, Any]) -> float:
        """Assess how well principles work together."""
        num_principles = len(designed_institutions)
        if num_principles >= 7:
            return 0.9
        elif num_principles >= 5:
            return 0.75
        else:
            return 0.5
