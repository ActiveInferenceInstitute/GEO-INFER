"""
Belief-Desire-Intention (BDI) Agent Models

This module implements the BDI cognitive architecture for intelligent agents.
BDI agents are modeled after human practical reasoning, using:
- Beliefs: the agent's information about the world
- Desires: the agent's goals or objectives
- Intentions: the agent's committed plans to achieve goals

The BDI model is particularly useful for geospatial agents that need to:
- Maintain a representation of their environment
- Have multiple goals and priorities
- Deliberate and adjust plans based on changing conditions
"""

from geo_infer_agent.models.bdi.belief import Belief, BeliefBase
from geo_infer_agent.models.bdi.desire import Desire, DesireSet
from geo_infer_agent.models.bdi.intention import Intention, IntentionStructure
from geo_infer_agent.models.bdi.plan import Plan, PlanLibrary
from geo_infer_agent.models.bdi.state import BDIState
from geo_infer_agent.models.bdi.agent import BDIAgent

__all__ = [
    "Belief", 
    "BeliefBase",
    "Desire", 
    "DesireSet",
    "Intention", 
    "IntentionStructure",
    "Plan", 
    "PlanLibrary",
    "BDIState",
    "BDIAgent"
] 