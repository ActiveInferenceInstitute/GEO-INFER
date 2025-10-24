"""
Environmental Monitoring Swarm Applications for GEO-INFER-ANT

This module implements specialized swarm applications for environmental monitoring,
including air quality, water quality, biodiversity, and ecological system monitoring.
The applications integrate multiple swarm intelligence algorithms with real-time
data collection and adaptive sampling strategies.

Key Features:
- Multi-objective environmental monitoring
- Adaptive sampling based on environmental variability
- Real-time sensor data integration
- Biodiversity and ecosystem health assessment
- Pollution tracking and source identification
- Integration with IoT sensor networks
"""

import numpy as np
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

# Integration imports
try:
    from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
    from geo_infer_space.core.analytics import SpatialAnalyticsInterface
    from geo_infer_ant.core.agent_base import SwarmAgent
    from geo_infer_ant.core.population import AgentPopulation
    from geo_infer_ant.core.stigmergy import PheromoneSystem
    from geo_infer_ant.core.digital_stigmergy import DigitalStigmergy
    from geo_infer_ant.algorithms.aco import AntColonyOptimization
    from geo_infer_ant.algorithms.pso import ParticleSwarmOptimization
except ImportError as e:
    logging.warning(f"Integration modules not available: {e}")
    SwarmAgent = None
    AgentPopulation = None
    PheromoneSystem = None
    DigitalStigmergy = None
    AntColonyOptimization = None
    ParticleSwarmOptimization = None

logger = logging.getLogger(__name__)


