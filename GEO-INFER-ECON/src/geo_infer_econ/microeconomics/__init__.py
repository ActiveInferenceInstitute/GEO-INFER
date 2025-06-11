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

# Import available modules - only consumer_theory exists currently
from .consumer_theory import (
    ConsumerProfile,
    UtilityFunctions,
    DemandFunctions,
    ConsumerChoiceModels,
    WelfareAnalysis,
    ConsumerSurplus
)

# Placeholder classes for modules not yet implemented
class ConsumerTheoryModels:
    """Main consumer theory modeling class."""
    pass

class ProducerTheoryModels:
    """Main producer theory modeling class.""" 
    pass

class MarketStructureAnalysis:
    """Main market structure analysis class."""
    pass

class GameTheoryModels:
    """Main game theory modeling class."""
    pass

class BehavioralEconomicsEngine:
    """Main behavioral economics engine class."""
    pass

__all__ = [
    # Available consumer theory classes
    'ConsumerProfile',
    'UtilityFunctions',
    'DemandFunctions', 
    'ConsumerChoiceModels',
    'WelfareAnalysis',
    'ConsumerSurplus',
    
    # Main modeling classes
    'ConsumerTheoryModels',
    'ProducerTheoryModels',
    'MarketStructureAnalysis',
    'GameTheoryModels',
    'BehavioralEconomicsEngine'
] 