# GEO-INFER-NORMS

## Overview
GEO-INFER-NORMS provides social-technical compliance modeling with deterministic and probabilistic aspects within the GEO-INFER framework. This module focuses on understanding, modeling, and analyzing social norms, regulatory frameworks, and compliance requirements in spatial contexts.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-norms.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Key Features
- **Legal Framework Analysis**: Model jurisdictions, legal entities, and regulations with their spatial dimensions
- **Zoning Analysis**: Evaluate land use regulations, zoning compatibility, and zoning change impacts
- **Compliance Tracking**: Monitor and report regulatory compliance across entities and jurisdictions
- **Policy Impact Assessment**: Analyze the effects of policy implementation in spatial contexts
- **Normative Inference**: Apply probabilistic reasoning to social norms and compliance expectations

## Directory Structure
```
GEO-INFER-NORMS/
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── examples/          # Example documentation
│   └── norms_and_laws.md  # Comprehensive guide to norms and laws
├── examples/              # Example use cases
│   ├── zoning_analysis_example.py  # Zoning analysis example
│   ├── legal_framework_example.py  # Legal framework example
│   └── compliance_tracking_example.py  # Compliance tracking example
├── src/                   # Source code
│   └── geo_infer_norms/   # Main package
│       ├── api/           # API definitions
│       ├── core/          # Core functionality
│       │   ├── legal_frameworks.py    # Legal framework analysis
│       │   ├── zoning_analysis.py     # Zoning and land use analysis
│       │   ├── compliance_tracking.py # Compliance tracking and reporting
│       │   ├── policy_impact.py       # Policy impact assessment
│       │   └── normative_inference.py # Normative inference engine
│       ├── models/        # Data models
│       │   ├── legal_entity.py        # Legal entities and jurisdictions
│       │   ├── regulation.py          # Regulations and frameworks
│       │   ├── compliance_status.py   # Compliance status and metrics
│       │   ├── zoning.py              # Zoning codes and districts
│       │   └── policy.py              # Policies and implementations
│       └── utils/         # Utility functions
└── tests/                 # Test suite
    ├── test_legal_frameworks.py   # Legal framework tests
    ├── test_zoning_analysis.py    # Zoning analysis tests
    ├── test_compliance_tracking.py # Compliance tracking tests
    └── test_policy_impact.py       # Policy impact tests
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

3. Running Examples
   ```bash
   python examples/zoning_analysis_example.py
   python examples/legal_framework_example.py
   python examples/compliance_tracking_example.py
   ```

## Core Components

### Legal Frameworks

The module provides comprehensive tools for modeling legal frameworks and jurisdictions:

```python
from geo_infer_norms.core.legal_frameworks import LegalFramework, JurisdictionHandler
from geo_infer_norms.models.legal_entity import Jurisdiction
from geo_infer_norms.models.regulation import Regulation
from shapely.geometry import Point

# Create jurisdictions with geometries
city = Jurisdiction.create(
    name="Sample City",
    level="city",
    geometry=city_geometry
)

# Create regulations
zoning_regulation = Regulation.create(
    name="City Zoning Ordinance",
    description="Regulates land use within the city",
    regulation_type="zoning",
    issuing_authority="City Planning Department",
    effective_date=effective_date,
    applicable_jurisdictions=[city.id]
)

# Create and use a legal framework
framework = LegalFramework(
    name="City Regulatory Framework",
    jurisdictions=[city],
    regulations=[zoning_regulation]
)

# Find regulations applicable to a location
point = Point(longitude, latitude)
applicable_regulations = framework.get_regulations_by_point(point)
```

### Zoning Analysis

Tools for analyzing zoning regulations and land use patterns:

```python
from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer, LandUseClassifier
from geo_infer_norms.models.zoning import ZoningCode, ZoningDistrict

# Create zoning codes and districts
residential_code = ZoningCode.create(
    code="R-1",
    name="Single Family Residential",
    description="Low-density residential area",
    category="residential",
    jurisdiction_id=city.id
)

residential_district = ZoningDistrict.create(
    name="North Residential",
    zoning_code=residential_code.code,
    jurisdiction_id=city.id,
    geometry=district_geometry
)

# Analyze zoning compatibility and boundaries
analyzer = ZoningAnalyzer(
    zoning_districts=[residential_district, commercial_district],
    zoning_codes=[residential_code, commercial_code]
)

