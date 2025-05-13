# GEO-INFER-ACT

## Overview
GEO-INFER-ACT is the analytical and formal Active Inference modeling module for nested and interacting systems within the GEO-INFER framework. This module provides advanced mathematical and computational tools for modeling complex ecological and civic systems using principles from active inference theory.

## Key Features
- Generative models for spatial-temporal dynamics
- Free-energy minimization frameworks for adaptive decision-making
- Probabilistic programming tools for uncertainty quantification
- Multi-scale active inference model integration

## Directory Structure
```
GEO-INFER-ACT/
├── docs/               # Documentation
├── examples/           # Example use cases
├── src/                # Source code
│   └── geo_infer_act/  # Main package
│       ├── api/        # API definitions
│       ├── core/       # Core functionality
│       ├── models/     # Data models
│       └── utils/      # Utility functions
└── tests/              # Test suite
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

3. Running Tests
   ```bash
   pytest tests/
   ```

## Active Inference Modeling
The module implements several key active inference concepts:
- Prior beliefs and preference specification
- Bayesian belief updating
- Free energy minimization
- Expected free energy computation
- Active inference policy selection

## Mathematical Framework
GEO-INFER-ACT provides tools for working with:
- Bayesian hierarchical models
- Markov decision processes
- Variational inference methods
- Dynamic causal modeling
- Predictive coding networks

## Integration with Other Modules
GEO-INFER-ACT integrates with:
- GEO-INFER-SPACE for spatial components
- GEO-INFER-TIME for temporal dynamics
- GEO-INFER-SIM for simulation-based inference
- GEO-INFER-ANT for specialized complex systems models

## Use Cases
- Ecological niche modeling with active inference
- Urban planning with multi-agent active inference
- Climate adaptation policy optimization
- Resource allocation under uncertainty

## Contributing
Follow the contribution guidelines in the main GEO-INFER documentation. 