@dataclass
class MonitoringObjective:
    """Configuration for environmental monitoring objectives."""
    name: str
    sensor_types: List[str]
    priority: float = 1.0
    target_accuracy: float = 0.9
    temporal_resolution: str = 'continuous'  # 'continuous', 'hourly', 'daily'
    spatial_resolution: str = 'high'  # 'low', 'medium', 'high'
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class SensorReading:
    """Individual sensor reading from monitoring agent."""
    agent_id: str
    sensor_type: str
    value: float
    location: np.ndarray
    timestamp: datetime
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnvironmentalMonitoringSwarm:
    """
    Comprehensive environmental monitoring system using swarm intelligence.

    This application coordinates multiple types of monitoring agents to collect
    environmental data, detect anomalies, optimize sampling strategies, and
    provide real-time environmental intelligence.

    Key Features:
    - Multi-sensor environmental monitoring
    - Adaptive sampling strategies
    - Anomaly detection and alerting
    - Spatial interpolation and mapping
    - Real-time data integration
    - Multi-objective optimization
    """

    def __init__(
        self,
        swarm_size: int = 200,
        monitoring_objectives: Optional[List[str]] = None,
        spatial_coverage: Optional[Dict[str, float]] = None,
        temporal_coverage: str = 'continuous',
        adaptive_sampling: bool = True,
        real_time_processing: bool = True,
        **kwargs
    ):
        """
        Initialize environmental monitoring swarm.

        Args:
            swarm_size: Number of monitoring agents
            monitoring_objectives: Types of environmental monitoring to perform
            spatial_coverage: Geographic area to monitor
            temporal_coverage: Temporal resolution of monitoring
            adaptive_sampling: Whether to use adaptive sampling strategies
            real_time_processing: Whether to process data in real-time
            **kwargs: Additional configuration parameters
        """
        self.swarm_size = swarm_size
        self.monitoring_objectives = monitoring_objectives or ['air_quality', 'water_quality', 'biodiversity']
        self.spatial_coverage = spatial_coverage or {'min_lat': 35, 'max_lat': 40, 'min_lng': -120, 'max_lng': -115}
        self.temporal_coverage = temporal_coverage
        self.adaptive_sampling = adaptive_sampling
        self.real_time_processing = real_time_processing

        # Monitoring system state
        self.monitoring_agents: List[SwarmAgent] = []
        self.pheromone_system: Optional[PheromoneSystem] = None
        self.digital_stigmergy: Optional[DigitalStigmergy] = None
        self.spatial_analytics: Optional[Any] = None

        # Data collection and analysis
        self.sensor_data: List[SensorReading] = []
        self.anomaly_history: List[Dict[str, Any]] = []
        self.coverage_maps: Dict[str, np.ndarray] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Optimization components
        self.sampling_optimizer: Optional[AntColonyOptimization] = None
        self.coverage_optimizer: Optional[ParticleSwarmOptimization] = None

        # Performance tracking
        self.monitoring_efficiency: float = 0.0
        self.coverage_quality: float = 0.0
        self.anomaly_detection_rate: float = 0.0

        # Initialize system components
        self._initialize_monitoring_system()

        logger.info(f"EnvironmentalMonitoringSwarm initialized with {swarm_size} agents")

    def _initialize_monitoring_system(self) -> None:
        """Initialize all monitoring system components."""
        # Initialize pheromone system for coordination
        if PheromoneSystem:
            try:
                self.pheromone_system = PheromoneSystem(
                    spatial_resolution='h3_r8',
                    pheromone_types=['monitoring', 'anomaly', 'coverage', 'priority'],
                    bounds=self.spatial_coverage
                )
                logger.info("Pheromone system initialized for environmental monitoring")
            except Exception as e:
                logger.warning(f"Failed to initialize pheromone system: {e}")

        # Initialize digital stigmergy for information sharing
        if DigitalStigmergy:
            try:
                self.digital_stigmergy = DigitalStigmergy(
                    communication_medium='iot_network',
                    information_types=['sensor_data', 'anomaly_detection', 'coverage_info', 'alerts'],
                    persistence_model='temporal_decay'
                )
                logger.info("Digital stigmergy initialized for environmental monitoring")
            except Exception as e:
                logger.warning(f"Failed to initialize digital stigmergy: {e}")

        # Initialize optimization algorithms
        if AntColonyOptimization:
            try:
                self.sampling_optimizer = AntColonyOptimization(
                    number_of_ants=30,
                    max_iterations=50,
                    variant='ACS'
                )
                logger.info("Sampling optimizer initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize sampling optimizer: {e}")

        if ParticleSwarmOptimization:
            try:
                self.coverage_optimizer = ParticleSwarmOptimization(
                    swarm_size=50,
                    dimensions=2,
                    bounds=[(self.spatial_coverage['min_lat'], self.spatial_coverage['max_lat']),
                           (self.spatial_coverage['min_lng'], self.spatial_coverage['max_lng'])],
                    max_iterations=100
                )
                logger.info("Coverage optimizer initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize coverage optimizer: {e}")

    async def deploy_agents(
        self,
        initial_positions: Optional[List[np.ndarray]] = None,
        environmental_priorities: Optional[Dict[str, float]] = None,
        logistical_constraints: Optional[Dict[str, Any]] = None,
        communication_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deploy monitoring agents across the target area.

        Args:
            initial_positions: Initial positions for agents (optimized if None)
            environmental_priorities: Priority areas for monitoring
            logistical_constraints: Constraints on agent deployment
            communication_requirements: Communication network requirements

        Returns:
            Deployment plan and agent configurations
        """
        logger.info(f"Deploying {self.swarm_size} monitoring agents")

        deployment_plan = {
            'agents': [],
            'deployment_strategy': 'optimized',
            'coverage_achieved': 0.0,
            'deployment_time': datetime.now(),
            'agent_configurations': {}
        }

        # Optimize initial positions if not provided
        if initial_positions is None:
            initial_positions = await self._optimize_initial_positions(
                environmental_priorities or {},
                logistical_constraints or {}
            )

        # Create monitoring agents
        for i in range(self.swarm_size):
            agent_id = f"env_monitor_{i+1:03d}"

            # Determine agent position
            position = initial_positions[i] if i < len(initial_positions) else self._generate_random_position()

            # Configure agent based on monitoring objectives
            agent_config = self._configure_monitoring_agent(
                agent_id, position, self.monitoring_objectives
            )

            # Create agent (would use actual SwarmAgent when available)
            agent_info = {
                'agent_id': agent_id,
                'position': position,
                'config': agent_config,
                'monitoring_objectives': self.monitoring_objectives,
                'deployment_time': datetime.now()
            }

            deployment_plan['agents'].append(agent_info)
            deployment_plan['agent_configurations'][agent_id] = agent_config

        # Calculate expected coverage
        deployment_plan['coverage_achieved'] = self._calculate_deployment_coverage(deployment_plan['agents'])

        logger.info(f"Agent deployment completed: {len(deployment_plan['agents'])} agents deployed")
        return deployment_plan

    async def _optimize_initial_positions(
        self,
        environmental_priorities: Dict[str, float],
        logistical_constraints: Dict[str, Any]
    ) -> List[np.ndarray]:
        """Optimize initial positions for maximum coverage and priority alignment."""
        if not self.coverage_optimizer:
            # Fallback to simple grid distribution
            return self._generate_grid_positions()

        try:
            # Define optimization objective for coverage
            def coverage_objective(positions: np.ndarray) -> float:
                if len(positions) == 0:
                    return 0.0

                # Calculate coverage quality (simplified)
                coverage_score = 0.0

                # Position diversity score
                if len(positions) > 1:
                    distances = []
                    for i in range(len(positions)):
                        for j in range(i+1, len(positions)):
                            dist = np.linalg.norm(positions[i] - positions[j])
                            distances.append(dist)

                    avg_distance = np.mean(distances)
                    # Optimal distance for coverage (balance between overlap and gaps)
                    optimal_distance = 0.01  # degrees (roughly 1km)
                    coverage_score += 1.0 / (1.0 + abs(avg_distance - optimal_distance))

                # Priority alignment score
                priority_score = 0.0
                for pos in positions:
                    # Calculate priority score for this position (simplified)
                    priority_score += self._calculate_position_priority(pos, environmental_priorities)

                coverage_score += priority_score / len(positions)

                return coverage_score

            # Initialize positions randomly
            initial_positions = np.array([
                [np.random.uniform(self.spatial_coverage['min_lat'], self.spatial_coverage['max_lat']),
                 np.random.uniform(self.spatial_coverage['min_lng'], self.spatial_coverage['max_lng'])]
                for _ in range(self.swarm_size)
            ])

            # Optimize positions
            optimal_positions = self.coverage_optimizer.optimize(coverage_objective, initial_positions)

            # Convert back to list of arrays
            return [optimal_positions[i] for i in range(len(optimal_positions))]

        except Exception as e:
            logger.warning(f"Position optimization failed: {e}")
            return self._generate_grid_positions()

    def _generate_grid_positions(self) -> List[np.ndarray]:
        """Generate grid-based initial positions."""
        positions = []

        # Calculate grid dimensions
        area_width = self.spatial_coverage['max_lng'] - self.spatial_coverage['min_lng']
        area_height = self.spatial_coverage['max_lat'] - self.spatial_coverage['min_lat']

        grid_cols = int(np.sqrt(self.swarm_size))
        grid_rows = (self.swarm_size + grid_cols - 1) // grid_cols

        lat_step = area_height / grid_rows if grid_rows > 1 else 0
        lng_step = area_width / grid_cols if grid_cols > 1 else 0

        for i in range(self.swarm_size):
            row = i // grid_cols
            col = i % grid_cols

            lat = self.spatial_coverage['min_lat'] + (row + 0.5) * lat_step
            lng = self.spatial_coverage['min_lng'] + (col + 0.5) * lng_step

            positions.append(np.array([lat, lng]))

        return positions

    def _generate_random_position(self) -> np.ndarray:
        """Generate random position within coverage area."""
        return np.array([
            np.random.uniform(self.spatial_coverage['min_lat'], self.spatial_coverage['max_lat']),
            np.random.uniform(self.spatial_coverage['min_lng'], self.spatial_coverage['max_lng'])
        ])

    def _configure_monitoring_agent(self, agent_id: str, position: np.ndarray, objectives: List[str]) -> Dict[str, Any]:
        """Configure individual monitoring agent."""
        config = {
            'agent_id': agent_id,
            'position': position,
            'monitoring_objectives': objectives,
            'sensory_capabilities': self._get_sensory_capabilities(objectives),
            'communication_range': 1000.0,  # meters
            'energy_capacity': 100.0,
            'sampling_frequency': self._get_sampling_frequency(),
            'data_quality_threshold': 0.8,
            'adaptive_behavior': self.adaptive_sampling
        }

        return config

    def _get_sensory_capabilities(self, objectives: List[str]) -> List[str]:
        """Get sensory capabilities based on monitoring objectives."""
        capabilities = []

        for objective in objectives:
            if objective == 'air_quality':
                capabilities.extend(['pm25_sensor', 'no2_sensor', 'o3_sensor', 'temperature', 'humidity'])
            elif objective == 'water_quality':
                capabilities.extend(['ph_sensor', 'turbidity_sensor', 'conductivity_sensor', 'temperature'])
            elif objective == 'biodiversity':
                capabilities.extend(['camera', 'microphone', 'species_detector', 'habitat_sensor'])
            elif objective == 'soil_quality':
                capabilities.extend(['moisture_sensor', 'ph_sensor', 'nutrient_sensor', 'compaction_sensor'])

        return list(set(capabilities))  # Remove duplicates

    def _get_sampling_frequency(self) -> str:
        """Get sampling frequency based on temporal coverage."""
        frequency_map = {
            'continuous': '1_minute',
            'hourly': '1_hour',
            'daily': '1_day'
        }
        return frequency_map.get(self.temporal_coverage, '1_hour')

    def _calculate_position_priority(self, position: np.ndarray, priorities: Dict[str, float]) -> float:
        """Calculate priority score for a position."""
        # Simplified priority calculation
        # In practice, would use actual priority maps and spatial analysis
        priority_score = 0.0

        # Base priority from environmental priorities
        for priority_type, weight in priorities.items():
            # Distance to priority features (simplified)
            if priority_type == 'pollution_sources':
                priority_score += weight * 0.8  # Assume high priority near sources
            elif priority_type == 'sensitive_areas':
                priority_score += weight * 0.9  # Assume high priority in sensitive areas

        return min(1.0, priority_score)

    def _calculate_deployment_coverage(self, deployed_agents: List[Dict[str, Any]]) -> float:
        """Calculate expected coverage quality of deployment."""
        if not deployed_agents:
            return 0.0

        # Simplified coverage calculation
        # In practice, would use spatial analysis and sensor range modeling
        positions = np.array([agent['position'] for agent in deployed_agents])

        # Calculate spatial distribution quality
        if len(positions) > 1:
            distances = []
            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    distances.append(np.linalg.norm(positions[i] - positions[j]))

            avg_distance = np.mean(distances)
            # Optimal distance for sensor coverage (assuming 500m range)
            optimal_distance = 0.005  # degrees (roughly 500m)
            coverage_quality = 1.0 / (1.0 + abs(avg_distance - optimal_distance))
        else:
            coverage_quality = 1.0

        return min(1.0, coverage_quality)

    async def coordinate_monitoring(
        self,
        agent_positions: List[np.ndarray],
        environmental_conditions: Optional[Dict[str, Any]] = None,
        data_priorities: Optional[Dict[str, float]] = None,
        energy_constraints: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate monitoring activities across all agents.

        Args:
            agent_positions: Current positions of all agents
            environmental_conditions: Current environmental conditions
            data_priorities: Priority levels for different data types
            energy_constraints: Energy limitations for agents

        Returns:
            Coordinated monitoring plan and instructions
        """
        logger.info(f"Coordinating monitoring for {len(agent_positions)} agents")

        coordination_plan = {
            'monitoring_instructions': {},
            'sampling_strategy': 'adaptive' if self.adaptive_sampling else 'uniform',
            'communication_protocol': 'pheromone_digital_hybrid',
            'coordination_time': datetime.now(),
            'estimated_coverage': 0.0,
            'priority_areas': []
        }

        # Update environmental conditions in pheromone system
        if self.pheromone_system and environmental_conditions:
            await self.pheromone_system.diffuse_pheromones(
                time_step=60.0,  # 1 minute
                environmental_conditions=environmental_conditions
            )

        # Generate adaptive sampling strategy
        if self.adaptive_sampling:
            sampling_strategy = await self._generate_adaptive_sampling_strategy(
                agent_positions, environmental_conditions, data_priorities
            )
            coordination_plan['sampling_strategy'] = sampling_strategy

        # Generate communication instructions
        communication_plan = self._generate_communication_plan(agent_positions)
        coordination_plan.update(communication_plan)

        # Calculate estimated coverage
        coordination_plan['estimated_coverage'] = self._calculate_monitoring_coverage(agent_positions)

        # Identify priority monitoring areas
        if data_priorities:
            priority_areas = self._identify_priority_areas(data_priorities)
            coordination_plan['priority_areas'] = priority_areas

        logger.info(f"Monitoring coordination completed: {len(coordination_plan['monitoring_instructions'])} instructions generated")
        return coordination_plan

    async def _generate_adaptive_sampling_strategy(
        self,
        agent_positions: List[np.ndarray],
        environmental_conditions: Optional[Dict[str, Any]] = None,
        data_priorities: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Generate adaptive sampling strategy based on current conditions."""
        strategy = {
            'strategy_type': 'adaptive',
            'sampling_zones': {},
            'agent_assignments': {},
            'sampling_frequencies': {}
        }

        try:
            # Divide area into sampling zones based on environmental variability
            if self.spatial_analytics:
                zones = self._create_sampling_zones(agent_positions, environmental_conditions)
                strategy['sampling_zones'] = zones

                # Assign agents to zones
                assignments = self._assign_agents_to_zones(agent_positions, zones)
                strategy['agent_assignments'] = assignments

            # Set sampling frequencies based on priorities and conditions
            base_frequency = self._get_sampling_frequency()
            strategy['sampling_frequencies'] = self._calculate_sampling_frequencies(
                data_priorities or {}, environmental_conditions or {}
            )

        except Exception as e:
            logger.warning(f"Adaptive sampling strategy generation failed: {e}")
            strategy['strategy_type'] = 'uniform'
            strategy['error'] = str(e)

        return strategy

    def _create_sampling_zones(self, agent_positions: List[np.ndarray], conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Create sampling zones based on environmental variability."""
        # Simplified zone creation
        # In practice, would use spatial clustering and environmental analysis
        zones = {
            'high_priority': {
                'bounds': self.spatial_coverage,
                'required_agents': max(1, len(agent_positions) // 3),
                'sampling_frequency': '5_minutes'
            },
            'medium_priority': {
                'bounds': self.spatial_coverage,
                'required_agents': max(1, len(agent_positions) // 2),
                'sampling_frequency': '15_minutes'
            },
            'low_priority': {
                'bounds': self.spatial_coverage,
                'required_agents': len(agent_positions) - (len(agent_positions) // 3 + len(agent_positions) // 2),
                'sampling_frequency': '1_hour'
            }
        }

        return zones

    def _assign_agents_to_zones(self, agent_positions: List[np.ndarray], zones: Dict[str, Any]) -> Dict[str, List[str]]:
        """Assign agents to sampling zones."""
        assignments = {zone_name: [] for zone_name in zones.keys()}

        # Simple assignment based on position
        for i, position in enumerate(agent_positions):
            agent_id = f"agent_{i}"

            # Assign to zone with highest priority that needs more agents
            for zone_name, zone_info in zones.items():
                if len(assignments[zone_name]) < zone_info['required_agents']:
                    assignments[zone_name].append(agent_id)
                    break

        return assignments

    def _calculate_sampling_frequencies(self, data_priorities: Dict[str, float], conditions: Dict[str, Any]) -> Dict[str, str]:
        """Calculate optimal sampling frequencies."""
        frequencies = {}

        for objective, priority in data_priorities.items():
            if priority > 0.8:
                frequencies[objective] = '1_minute'
            elif priority > 0.5:
                frequencies[objective] = '5_minutes'
            elif priority > 0.2:
                frequencies[objective] = '15_minutes'
            else:
                frequencies[objective] = '1_hour'

        return frequencies

    def _generate_communication_plan(self, agent_positions: List[np.ndarray]) -> Dict[str, Any]:
        """Generate communication plan for agents."""
        plan = {
            'communication_instructions': {},
            'information_sharing_rules': {},
            'coordination_signals': {}
        }

        # Define communication rules
        plan['information_sharing_rules'] = {
            'share_anomalies': True,
            'share_sensor_data': True,
            'share_position_updates': True,
            'coordinate_sampling': self.adaptive_sampling
        }

        # Generate coordination signals via pheromones
        if self.pheromone_system:
            plan['coordination_signals']['pheromone_types'] = ['monitoring', 'anomaly', 'coverage']

        # Generate digital stigmergy coordination
        if self.digital_stigmergy:
            plan['coordination_signals']['digital_types'] = ['sensor_data', 'anomaly_detection', 'coverage_info']

        return plan

    def _calculate_monitoring_coverage(self, agent_positions: List[np.ndarray]) -> float:
        """Calculate current monitoring coverage quality."""
        if not agent_positions:
            return 0.0

        # Simplified coverage calculation
        # In practice, would use spatial analysis of sensor ranges and overlaps
        n_agents = len(agent_positions)

        # Base coverage from agent count
        base_coverage = min(1.0, n_agents / 50)  # Assume 50 agents needed for full coverage

        # Spatial distribution factor
        if n_agents > 1:
            positions = np.array(agent_positions)
            # Calculate area covered vs total area
            area_covered = self._estimate_covered_area(positions)
            total_area = self._calculate_total_area()
            spatial_factor = min(1.0, area_covered / total_area)
        else:
            spatial_factor = 1.0

        return base_coverage * spatial_factor

    def _estimate_covered_area(self, positions: np.ndarray) -> float:
        """Estimate area covered by agent sensors."""
        # Simplified calculation assuming circular sensor ranges
        sensor_range = 0.005  # degrees (roughly 500m)
        area_per_agent = np.pi * (sensor_range ** 2)

        # Account for overlaps (simplified)
        overlap_factor = 0.7  # Assume 30% overlap
        effective_area = n_agents * area_per_agent * overlap_factor

        return effective_area

    def _calculate_total_area(self) -> float:
        """Calculate total area of monitoring region."""
        width = self.spatial_coverage['max_lng'] - self.spatial_coverage['min_lng']
        height = self.spatial_coverage['max_lat'] - self.spatial_coverage['min_lat']
        return width * height

    def _identify_priority_areas(self, data_priorities: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify priority areas for focused monitoring."""
        priority_areas = []

        for priority_type, priority_level in data_priorities.items():
            if priority_level > 0.6:  # High priority threshold
                # Define priority area based on type
                if priority_type == 'air_quality':
                    priority_area = {
                        'type': 'air_quality_hotspot',
                        'bounds': self.spatial_coverage,  # Would be more specific in practice
                        'priority_level': priority_level,
                        'monitoring_frequency': '5_minutes'
                    }
                elif priority_type == 'water_quality':
                    priority_area = {
                        'type': 'water_body',
                        'bounds': self.spatial_coverage,
                        'priority_level': priority_level,
                        'monitoring_frequency': '15_minutes'
                    }
                else:
                    priority_area = {
                        'type': priority_type,
                        'bounds': self.spatial_coverage,
                        'priority_level': priority_level,
                        'monitoring_frequency': '15_minutes'
                    }

                priority_areas.append(priority_area)

        return priority_areas

    async def process_collective_intelligence(
        self,
        individual_measurements: List[SensorReading],
        spatial_interpolation: str = 'kriging',
        uncertainty_quantification: str = 'bayesian',
        anomaly_detection: str = 'statistical'
    ) -> Dict[str, Any]:
        """
        Process collective environmental intelligence from all agents.

        Args:
            individual_measurements: Sensor readings from all agents
            spatial_interpolation: Method for spatial interpolation
            uncertainty_quantification: Method for uncertainty analysis
            anomaly_detection: Method for anomaly detection

        Returns:
            Comprehensive environmental assessment
        """
        logger.info(f"Processing collective intelligence from {len(individual_measurements)} measurements")

        assessment = {
            'assessment_time': datetime.now(),
            'data_summary': self._summarize_measurements(individual_measurements),
            'spatial_analysis': {},
            'anomaly_detection': {},
            'uncertainty_analysis': {},
            'recommendations': []
        }

        try:
            # Spatial analysis and interpolation
            if spatial_interpolation != 'none' and self.spatial_analytics:
                spatial_results = await self._perform_spatial_analysis(
                    individual_measurements, spatial_interpolation
                )
                assessment['spatial_analysis'] = spatial_results

            # Anomaly detection
            if anomaly_detection != 'none':
                anomalies = await self._detect_anomalies(
                    individual_measurements, anomaly_detection
                )
                assessment['anomaly_detection'] = anomalies

                # Update anomaly history
                self.anomaly_history.extend(anomalies)

            # Uncertainty quantification
            if uncertainty_quantification != 'none':
                uncertainty = self._quantify_uncertainty(
                    individual_measurements, uncertainty_quantification
                )
                assessment['uncertainty_analysis'] = uncertainty

            # Generate recommendations
            recommendations = self._generate_monitoring_recommendations(assessment)
            assessment['recommendations'] = recommendations

            # Update performance metrics
            self._update_performance_metrics(individual_measurements, assessment)

        except Exception as e:
            logger.error(f"Collective intelligence processing failed: {e}")
            assessment['error'] = str(e)

        logger.info(f"Collective intelligence assessment completed: {len(assessment['recommendations'])} recommendations")
        return assessment

    def _summarize_measurements(self, measurements: List[SensorReading]) -> Dict[str, Any]:
        """Summarize measurement data."""
        if not measurements:
            return {'total_measurements': 0}

        summary = {
            'total_measurements': len(measurements),
            'measurement_types': list(set([m.sensor_type for m in measurements])),
            'time_range': {
                'start': min([m.timestamp for m in measurements]),
                'end': max([m.timestamp for m in measurements])
            },
            'spatial_range': {
                'min_lat': min([m.location[0] for m in measurements]),
                'max_lat': max([m.location[0] for m in measurements]),
                'min_lng': min([m.location[1] for m in measurements]),
                'max_lng': max([m.location[1] for m in measurements])
            }
        }

        # Statistical summaries by sensor type
        sensor_stats = defaultdict(list)
        for measurement in measurements:
            sensor_stats[measurement.sensor_type].append(measurement.value)

        summary['sensor_statistics'] = {}
        for sensor_type, values in sensor_stats.items():
            summary['sensor_statistics'][sensor_type] = {
                'count': len(values),
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }

        return summary

    async def _perform_spatial_analysis(
        self,
        measurements: List[SensorReading],
        interpolation_method: str
    ) -> Dict[str, Any]:
        """Perform spatial analysis and interpolation."""
        if not self.spatial_analytics:
            return {'status': 'spatial_analytics_unavailable'}

        try:
            # Group measurements by type
            measurements_by_type = defaultdict(list)
            for measurement in measurements:
                measurements_by_type[measurement.sensor_type].append(measurement)

            spatial_results = {}

            for sensor_type, type_measurements in measurements_by_type.items():
                if len(type_measurements) < 3:
                    continue  # Need at least 3 points for interpolation

                # Extract locations and values
                locations = np.array([m.location for m in type_measurements])
                values = np.array([m.value for m in type_measurements])

                # Perform spatial interpolation (simplified)
                if interpolation_method == 'kriging':
                    # Would use actual kriging implementation
                    interpolated_field = self._simple_kriging_interpolation(locations, values)
                elif interpolation_method == 'idw':
                    # Inverse distance weighting
                    interpolated_field = self._inverse_distance_weighting(locations, values)
                else:
                    interpolated_field = {'method': 'none', 'values': values}

                spatial_results[sensor_type] = {
                    'interpolation_method': interpolation_method,
                    'interpolated_field': interpolated_field,
                    'sample_points': len(type_measurements),
                    'spatial_coverage': self._calculate_spatial_coverage(locations)
                }

            return spatial_results

        except Exception as e:
            logger.warning(f"Spatial analysis failed: {e}")
            return {'error': str(e)}

    def _simple_kriging_interpolation(self, locations: np.ndarray, values: np.ndarray) -> Dict[str, Any]:
        """Simple kriging interpolation (placeholder)."""
        # In practice, would use actual kriging implementation
        return {
            'method': 'simple_kriging',
            'estimated_field': np.mean(values),  # Placeholder
            'variance': np.var(values)  # Placeholder
        }

    def _inverse_distance_weighting(self, locations: np.ndarray, values: np.ndarray) -> Dict[str, Any]:
        """Inverse distance weighting interpolation."""
        # Simplified IDW implementation
        return {
            'method': 'inverse_distance_weighting',
            'estimated_field': np.mean(values),
            'weights': np.ones(len(locations)) / len(locations)
        }

    def _calculate_spatial_coverage(self, locations: np.ndarray) -> float:
        """Calculate spatial coverage of measurement locations."""
        if len(locations) < 2:
            return 1.0

        # Simple coverage calculation based on area spanned
        lat_range = np.max(locations[:, 0]) - np.min(locations[:, 0])
        lng_range = np.max(locations[:, 1]) - np.min(locations[:, 1])

        total_range = lat_range + lng_range
        max_range = (self.spatial_coverage['max_lat'] - self.spatial_coverage['min_lat'] +
                    self.spatial_coverage['max_lng'] - self.spatial_coverage['min_lng'])

        return min(1.0, total_range / max_range)

    async def _detect_anomalies(
        self,
        measurements: List[SensorReading],
        detection_method: str
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in environmental measurements."""
        anomalies = []

        try:
            # Group measurements by type for anomaly detection
            measurements_by_type = defaultdict(list)
            for measurement in measurements:
                measurements_by_type[measurement.sensor_type].append(measurement)

            for sensor_type, type_measurements in measurements_by_type.items():
                if len(type_measurements) < 5:
                    continue  # Need sufficient data for anomaly detection

                values = np.array([m.value for m in type_measurements])
                timestamps = [m.timestamp for m in type_measurements]
                locations = np.array([m.location for m in type_measurements])

                # Statistical anomaly detection
                if detection_method == 'statistical':
                    anomaly_indices = self._statistical_anomaly_detection(values)

                elif detection_method == 'isolation_forest':
                    anomaly_indices = self._isolation_forest_anomaly_detection(values)

                elif detection_method == 'zscore':
                    anomaly_indices = self._zscore_anomaly_detection(values)

                else:
                    anomaly_indices = []

                # Create anomaly records
                for idx in anomaly_indices:
                    measurement = type_measurements[idx]
                    anomaly = {
                        'anomaly_id': f"{sensor_type}_{measurement.agent_id}_{measurement.timestamp.isoformat()}",
                        'sensor_type': sensor_type,
                        'agent_id': measurement.agent_id,
                        'value': measurement.value,
                        'location': measurement.location,
                        'timestamp': measurement.timestamp,
                        'severity': self._calculate_anomaly_severity(measurement.value, sensor_type),
                        'detection_method': detection_method
                    }
                    anomalies.append(anomaly)

        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")

        return anomalies

    def _statistical_anomaly_detection(self, values: np.ndarray) -> List[int]:
        """Statistical outlier detection using IQR method."""
        if len(values) < 4:
            return []

        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        anomaly_indices = []
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                anomaly_indices.append(i)

        return anomaly_indices

    def _isolation_forest_anomaly_detection(self, values: np.ndarray) -> List[int]:
        """Isolation forest anomaly detection (simplified)."""
        # In practice, would use sklearn's IsolationForest
        # For now, use statistical method as fallback
        return self._statistical_anomaly_detection(values)

    def _zscore_anomaly_detection(self, values: np.ndarray) -> List[int]:
        """Z-score based anomaly detection."""
        if len(values) < 3:
            return []

        mean_val = np.mean(values)
        std_val = np.std(values)

        if std_val == 0:
            return []

        anomaly_indices = []
        for i, value in enumerate(values):
            zscore = abs((value - mean_val) / std_val)
            if zscore > 3.0:  # 3-sigma threshold
                anomaly_indices.append(i)

        return anomaly_indices

    def _calculate_anomaly_severity(self, value: float, sensor_type: str) -> str:
        """Calculate severity level of anomaly."""
        # Define severity thresholds by sensor type
        severity_thresholds = {
            'pm25_sensor': {'low': 25, 'medium': 50, 'high': 100},
            'no2_sensor': {'low': 0.05, 'medium': 0.1, 'high': 0.2},
            'ph_sensor': {'low': 1.0, 'medium': 2.0, 'high': 3.0},
            'temperature': {'low': 5, 'medium': 10, 'high': 15}  # deviation from normal
        }

        thresholds = severity_thresholds.get(sensor_type, {'low': 1, 'medium': 2, 'high': 3})

        if abs(value) > thresholds['high']:
            return 'high'
        elif abs(value) > thresholds['medium']:
            return 'medium'
        elif abs(value) > thresholds['low']:
            return 'low'
        else:
            return 'minimal'

    def _quantify_uncertainty(
        self,
        measurements: List[SensorReading],
        method: str
    ) -> Dict[str, Any]:
        """Quantify uncertainty in measurements."""
        uncertainty = {
            'method': method,
            'overall_uncertainty': 0.0,
            'sensor_uncertainties': {},
            'spatial_uncertainty': 0.0,
            'temporal_uncertainty': 0.0
        }

        if not measurements:
            return uncertainty

        try:
            # Calculate sensor-specific uncertainties
            sensor_uncertainties = defaultdict(list)
            for measurement in measurements:
                sensor_uncertainties[measurement.sensor_type].append(measurement.quality_score)

            for sensor_type, quality_scores in sensor_uncertainties.items():
                uncertainty['sensor_uncertainties'][sensor_type] = {
                    'mean_quality': np.mean(quality_scores),
                    'quality_std': np.std(quality_scores),
                    'uncertainty_score': 1.0 - np.mean(quality_scores)  # Convert quality to uncertainty
                }

            # Calculate spatial uncertainty (gaps in coverage)
            if len(measurements) > 1:
                locations = np.array([m.location for m in measurements])
                spatial_uncertainty = self._calculate_spatial_uncertainty(locations)
                uncertainty['spatial_uncertainty'] = spatial_uncertainty

            # Calculate temporal uncertainty (time gaps)
            if len(measurements) > 1:
                timestamps = [m.timestamp for m in measurements]
                temporal_uncertainty = self._calculate_temporal_uncertainty(timestamps)
                uncertainty['temporal_uncertainty'] = temporal_uncertainty

            # Overall uncertainty (weighted combination)
            weights = {'sensor': 0.5, 'spatial': 0.3, 'temporal': 0.2}
            overall = (
                np.mean(list(uncertainty['sensor_uncertainties'].values())) * weights['sensor'] +
                uncertainty['spatial_uncertainty'] * weights['spatial'] +
                uncertainty['temporal_uncertainty'] * weights['temporal']
            )
            uncertainty['overall_uncertainty'] = overall

        except Exception as e:
            logger.warning(f"Uncertainty quantification failed: {e}")
            uncertainty['error'] = str(e)

        return uncertainty

    def _calculate_spatial_uncertainty(self, locations: np.ndarray) -> float:
        """Calculate spatial uncertainty based on location distribution."""
        if len(locations) < 2:
            return 1.0

        # Calculate average nearest neighbor distance
        distances = []
        for i in range(len(locations)):
            other_locations = np.delete(locations, i, axis=0)
            nearest_distance = np.min([np.linalg.norm(locations[i] - other) for other in other_locations])
            distances.append(nearest_distance)

        avg_distance = np.mean(distances)

        # Uncertainty increases with distance (sparser coverage)
        # Normalize to 0-1 scale (assuming 0.01 degrees ≈ 1km)
        max_expected_distance = 0.01  # Expected distance for good coverage
        uncertainty = min(1.0, avg_distance / max_expected_distance)

        return uncertainty

    def _calculate_temporal_uncertainty(self, timestamps: List[datetime]) -> float:
        """Calculate temporal uncertainty based on time gaps."""
        if len(timestamps) < 2:
            return 1.0

        # Calculate time gaps
        sorted_timestamps = sorted(timestamps)
        time_gaps = []

        for i in range(1, len(sorted_timestamps)):
            gap = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
            time_gaps.append(gap)

        avg_gap = np.mean(time_gaps)

        # Expected gap based on sampling frequency
        expected_gaps = {
            '1_minute': 60,
            '5_minutes': 300,
            '15_minutes': 900,
            '1_hour': 3600
        }

        expected_gap = expected_gaps.get(self._get_sampling_frequency(), 900)
        uncertainty = min(1.0, avg_gap / expected_gap)

        return uncertainty

    def _generate_monitoring_recommendations(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for improving monitoring."""
        recommendations = []

        try:
            # Coverage-based recommendations
            coverage = assessment.get('spatial_analysis', {}).get('coverage', 0.5)
            if coverage < 0.7:
                recommendations.append({
                    'type': 'coverage_improvement',
                    'priority': 'high',
                    'description': f'Increase monitoring coverage from {coverage:.2f} to >0.8',
                    'actions': ['deploy_additional_agents', 'optimize_agent_positions']
                })

            # Anomaly-based recommendations
            anomalies = assessment.get('anomaly_detection', {})
            if anomalies and len(anomalies) > 0:
                high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
                if high_severity_anomalies:
                    recommendations.append({
                        'type': 'anomaly_investigation',
                        'priority': 'urgent',
                        'description': f'Investigate {len(high_severity_anomalies)} high-severity anomalies',
                        'actions': ['increase_sampling_frequency', 'deploy_specialized_sensors']
                    })

            # Uncertainty-based recommendations
            uncertainty = assessment.get('uncertainty_analysis', {}).get('overall_uncertainty', 0.5)
            if uncertainty > 0.6:
                recommendations.append({
                    'type': 'uncertainty_reduction',
                    'priority': 'medium',
                    'description': f'Reduce measurement uncertainty from {uncertainty:.2f} to <0.4',
                    'actions': ['calibrate_sensors', 'increase_redundancy', 'improve_spatial_coverage']
                })

        except Exception as e:
            logger.warning(f"Recommendation generation failed: {e}")

        return recommendations

    def _update_performance_metrics(
        self,
        measurements: List[SensorReading],
        assessment: Dict[str, Any]
    ) -> None:
        """Update system performance metrics."""
        if not measurements:
            return

        # Calculate monitoring efficiency
        expected_measurements = len(self.monitoring_agents) * 10  # Expected per hour
        actual_measurements = len(measurements)
        self.monitoring_efficiency = min(1.0, actual_measurements / expected_measurements)

        # Calculate coverage quality
        spatial_analysis = assessment.get('spatial_analysis', {})
        self.coverage_quality = spatial_analysis.get('coverage', 0.5)

        # Calculate anomaly detection rate
        anomalies = assessment.get('anomaly_detection', [])
        self.anomaly_detection_rate = len(anomalies) / max(1, len(measurements)) * 1000  # Per 1000 measurements

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring system status."""
        status = {
            'system_status': 'operational',
            'monitoring_objectives': self.monitoring_objectives,
            'spatial_coverage': self.spatial_coverage,
            'temporal_coverage': self.temporal_coverage,
            'adaptive_sampling': self.adaptive_sampling,
            'performance_metrics': {
                'monitoring_efficiency': self.monitoring_efficiency,
                'coverage_quality': self.coverage_quality,
                'anomaly_detection_rate': self.anomaly_detection_rate
            },
            'component_status': {
                'pheromone_system': self.pheromone_system is not None,
                'digital_stigmergy': self.digital_stigmergy is not None,
                'spatial_analytics': self.spatial_analytics is not None,
                'sampling_optimizer': self.sampling_optimizer is not None,
                'coverage_optimizer': self.coverage_optimizer is not None
            },
            'data_summary': {
                'total_sensor_readings': len(self.sensor_data),
                'total_anomalies': len(self.anomaly_history),
                'active_alerts': len(self.alerts)
            }
        }

        return status
