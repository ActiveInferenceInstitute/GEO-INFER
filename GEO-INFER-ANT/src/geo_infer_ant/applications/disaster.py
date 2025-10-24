"""
Disaster Response Coordination for GEO-INFER-ANT

This module implements swarm-based disaster response coordination systems,
including search and rescue operations, damage assessment, resource distribution,
and multi-agency coordination during emergency situations.

Key Features:
- Multi-objective disaster response optimization
- Real-time situation assessment and adaptation
- Resource allocation and deployment optimization
- Communication network management in degraded environments
- Integration with emergency response protocols
- After-action analysis and learning
"""

import numpy as np
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DisasterScenario:
    """Configuration for disaster response scenario."""
    disaster_type: str  # 'flood', 'earthquake', 'wildfire', 'hurricane', etc.
    affected_area: Dict[str, float]  # Geographic bounds
    severity_level: str  # 'low', 'medium', 'high', 'critical'
    response_phases: List[str]  # 'preparedness', 'response', 'recovery'
    available_resources: Dict[str, Any]
    environmental_conditions: Dict[str, Any]
    time_constraints: Dict[str, float]

    def __post_init__(self):
        """Validate scenario configuration."""
        valid_types = ['flood', 'earthquake', 'wildfire', 'hurricane', 'tornado', 'tsunami']
        if self.disaster_type not in valid_types:
            raise ValueError(f"Invalid disaster type: {self.disaster_type}")

        valid_severity = ['low', 'medium', 'high', 'critical']
        if self.severity_level not in valid_severity:
            raise ValueError(f"Invalid severity level: {self.severity_level}")


