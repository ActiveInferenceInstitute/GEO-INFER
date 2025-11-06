"""
GEO-INFER-AGENT Models

This package provides different agent architecture and modeling approaches:
- Belief-Desire-Intention (BDI) agents
- Active Inference based agents
- Reinforcement Learning agents
- Rule-based agents
- Hybrid agent architectures

Each module implements a specific agent architecture that can be used
as a foundation for specialized geospatial agents.
"""

# Import BDI classes - BDIState and BDIAgent are in bdi.py file, not bdi/ subdirectory
# Since there's both bdi.py and bdi/ directory, we need to import from the file directly
import importlib.util
import os
bdi_file_path = os.path.join(os.path.dirname(__file__), 'bdi.py')
spec = importlib.util.spec_from_file_location("geo_infer_agent.models.bdi_file", bdi_file_path)
bdi_file_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bdi_file_module)
BDIAgent = bdi_file_module.BDIAgent
BDIState = bdi_file_module.BDIState
# Import other BDI components from bdi/ subdirectory
from geo_infer_agent.models.bdi import Belief, Desire, Plan
from geo_infer_agent.models.active_inference import ActiveInferenceAgent, ActiveInferenceState, GenerativeModel
from geo_infer_agent.models.rl import RLAgent, RLState, QTable, ReplayBuffer, Experience
from geo_infer_agent.models.rule_based import RuleBasedAgent, RuleBasedState, Rule, RuleSet
from geo_infer_agent.models.hybrid import HybridAgent, HybridState, SubAgentWrapper

__all__ = [
    # Module names
    "bdi", "active_inference", "rl", "rule_based", "hybrid",
    
    # BDI agent classes
    "BDIAgent", "BDIState", "Belief", "Desire", "Plan",
    
    # Active inference agent classes
    "ActiveInferenceAgent", "ActiveInferenceState", "GenerativeModel",
    
    # RL agent classes
    "RLAgent", "RLState", "QTable", "ReplayBuffer", "Experience",
    
    # Rule-based agent classes
    "RuleBasedAgent", "RuleBasedState", "Rule", "RuleSet",
    
    # Hybrid agent classes
    "HybridAgent", "HybridState", "SubAgentWrapper"
] 