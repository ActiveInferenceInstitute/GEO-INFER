"""
Microeconomics Module for GEO-INFER-ECON

This module provides comprehensive microeconomic modeling capabilities including:
- Consumer theory and demand analysis
- Producer theory and supply analysis  
- Market structure analysis
- Game theory applications
- Behavioral economics integration
- Spatial microeconomic modeling
"""
# Consumer, producer, market-structure, game-theory and behavioral classes
from .consumer_theory import (
    ConsumerProfile,
    UtilityFunctions,
    DemandFunctions,
    ConsumerChoiceModels,
    WelfareAnalysis,
    ConsumerSurplus
)

# Import implemented classes
from .producer_theory import ProducerTheoryModels
from .market_structure import MarketStructureAnalysis
from .game_theory import GameTheoryModels
from .behavioral_economics import BehavioralEconomicsEngine

__all__ = [
    # Available consumer theory classes
    'ConsumerProfile',
    'UtilityFunctions',
    'DemandFunctions', 
    'ConsumerChoiceModels',
    'WelfareAnalysis',
    'ConsumerSurplus',
    
    # Main modeling classes
    'ProducerTheoryModels',
    'MarketStructureAnalysis',
    'GameTheoryModels',
    'BehavioralEconomicsEngine'
] 