class DisasterResponseSwarm:
    """
    Swarm-based disaster response coordination system.

    This application coordinates multiple types of response agents and resources
    to optimize disaster response operations, including search and rescue,
    damage assessment, resource distribution, and multi-agency coordination.

    Key Features:
    - Real-time situation assessment
    - Multi-objective response optimization
    - Resource allocation under constraints
    - Communication in degraded environments
    - Adaptive response strategies
    """

    def __init__(
        self,
        response_types: Optional[List[str]] = None,
        swarm_composition: Optional[Dict[str, int]] = None,
        coordination_protocol: str = 'stigmergic',
        real_time_adaptation: bool = True,
        **kwargs
    ):
        """
        Initialize disaster response swarm.

        Args:
            response_types: Types of response operations to coordinate
            swarm_composition: Composition of response agents/units
            coordination_protocol: Protocol for agent coordination
            real_time_adaptation: Whether to adapt in real-time
            **kwargs: Additional configuration parameters
        """
        self.response_types = response_types or ['search_rescue', 'damage_assessment', 'resource_distribution']
        self.swarm_composition = swarm_composition or {'drones': 20, 'ground_vehicles': 15, 'human_teams': 10}
        self.coordination_protocol = coordination_protocol
        self.real_time_adaptation = real_time_adaptation

        # Response system state
        self.response_agents: List[Dict[str, Any]] = []
        self.current_scenario: Optional[DisasterScenario] = None
        self.response_coordination: Dict[str, Any] = {}
        self.resource_allocation: Dict[str, Any] = {}

        # Performance tracking
        self.response_efficiency: float = 0.0
        self.coverage_effectiveness: float = 0.0
        self.coordination_quality: float = 0.0

        logger.info(f"DisasterResponseSwarm initialized for {len(self.response_types)} response types")

    async def assess_situation(
        self,
        disaster_type: str,
        affected_area: Dict[str, float],
        incident_severity: str = 'medium',
        available_resources: Optional[Dict[str, Any]] = None,
        environmental_conditions: Optional[Dict[str, Any]] = None,
        time_available: float = 7200  # 2 hours in seconds
    ) -> Dict[str, Any]:
        """
        Assess disaster situation and determine response requirements.

        Args:
            disaster_type: Type of disaster incident
            affected_area: Geographic bounds of affected area
            incident_severity: Severity level of the incident
            available_resources: Resources available for response
            environmental_conditions: Environmental conditions affecting response
            time_available: Time available for response operations

        Returns:
            Situation assessment and response requirements
        """
        logger.info(f"Assessing disaster situation: {disaster_type}, severity: {incident_severity}")

        assessment = {
            'assessment_time': datetime.now(),
            'disaster_type': disaster_type,
            'affected_area': affected_area,
            'severity': incident_severity,
            'response_requirements': {},
            'resource_requirements': {},
            'priority_zones': [],
            'risk_factors': {},
            'estimated_response_time': 0.0
        }

        try:
            # Create disaster scenario
            self.current_scenario = DisasterScenario(
                disaster_type=disaster_type,
                affected_area=affected_area,
                severity_level=incident_severity,
                response_phases=['response', 'recovery'],
                available_resources=available_resources or self.swarm_composition,
                environmental_conditions=environmental_conditions or {},
                time_constraints={'response_window': time_available}
            )

            # Calculate response requirements based on disaster type and severity
            requirements = self._calculate_response_requirements(
                disaster_type, incident_severity, affected_area
            )
            assessment['response_requirements'] = requirements

            # Calculate resource requirements
            resource_reqs = self._calculate_resource_requirements(requirements, available_resources)
            assessment['resource_requirements'] = resource_reqs

            # Identify priority response zones
            priority_zones = self._identify_priority_zones(affected_area, disaster_type, incident_severity)
            assessment['priority_zones'] = priority_zones

            # Assess risk factors
            risk_factors = self._assess_risk_factors(environmental_conditions, disaster_type)
            assessment['risk_factors'] = risk_factors

            # Estimate total response time
            estimated_time = self._estimate_response_time(requirements, resource_reqs)
            assessment['estimated_response_time'] = estimated_time

        except Exception as e:
            logger.error(f"Disaster situation assessment failed: {e}")
            assessment['error'] = str(e)

        logger.info(f"Disaster assessment completed: {len(assessment['response_requirements'])} requirements identified")
        return assessment

    def _calculate_response_requirements(
        self,
        disaster_type: str,
        severity: str,
        affected_area: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate response requirements based on disaster characteristics."""
        requirements = {}

        # Base requirements by disaster type
        type_requirements = {
            'flood': {'search_rescue': 0.8, 'resource_distribution': 0.7, 'damage_assessment': 0.6},
            'earthquake': {'search_rescue': 0.9, 'damage_assessment': 0.8, 'resource_distribution': 0.5},
            'wildfire': {'search_rescue': 0.6, 'resource_distribution': 0.8, 'damage_assessment': 0.7},
            'hurricane': {'search_rescue': 0.7, 'resource_distribution': 0.9, 'damage_assessment': 0.8}
        }

        base_reqs = type_requirements.get(disaster_type, {'search_rescue': 0.7, 'resource_distribution': 0.7, 'damage_assessment': 0.7})

        # Adjust for severity
        severity_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 1.5, 'critical': 2.0}
        multiplier = severity_multipliers.get(severity, 1.0)

        # Adjust for area size
        area_size = (affected_area['max_lat'] - affected_area['min_lat']) * (affected_area['max_lng'] - affected_area['min_lng'])
        area_multiplier = min(2.0, 1.0 + area_size * 10)  # Scale with area size

        for response_type, base_priority in base_reqs.items():
            requirements[response_type] = {
                'priority': base_priority * multiplier * area_multiplier,
                'required_agents': max(5, int(20 * base_priority * multiplier)),
                'time_estimate': 30 * multiplier,  # minutes
                'resource_needs': self._get_resource_needs(response_type, multiplier)
            }

        return requirements

    def _get_resource_needs(self, response_type: str, multiplier: float) -> Dict[str, Any]:
        """Get resource requirements for response type."""
        resource_needs = {
            'search_rescue': {'drones': 10, 'human_teams': 5, 'medical_kits': 20},
            'damage_assessment': {'drones': 15, 'sensors': 30, 'communication_devices': 10},
            'resource_distribution': {'ground_vehicles': 20, 'supplies': 100, 'fuel': 50}
        }

        base_needs = resource_needs.get(response_type, {'drones': 5, 'human_teams': 3})
        return {k: int(v * multiplier) for k, v in base_needs.items()}

    def _calculate_resource_requirements(
        self,
        requirements: Dict[str, Any],
        available_resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate resource allocation requirements."""
        resource_reqs = {
            'total_required': {},
            'resource_gaps': {},
            'allocation_priority': {},
            'logistical_constraints': {}
        }

        # Aggregate resource requirements
        total_required = defaultdict(int)
        for response_type, req_data in requirements.items():
            for resource, amount in req_data['resource_needs'].items():
                total_required[resource] += amount

        resource_reqs['total_required'] = dict(total_required)

        # Identify resource gaps
        for resource, required in total_required.items():
            available = available_resources.get(resource, 0)
            gap = max(0, required - available)
            resource_reqs['resource_gaps'][resource] = gap
            resource_reqs['allocation_priority'][resource] = required / max(1, available)

        return resource_reqs

    def _identify_priority_zones(
        self,
        affected_area: Dict[str, float],
        disaster_type: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """Identify priority zones within affected area."""
        priority_zones = []

        # Simplified priority zone identification
        # In practice, would use actual vulnerability mapping and population data

        # Create priority zones based on disaster type
        if disaster_type in ['flood', 'hurricane']:
            # Water-related disasters: prioritize low-lying areas
            priority_zones.append({
                'zone_id': 'flood_prone_1',
                'bounds': affected_area,
                'priority_level': 'critical',
                'response_types': ['search_rescue', 'resource_distribution'],
                'estimated_population': 1000,
                'vulnerability_factors': ['elevation', 'proximity_to_water']
            })

        elif disaster_type == 'earthquake':
            # Earthquake: prioritize urban areas and infrastructure
            priority_zones.append({
                'zone_id': 'urban_core_1',
                'bounds': affected_area,
                'priority_level': 'high',
                'response_types': ['search_rescue', 'damage_assessment'],
                'estimated_population': 5000,
                'vulnerability_factors': ['building_density', 'infrastructure_criticality']
            })

        elif disaster_type == 'wildfire':
            # Wildfire: prioritize evacuation routes and high-risk areas
            priority_zones.append({
                'zone_id': 'evacuation_routes_1',
                'bounds': affected_area,
                'priority_level': 'high',
                'response_types': ['resource_distribution', 'search_rescue'],
                'estimated_population': 2000,
                'vulnerability_factors': ['wind_direction', 'fuel_load', 'proximity_to_habitats']
            })

        # Adjust priorities based on severity
        if severity == 'critical':
            for zone in priority_zones:
                if zone['priority_level'] == 'high':
                    zone['priority_level'] = 'critical'
        elif severity == 'low':
            for zone in priority_zones:
                if zone['priority_level'] == 'high':
                    zone['priority_level'] = 'medium'

        return priority_zones

    def _assess_risk_factors(
        self,
        environmental_conditions: Dict[str, Any],
        disaster_type: str
    ) -> Dict[str, Any]:
        """Assess risk factors for response operations."""
        risk_factors = {
            'environmental_risks': {},
            'operational_risks': {},
            'coordination_risks': {},
            'overall_risk_level': 'medium'
        }

        # Environmental risks
        weather_risks = environmental_conditions.get('weather_risks', {})
        risk_factors['environmental_risks'] = {
            'weather_volatility': weather_risks.get('volatility', 0.5),
            'visibility': weather_risks.get('visibility', 1.0),
            'temperature_extremes': weather_risks.get('temperature_extremes', False)
        }

        # Operational risks based on disaster type
        if disaster_type == 'wildfire':
            risk_factors['operational_risks']['fire_spread'] = 0.8
            risk_factors['operational_risks']['smoke_hazards'] = 0.7
        elif disaster_type == 'flood':
            risk_factors['operational_risks']['water_currents'] = 0.6
            risk_factors['operational_risks']['contamination'] = 0.5

        # Coordination risks
        risk_factors['coordination_risks'] = {
            'communication_degradation': 0.3,
            'resource_conflicts': 0.4,
            'agency_coordination': 0.2
        }

        # Overall risk assessment
        all_risks = []
        for category in ['environmental_risks', 'operational_risks', 'coordination_risks']:
            category_risks = risk_factors[category]
            if isinstance(category_risks, dict):
                all_risks.extend(category_risks.values())
            else:
                all_risks.append(category_risks)

        avg_risk = np.mean(all_risks) if all_risks else 0.5

        if avg_risk > 0.7:
            risk_factors['overall_risk_level'] = 'high'
        elif avg_risk > 0.4:
            risk_factors['overall_risk_level'] = 'medium'
        else:
            risk_factors['overall_risk_level'] = 'low'

        return risk_factors

    def _estimate_response_time(
        self,
        requirements: Dict[str, Any],
        resource_reqs: Dict[str, Any]
    ) -> float:
        """Estimate total response time."""
        # Simplified time estimation
        setup_time = 15  # minutes for initial setup
        deployment_time = 20  # minutes for agent deployment

        # Operation time based on requirements
        operation_times = []
        for response_type, req_data in requirements.items():
            operation_times.append(req_data['time_estimate'])

        total_operation_time = max(operation_times) if operation_times else 60

        # Add buffer for resource gaps
        resource_gaps = resource_reqs.get('resource_gaps', {})
        gap_penalty = sum(gaps for gaps in resource_gaps.values()) * 0.1  # 0.1 minutes per unit gap

        total_time = setup_time + deployment_time + total_operation_time + gap_penalty

        return total_time

    async def coordinate_response(
        self,
        situation_assessment: Dict[str, Any],
        response_priorities: Optional[Dict[str, float]] = None,
        resource_allocation: Optional[Dict[str, Any]] = None,
        communication_networks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate disaster response activities.

        Args:
            situation_assessment: Results from situation assessment
            response_priorities: Priority levels for different response types
            resource_allocation: How to allocate available resources
            communication_networks: Available communication networks

        Returns:
            Coordinated response plan
        """
        logger.info("Coordinating disaster response activities")

        coordination_plan = {
            'coordination_time': datetime.now(),
            'response_assignments': {},
            'communication_plan': {},
            'resource_deployment': {},
            'coordination_metrics': {},
            'contingency_plans': []
        }

        try:
            # Assign response tasks to agents
            assignments = self._assign_response_tasks(
                situation_assessment, response_priorities, resource_allocation
            )
            coordination_plan['response_assignments'] = assignments

            # Generate communication plan
            comm_plan = self._generate_communication_plan(
                situation_assessment, communication_networks or ['radio', 'satellite', 'mesh_network']
            )
            coordination_plan['communication_plan'] = comm_plan

            # Plan resource deployment
            deployment = self._plan_resource_deployment(
                situation_assessment, resource_allocation
            )
            coordination_plan['resource_deployment'] = deployment

            # Calculate coordination metrics
            metrics = self._calculate_coordination_metrics(assignments, deployment)
            coordination_plan['coordination_metrics'] = metrics

            # Generate contingency plans
            contingencies = self._generate_contingency_plans(situation_assessment)
            coordination_plan['contingency_plans'] = contingencies

        except Exception as e:
            logger.error(f"Response coordination failed: {e}")
            coordination_plan['error'] = str(e)

        logger.info(f"Response coordination completed: {len(coordination_plan['response_assignments'])} assignments")
        return coordination_plan

    def _assign_response_tasks(
        self,
        assessment: Dict[str, Any],
        priorities: Optional[Dict[str, float]],
        resources: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assign response tasks to available agents."""
        assignments = {
            'task_assignments': {},
            'agent_utilization': {},
            'coverage_analysis': {},
            'optimization_objective': 'maximize_coverage_minimize_time'
        }

        # Get response requirements
        requirements = assessment.get('response_requirements', {})
        available_resources = assessment.get('available_resources', self.swarm_composition)

        # Simple assignment based on requirements and availability
        for response_type, req_data in requirements.items():
            required_agents = req_data['required_agents']
            available_for_type = available_resources.get(response_type.split('_')[0], 0)

            # Assign minimum of required and available
            assigned_count = min(required_agents, available_for_type)

            assignments['task_assignments'][response_type] = {
                'assigned_agents': assigned_count,
                'required_agents': required_agents,
                'assignment_ratio': assigned_count / required_agents,
                'priority': req_data['priority']
            }

        return assignments

    def _generate_communication_plan(
        self,
        assessment: Dict[str, Any],
        networks: List[str]
    ) -> Dict[str, Any]:
        """Generate communication plan for response coordination."""
        plan = {
            'primary_network': networks[0] if networks else 'radio',
            'backup_networks': networks[1:] if len(networks) > 1 else [],
            'communication_frequency': 'continuous',
            'information_priority': {},
            'coordination_checkpoints': []
        }

        # Set information priorities
        disaster_type = assessment.get('disaster_type', 'unknown')
        if disaster_type == 'earthquake':
            plan['information_priority'] = {
                'structural_damage': 'critical',
                'casualty_reports': 'critical',
                'infrastructure_status': 'high'
            }
        elif disaster_type == 'flood':
            plan['information_priority'] = {
                'water_levels': 'critical',
                'evacuation_status': 'critical',
                'rescue_requests': 'high'
            }

        # Set coordination checkpoints
        plan['coordination_checkpoints'] = [
            {'time_offset': 15, 'type': 'status_check'},
            {'time_offset': 30, 'type': 'progress_review'},
            {'time_offset': 60, 'type': 'resource_reallocation'}
        ]

        return plan

    def _plan_resource_deployment(
        self,
        assessment: Dict[str, Any],
        allocation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Plan deployment of response resources."""
        deployment = {
            'deployment_schedule': {},
            'resource_routes': {},
            'staging_areas': [],
            'supply_chain': {}
        }

        # Simple deployment planning
        priority_zones = assessment.get('priority_zones', [])
        resource_requirements = assessment.get('resource_requirements', {})

        for i, zone in enumerate(priority_zones):
            deployment['deployment_schedule'][zone['zone_id']] = {
                'deployment_order': i + 1,
                'estimated_arrival': datetime.now() + timedelta(minutes=15 * (i + 1)),
                'required_resources': resource_requirements.get('total_required', {})
            }

        return deployment

    def _calculate_coordination_metrics(
        self,
        assignments: Dict[str, Any],
        deployment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate coordination quality metrics."""
        metrics = {
            'assignment_efficiency': 0.0,
            'resource_utilization': 0.0,
            'coverage_effectiveness': 0.0,
            'coordination_overhead': 0.0
        }

        try:
            # Assignment efficiency
            task_assignments = assignments.get('task_assignments', {})
            if task_assignments:
                efficiency_scores = [
                    task_data.get('assignment_ratio', 0.0)
                    for task_data in task_assignments.values()
                ]
                metrics['assignment_efficiency'] = np.mean(efficiency_scores)

            # Resource utilization
            resource_utilization = 0.8  # Simplified calculation
            metrics['resource_utilization'] = resource_utilization

            # Coverage effectiveness (simplified)
            metrics['coverage_effectiveness'] = 0.75

            # Coordination overhead
            metrics['coordination_overhead'] = 0.15  # 15% overhead for coordination

        except Exception as e:
            logger.warning(f"Coordination metrics calculation failed: {e}")

        return metrics

    def _generate_contingency_plans(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contingency plans for various scenarios."""
        contingencies = []

        # Risk-based contingency planning
        risk_factors = assessment.get('risk_factors', {})

        if risk_factors.get('environmental_risks', {}).get('weather_volatility', 0) > 0.7:
            contingencies.append({
                'trigger': 'weather_deterioration',
                'plan': 'evacuate_teams',
                'priority': 'high',
                'alternative_coordination': 'satellite_communication'
            })

        if risk_factors.get('overall_risk_level') == 'high':
            contingencies.append({
                'trigger': 'high_overall_risk',
                'plan': 'increase_redundancy',
                'priority': 'medium',
                'additional_resources': {'backup_teams': 5, 'communication_redundancy': True}
            })

        # Resource gap contingencies
        resource_gaps = assessment.get('resource_requirements', {}).get('resource_gaps', {})
        if any(gaps > 0 for gaps in resource_gaps.values()):
            contingencies.append({
                'trigger': 'resource_shortage',
                'plan': 'prioritize_critical_tasks',
                'priority': 'medium',
                'resource_reallocation': True
            })

        return contingencies

    async def adapt_response(
        self,
        current_situation: Dict[str, Any],
        performance_feedback: Dict[str, Any],
        environmental_changes: Optional[Dict[str, Any]] = None,
        resource_availability: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adapt response strategy based on current conditions and performance.

        Args:
            current_situation: Current disaster situation
            performance_feedback: Performance metrics and feedback
            environmental_changes: Changes in environmental conditions
            resource_availability: Current resource availability

        Returns:
            Adapted response plan
        """
        logger.info("Adapting disaster response strategy")

        adaptation = {
            'adaptation_time': datetime.now(),
            'strategy_changes': [],
            'resource_reallocations': {},
            'priority_adjustments': {},
            'communication_updates': {},
            'performance_improvements': []
        }

        try:
            # Analyze current performance
            current_performance = performance_feedback.get('current_metrics', {})

            # Adapt based on performance gaps
            if current_performance.get('efficiency', 1.0) < 0.7:
                adaptation['strategy_changes'].append('increase_coordination_frequency')
                adaptation['performance_improvements'].append('optimize_task_assignment')

            if current_performance.get('coverage', 1.0) < 0.8:
                adaptation['strategy_changes'].append('expand_search_area')
                adaptation['resource_reallocations']['additional_search_teams'] = 3

            # Adapt to environmental changes
            if environmental_changes:
                env_adaptation = self._adapt_to_environmental_changes(environmental_changes)
                adaptation.update(env_adaptation)

            # Adapt to resource changes
            if resource_availability:
                resource_adaptation = self._adapt_to_resource_changes(resource_availability)
                adaptation['resource_reallocations'].update(resource_adaptation)

            # Update priorities based on situation evolution
            priority_updates = self._update_response_priorities(current_situation)
            adaptation['priority_adjustments'] = priority_updates

            # Update communication strategy
            comm_updates = self._update_communication_strategy(current_situation)
            adaptation['communication_updates'] = comm_updates

        except Exception as e:
            logger.error(f"Response adaptation failed: {e}")
            adaptation['error'] = str(e)

        logger.info(f"Response adaptation completed: {len(adaptation['strategy_changes'])} strategy changes")
        return adaptation

    def _adapt_to_environmental_changes(self, env_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt response to environmental changes."""
        adaptation = {
            'environmental_changes': env_changes,
            'strategy_changes': [],
            'safety_measures': []
        }

        # Weather-related adaptations
        if 'weather' in env_changes:
            weather = env_changes['weather']

            if weather.get('visibility', 1.0) < 0.5:
                adaptation['strategy_changes'].append('switch_to_instrument_navigation')
                adaptation['safety_measures'].append('increase_team_separation')

            if weather.get('wind_speed', 0) > 15:
                adaptation['strategy_changes'].append('adjust_drone_operations')
                adaptation['safety_measures'].append('ground_drone_teams')

        # Hazard-related adaptations
        if 'hazards' in env_changes:
            hazards = env_changes['hazards']

            if hazards.get('contamination', False):
                adaptation['safety_measures'].append('require_protective_equipment')
                adaptation['strategy_changes'].append('adjust_decontamination_protocols')

        return adaptation

    def _adapt_to_resource_changes(self, resource_availability: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt response to resource availability changes."""
        reallocations = {}

        # Check for resource shortages
        if self.current_scenario:
            resource_gaps = self.current_scenario.available_resources
            current_resources = resource_availability

            for resource, available in current_resources.items():
                required = resource_gaps.get(resource, 0)
                if available < required * 0.8:  # Less than 80% of required
                    reallocations[f'reduce_{resource}_usage'] = True

        return reallocations

    def _update_response_priorities(self, current_situation: Dict[str, Any]) -> Dict[str, float]:
        """Update response priorities based on current situation."""
        priorities = {}

        # Base priorities from current scenario
        if self.current_scenario:
            base_priorities = {
                'search_rescue': 0.9,
                'damage_assessment': 0.7,
                'resource_distribution': 0.6
            }

            # Adjust based on time elapsed
            time_elapsed = (datetime.now() - current_situation.get('start_time', datetime.now())).total_seconds() / 3600
            if time_elapsed > 2:  # After 2 hours
                priorities['resource_distribution'] = 0.8  # Increase priority of resource distribution
                priorities['damage_assessment'] = 0.5    # Decrease priority of damage assessment

            # Adjust based on progress
            progress = current_situation.get('completion_rate', 0.5)
            if progress < 0.3:
                priorities['search_rescue'] = 1.0  # Maximum priority for search and rescue
            elif progress > 0.8:
                priorities['resource_distribution'] = 1.0  # Focus on resource distribution in final phase

        return priorities

    def _update_communication_strategy(self, current_situation: Dict[str, Any]) -> Dict[str, Any]:
        """Update communication strategy based on current conditions."""
        updates = {
            'communication_frequency': 'standard',
            'information_priorities': {},
            'network_redundancy': False
        }

        # Adjust based on situation severity
        severity = current_situation.get('severity', 'medium')
        if severity == 'critical':
            updates['communication_frequency'] = 'high'
            updates['network_redundancy'] = True

        # Adjust based on communication reliability
        comm_reliability = current_situation.get('communication_reliability', 0.9)
        if comm_reliability < 0.7:
            updates['communication_frequency'] = 'continuous'
            updates['network_redundancy'] = True

        return updates

    def get_response_status(self) -> Dict[str, Any]:
        """Get current disaster response status."""
        status = {
            'response_active': self.current_scenario is not None,
            'current_scenario': self.current_scenario.__dict__ if self.current_scenario else None,
            'coordination_protocol': self.coordination_protocol,
            'real_time_adaptation': self.real_time_adaptation,
            'performance_metrics': {
                'response_efficiency': self.response_efficiency,
                'coverage_effectiveness': self.coverage_effectiveness,
                'coordination_quality': self.coordination_quality
            },
            'resource_status': {
                'total_agents': sum(self.swarm_composition.values()),
                'composition': self.swarm_composition,
                'utilization': 0.8  # Simplified
            }
        }

        if self.current_scenario:
            status['time_remaining'] = (
                self.current_scenario.time_constraints.get('response_window', 7200) -
                (datetime.now() - status['current_scenario']['timestamp']).total_seconds()
            )

        return status
