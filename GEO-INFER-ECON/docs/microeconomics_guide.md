# Microeconomics Module Guide

## Overview

The microeconomics module in GEO-INFER-ECON provides comprehensive tools for analyzing individual economic decision-making, market behavior, and spatial microeconomic phenomena. It combines traditional microeconomic theory with spatial analysis and modern behavioral insights.

## Core Components

### 1. Consumer Theory
- **Utility Functions**: Cobb-Douglas, CES, Linear, Leontief, and Spatial utility
- **Demand Analysis**: Marshallian and Hicksian demand functions
- **Consumer Choice Models**: Optimization with spatial market selection
- **Welfare Analysis**: Consumer surplus, equivalent/compensating variation
- **Spatial Consumer Behavior**: Location-dependent preferences and market access

### 2. Producer Theory  
- **Production Functions**: Various forms with spatial productivity factors
- **Cost Functions**: Cost minimization with spatial input costs
- **Technical Efficiency**: Spatial DEA and efficiency analysis
- **Supply Analysis**: Producer surplus and spatial supply chains

### 3. Market Structure Analysis
- **Perfect Competition**: Spatial price equilibrium
- **Monopoly Models**: Spatial monopoly and price discrimination
- **Oligopoly**: Spatial competition and strategic interaction
- **Monopolistic Competition**: Product differentiation with location
- **Market Power**: Spatial market definition and power measurement

### 4. Game Theory Applications
- **Strategic Games**: Location games, price competition
- **Extensive Games**: Sequential spatial decisions
- **Evolutionary Games**: Spatial strategy evolution
- **Auction Theory**: Land auctions, spectrum auctions
- **Mechanism Design**: Spatial mechanism design problems

### 5. Behavioral Economics Integration
- **Bounded Rationality**: Spatial search and limited information
- **Prospect Theory**: Reference points and spatial context
- **Social Preferences**: Community effects and spatial spillovers
- **Nudge Analysis**: Location-based behavioral interventions

## Usage Examples

### Consumer Choice Analysis

```python
from geo_infer_econ.microeconomics import ConsumerChoiceModels, ConsumerProfile

# Create consumer profile
consumer = ConsumerProfile(
    consumer_id="consumer_001",
    income=1000.0,
    location=(40.7128, -74.0060),  # NYC coordinates
    preferences={"good_1": 0.6, "good_2": 0.4},
    demographic_attributes={"age": 35, "education": "college"},
    spatial_attributes={"accessibility_index": 0.8}
)

# Initialize choice model
choice_model = ConsumerChoiceModels()

# Solve utility maximization
prices = [2.0, 3.0]
goods = ["good_1", "good_2"]
result = choice_model.solve_utility_maximization(consumer, prices, goods)

print(f"Optimal quantities: {result['quantities']}")
print(f"Maximum utility: {result['utility']:.2f}")
```

### Spatial Market Analysis

```python
import geopandas as gpd
from geo_infer_econ.microeconomics import ConsumerChoiceModels

# Create spatial markets
markets = gpd.GeoDataFrame({
    'market_id': ['A', 'B', 'C'],
    'price_good_1': [2.0, 2.2, 1.8],
    'price_good_2': [3.0, 2.8, 3.2],
    'geometry': [Point(-74.0, 40.7), Point(-74.1, 40.8), Point(-73.9, 40.6)]
})

# Transport costs
transport_costs = {'per_km': 0.1}

# Find optimal market choice
choice_result = choice_model.spatial_consumer_choice(
    consumer, markets, transport_costs
)
```

### Demand System Estimation

```python
from geo_infer_econ.microeconomics import DemandFunctions
import pandas as pd

# Sample consumer data
data = pd.DataFrame({
    'quantity_good_1': [10, 12, 8, 15],
    'quantity_good_2': [5, 6, 4, 7],
    'price_good_1': [2.0, 2.2, 1.8, 2.1],
    'price_good_2': [3.0, 2.8, 3.2, 2.9],
    'income': [1000, 1200, 800, 1500]
})

demand_model = DemandFunctions()
results = demand_model.estimate_demand_system(data, method='aids')
```

## Advanced Features

### Spatial Consumer Models
- Location choice with housing and job markets
- Transport costs and accessibility analysis
- Agglomeration effects on consumer behavior
- Multi-market shopping behavior

### Behavioral Extensions
- Reference-dependent preferences with spatial anchoring
- Social learning in spatial networks
- Habit formation and spatial persistence
- Mental accounting with location-specific budgets

### Market Power Analysis
- Spatial market definition using price correlation
- Geographic market concentration measures
- Spatial price discrimination analysis
- Network effects and platform competition

## Integration with Other Modules

The microeconomics module integrates seamlessly with:

- **GEO-INFER-SPACE**: Spatial analysis and network effects
- **GEO-INFER-DATA**: Consumer and market data sources
- **GEO-INFER-TIME**: Dynamic consumer behavior analysis
- **GEO-INFER-AI**: Machine learning for demand prediction
- **GEO-INFER-BAYES**: Bayesian estimation of consumer preferences

## Configuration

Microeconomic models are configured through the `microeconomic` section in the configuration file:

```yaml
microeconomic:
  consumer_theory:
    utility_function: spatial  # incorporates location preferences
    demand_estimation: aids    # Almost Ideal Demand System
    welfare_analysis: true
  producer_theory:
    production_function: spatial  # location-dependent productivity
    technical_efficiency: true
  behavioral_economics:
    bounded_rationality: true
    prospect_theory: true
    social_preferences: true
```

## Research Applications

- Urban economics and residential location choice
- Retail location and market area analysis  
- Consumer travel behavior and shopping patterns
- Digital platform competition and network effects
- Environmental goods valuation
- Health economics and spatial access to care
- Labor market search and spatial mismatch
- Housing market dynamics and gentrification 