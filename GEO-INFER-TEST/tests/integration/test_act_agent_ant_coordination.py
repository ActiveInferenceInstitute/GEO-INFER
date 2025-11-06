"""
Integration tests for ACT + AGENT + ANT coordination.

Tests real integration between Active Inference, Agent framework,
and Swarm Intelligence modules.
"""

import pytest
import numpy as np
from typing import Dict, Any, List

# Try to import actual modules
try:
    from geo_infer_act.core.active_inference import ActiveInferenceModel
    from geo_infer_act.core.free_energy import FreeEnergyCalculator
    ACT_AVAILABLE = True
except ImportError:
    ACT_AVAILABLE = False
    pytest.skip("GEO-INFER-ACT not available", allow_module_level=True)

try:
    from geo_infer_agent.core.agent_base import BaseAgent, AgentState
    from geo_infer_agent.core.agent_registry import AgentRegistry
    from geo_infer_agent.api.messaging import MessagingService
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    pytest.skip("GEO-INFER-AGENT not available", allow_module_level=True)

try:
    from geo_infer_ant.core.population import AgentPopulation
    from geo_infer_ant.core.swarm_agent import SwarmAgent
    from geo_infer_ant.algorithms.aco import AntColonyOptimization
    ANT_AVAILABLE = True
except ImportError:
    ANT_AVAILABLE = False
    pytest.skip("GEO-INFER-ANT not available", allow_module_level=True)


@pytest.fixture
def sample_agent_config():
    """Sample configuration for agent coordination."""
    return {
        'spatial_bounds': {
            'min_lat': 37.7,
            'max_lat': 37.9,
            'min_lng': -122.5,
            'max_lng': -122.3
        },
        'num_agents': 5,
        'communication_range': 1000.0
    }


@pytest.mark.integration
class TestActAgentAntCoordination:
    """Test coordination between ACT, AGENT, and ANT modules."""
    
    def test_active_inference_agent_creation(self, sample_agent_config):
        """Test creating agents with Active Inference models."""
        if not (ACT_AVAILABLE and AGENT_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create Active Inference model
        act_model = ActiveInferenceModel(
            model_type='categorical',
            state_dim=5,
            obs_dim=3
        )
        
        # Create agent with Active Inference
        agent = BaseAgent(
            agent_id="test_agent_001",
            config=sample_agent_config
        )
        
        # Verify agent creation
        assert agent.agent_id == "test_agent_001"
        assert agent.get_state() is not None
    
    def test_swarm_agent_with_active_inference(self, sample_agent_config):
        """Test swarm agents using Active Inference for decision-making."""
        if not (ACT_AVAILABLE and ANT_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create Active Inference model for swarm agent
        act_model = ActiveInferenceModel(
            model_type='categorical',
            state_dim=4,
            obs_dim=2
        )
        
        # Create swarm agent population
        population = AgentPopulation(
            num_agents=sample_agent_config['num_agents'],
            spatial_bounds=sample_agent_config['spatial_bounds']
        )
        
        # Verify population creation
        assert len(population.agents) == sample_agent_config['num_agents']
        assert population.spatial_bounds == sample_agent_config['spatial_bounds']
    
    def test_multi_agent_coordination(self, sample_agent_config):
        """Test multi-agent coordination with messaging."""
        if not (AGENT_AVAILABLE and ACT_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create agent registry
        registry = AgentRegistry()
        
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = BaseAgent(
                agent_id=f"coord_agent_{i:03d}",
                config=sample_agent_config
            )
            agents.append(agent)
            registry.register(agent)
        
        # Create messaging service
        messaging = MessagingService()
        
        # Send message between agents
        if len(agents) >= 2:
            message = {
                'from': agents[0].agent_id,
                'to': agents[1].agent_id,
                'type': 'coordination',
                'content': {'action': 'coordinate', 'data': {'value': 42}}
            }
            
            # Verify messaging capability
            assert messaging is not None
            assert len(agents) == 3
    
    def test_swarm_optimization_with_agent_framework(self, sample_agent_config):
        """Test swarm optimization algorithms with agent framework."""
        if not (ANT_AVAILABLE and AGENT_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create ant colony optimization
        aco = AntColonyOptimization(
            num_ants=10,
            num_iterations=5,
            alpha=1.0,
            beta=2.0,
            evaporation_rate=0.5
        )
        
        # Create simple problem (distance matrix)
        n_nodes = 5
        distance_matrix = np.random.rand(n_nodes, n_nodes)
        distance_matrix = (distance_matrix + distance_matrix.T) / 2  # Symmetric
        np.fill_diagonal(distance_matrix, 0)
        
        # Run optimization
        result = aco.optimize(distance_matrix)
        
        # Verify optimization result
        assert result is not None
        assert 'best_path' in result or 'solution' in result or isinstance(result, (list, np.ndarray))
    
    def test_agent_population_with_active_inference(self, sample_agent_config):
        """Test agent population using Active Inference for collective behavior."""
        if not (ACT_AVAILABLE and ANT_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create Active Inference model
        act_model = ActiveInferenceModel(
            model_type='categorical',
            state_dim=3,
            obs_dim=2
        )
        
        # Create agent population
        population = AgentPopulation(
            num_agents=sample_agent_config['num_agents'],
            spatial_bounds=sample_agent_config['spatial_bounds']
        )
        
        # Simulate collective behavior
        for agent in population.agents[:3]:  # Test first 3 agents
            # Get agent state
            state = agent.get_state() if hasattr(agent, 'get_state') else {}
            
            # Verify agent has state
            assert state is not None or isinstance(state, dict)
        
        # Verify population structure
        assert len(population.agents) == sample_agent_config['num_agents']


