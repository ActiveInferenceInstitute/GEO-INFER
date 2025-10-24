"""
Unit Tests for GEO-INFER-ANT

This package contains comprehensive unit tests for all components of the
GEO-INFER-ANT swarm intelligence framework.

Test Structure:
- test_core.py: Tests for core components (agents, population, stigmergy)
- test_algorithms.py: Tests for optimization algorithms (ACO, PSO, ABC)
- test_applications.py: Tests for domain applications (environmental monitoring)
- test_analysis.py: Tests for pattern analysis and metrics
- test_metrics.py: Tests for performance evaluation framework

Usage:
    python -m pytest tests/unit/ -v
    python -m pytest tests/unit/test_core.py -v
    python -m pytest tests/unit/test_algorithms.py -v
"""

import pytest

# Export test classes for easy access
from .test_core import TestSwarmAgent, TestAgentPopulation, TestPheromoneSystem, TestDigitalStigmergy
from .test_algorithms import TestAntColonyOptimization, TestParticleSwarmOptimization, TestArtificialBeeColony
from .test_applications import TestEnvironmentalMonitoringSwarm
from .test_analysis import TestSwarmPatternAnalyzer
from .test_metrics import TestPerformanceMetrics, TestRobustnessAnalysis, TestScalabilityAssessment

__all__ = [
    # Core tests
    'TestSwarmAgent',
    'TestAgentPopulation',
    'TestPheromoneSystem',
    'TestDigitalStigmergy',

    # Algorithm tests
    'TestAntColonyOptimization',
    'TestParticleSwarmOptimization',
    'TestArtificialBeeColony',

    # Application tests
    'TestEnvironmentalMonitoringSwarm',

    # Analysis tests
    'TestSwarmPatternAnalyzer',

    # Metrics tests
    'TestPerformanceMetrics',
    'TestRobustnessAnalysis',
    'TestScalabilityAssessment'
]
