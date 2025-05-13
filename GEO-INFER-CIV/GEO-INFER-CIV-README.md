# GEO-INFER-CIV

## Overview
GEO-INFER-CIV provides community engagement and participatory mapping tools within the GEO-INFER framework. This module enables civic participation in geospatial data collection, analysis, and decision-making, fostering collaborative approaches to ecological and urban challenges.

## Key Features
- Tools like STEW-MAP to visualize stewardship networks
- Platforms enabling community-driven spatial planning initiatives
- Participatory mapping and citizen science capabilities
- Collaborative decision support systems

## Directory Structure
```
GEO-INFER-CIV/
├── docs/                # Documentation
├── examples/            # Example use cases
├── src/                 # Source code
│   └── geo_infer_civ/   # Main package
│       ├── api/         # API definitions
│       ├── core/        # Core functionality
│       ├── models/      # Data models
│       └── utils/       # Utility functions
└── tests/               # Test suite
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

3. Running the Platform
   ```bash
   python -m geo_infer_civ.app
   ```

## Engagement Tools
GEO-INFER-CIV offers a diverse set of community engagement tools:
- Participatory mapping interfaces
- Citizen science data collection apps
- Stakeholder identification and analysis
- Community asset mapping
- Collaborative scenario planning
- Consensus building frameworks

## STEW-MAP Implementation
The module includes a full implementation of the Stewardship Mapping and Assessment Project (STEW-MAP):
- Stewardship group mapping
- Network analysis of relationships
- Spatial coverage analysis
- Gap identification
- Resource sharing facilitation
- Impact assessment

## Data Collection Methods
Multiple methods for community data collection:
- Mobile applications for field data
- Web-based mapping interfaces
- Survey tools with spatial components
- Crowdsourcing and volunteered geographic information
- Integration with social media spatial data
- Sensor networks and IoT devices

## Decision Support
Tools for collaborative decision-making:
- Multi-criteria decision analysis
- Spatial consensus building
- Conflict resolution frameworks
- Equity and justice considerations
- Collaborative goal setting
- Impact monitoring and evaluation

## Integration with Other Modules
GEO-INFER-CIV integrates with:
- GEO-INFER-APP for user interfaces
- GEO-INFER-DATA for data management
- GEO-INFER-SPACE for spatial analysis
- GEO-INFER-NORMS for policy and regulation context

## Contributing
Follow the contribution guidelines in the main GEO-INFER documentation. 