# Evaluate a zoning change
impact = analyzer.evaluate_zoning_change(
    district_id=residential_district.id,
    new_code=commercial_code.code
)

# Visualize zoning
fig = analyzer.visualize_zoning()
```

### Compliance Tracking

Monitor and report on regulatory compliance:

```python
from geo_infer_norms.core.compliance_tracking import ComplianceTracker, ComplianceReport
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric

# Create compliance metrics
air_quality_metric = ComplianceMetric.create(
    name="Air Quality Standard",
    description="Measures compliance with air quality regulations",
    regulation_id=environmental_regulation.id,
    evaluation_type="threshold",
    primary_field="pollutant_level",
    threshold_value=2.5,
    comparison="less_than"
)

# Track compliance
tracker = ComplianceTracker(
    name="Environmental Compliance Tracker",
    compliance_metrics=[air_quality_metric]
)

# Evaluate compliance for an entity
status = tracker.evaluate_compliance(
    entity=facility,
    regulation=environmental_regulation,
    evaluation_data={"pollutant_level": 1.8}
)

# Generate compliance reports
report = ComplianceReport(tracker)
summary = report.generate_summary_report()
entity_report = report.generate_entity_report(facility.id)
```

## Normative Frameworks
GEO-INFER-NORMS implements several normative frameworks:
- Environmental, Social, and Governance (ESG) standards
- Regulatory compliance models
- Social norm diffusion patterns
- Policy impact assessment frameworks
- Spatial equity and justice metrics

## Modeling Capabilities
The module provides tools for modeling:
- Regulatory compliance in spatial contexts
- Social norm emergence and diffusion
- Policy implementation effectiveness
- Spatial distribution of compliance/non-compliance
- Scenario analysis for policy interventions

## Analysis Methods
Key analysis methods include:
- Spatial compliance mapping
- Probabilistic norm modeling
- Regulatory impact assessment
- Socio-ecological system analysis
- Agent-based normative behavior simulation

## Integration with Other Modules

GEO-INFER-NORMS interfaces seamlessly with several other modules in the GEO-INFER ecosystem:

- **GEO-INFER-SPACE**: NORMS utilizes SPACE for spatial representation of jurisdictions, zoning boundaries, and compliance visualization across geographic areas.
- **GEO-INFER-TIME**: Leverages TIME for tracking regulatory changes over time, analyzing compliance history, and modeling normative evolution.
- **GEO-INFER-ACT**: Provides normative frameworks that can guide active inference processes, particularly for normative decision-making models.
- **GEO-INFER-SIM**: Supplies regulatory constraints and compliance models for policy scenario simulations.
- **GEO-INFER-APP**: Enables visualization and interactive exploration of normative frameworks, compliance status, and regulatory impacts.
- **GEO-INFER-DATA**: Relies on DATA for storage and retrieval of regulatory databases, compliance records, and jurisdiction information.
- **GEO-INFER-SEC**: Collaborates on security compliance aspects and regulatory requirements for data privacy.
- **GEO-INFER-REQ**: Works closely with REQ to formalize normative requirements into technical specifications.
- **GEO-INFER-ORG**: Provides normative frameworks that inform organizational governance structures and policies.

## Applications
- Urban planning policy assessment
- Environmental regulation compliance monitoring
- Social impact analysis of spatial policies
- Equity and justice evaluation in resource distribution
- Scenario planning for regulatory changes
- Legal tech development and automation
- Zoning analysis and land use planning
- Jurisdictional boundary analysis

## Documentation

For comprehensive documentation on using GEO-INFER-NORMS for legal tech, zoning analysis, and compliance tracking, see:

- [Norms and Laws Guide](docs/norms_and_laws.md): Comprehensive documentation on all components
- [API Documentation](docs/api/): Detailed API reference
- [Example Documentation](docs/examples/): Explanation of example use cases

## Future Development

- Advanced machine learning for regulatory compliance prediction
- Blockchain integration for immutable compliance records
- Enhanced visualization of normative frameworks
- Expanded jurisdictional boundary analysis tools
- Integration with external regulatory databases and APIs
- Natural language processing for automated regulatory text analysis
- Improved cross-jurisdictional compliance modeling

## Contributing

Contributions to GEO-INFER-NORMS are welcome! We especially value expertise in legal frameworks, compliance management, policy analysis, and normative modeling.

Please refer to the main `CONTRIBUTING.md` in the GEO-INFER root directory for contribution guidelines.

## License

This module, as part of the GEO-INFER framework, is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 