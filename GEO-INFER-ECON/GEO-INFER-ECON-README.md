# GEO-INFER-ECON

## Overview
GEO-INFER-ECON provides powerful economic modeling and analysis capabilities within the GEO-INFER framework. This module integrates spatial dimensions with economic principles, enabling sophisticated analysis of economic activities, resource allocation, and policy impacts across geographic regions. It bridges traditional economic modeling with geospatial analytics for more nuanced and context-aware economic insights.

## Key Features
- Spatial economic modeling and analysis
- Market simulation with geographic constraints
- Resource allocation optimization across regions
- Policy impact assessment with spatial dimensions
- Economic risk assessment incorporating geographic factors

## Directory Structure
```
GEO-INFER-ECON/
├── config/               # Configuration files
├── docs/                 # Documentation
├── examples/             # Example use cases
├── src/                  # Source code
│   └── geo_infer_econ/   # Main package
│       ├── api/          # API definitions
│       ├── core/         # Core functionality
│       ├── models/       # Economic models
│       └── utils/        # Utility functions
└── tests/                # Test suite
```

## Getting Started
1. Installation
   ```bash
   pip install -e .
   ```

2. Configuration
   ```bash
   cp config/example.yaml config/local.yaml
   # Edit local.yaml with your configuration
   ```

3. Running a Spatial Economic Analysis
   ```python
   from geo_infer_econ.models import SpatialEquilibrium
   from geo_infer_econ.core import EconomicAnalysis
   
   # Define economic data and model
   model = SpatialEquilibrium(regions=regions_gdf)
   
   # Perform economic analysis
   analysis = EconomicAnalysis(model=model)
   results = analysis.run(market_data=economic_data)
   
   # Visualize economic indicators
   results.plot_spatial_distribution('price_index')
   ```

## Economic Modeling Capabilities
The module provides specialized economic modeling tools:
- Spatial equilibrium models
- Input-output analysis with spatial dimensions
- Computable general equilibrium models
- Agent-based economic models
- Location-allocation models
- Spatial hedonic pricing models

## Analytical Methods
Supported economic analytical approaches:
- Spatial econometrics
- Geographically weighted regression
- Spatial panel data analysis
- Network analysis for trade flows
- Accessibility and transportation modeling
- Spatial interaction models

## Policy Analysis
Tools for policy evaluation and decision support:
- Tax and subsidy impact assessment
- Infrastructure investment analysis
- Land use regulation evaluation
- Resource management optimization
- Environmental policy analysis
- Regional development strategy evaluation

## Integration with Other Modules
GEO-INFER-ECON integrates with:
- GEO-INFER-SPACE for spatial data representation
- GEO-INFER-TIME for temporal economic modeling
- GEO-INFER-BAYES for Bayesian economic inference
- GEO-INFER-SIM for economic scenario simulation
- GEO-INFER-NORMS for regulatory compliance modeling
- GEO-INFER-AG for agricultural economics integration

## Application Domains
- Urban economics and land use
- Transportation economics
- Environmental economics
- Resource economics
- Regional development
- Trade and location theory
- Labor market analysis
- Public finance

## Data Sources
The module can integrate with various economic data sources:
- National economic accounts
- Regional economic data
- Trade flow statistics
- Labor market statistics
- Consumer expenditure data
- Business establishment data
- Infrastructure and accessibility metrics

## Contributing
Follow the contribution guidelines in the main GEO-INFER documentation. 