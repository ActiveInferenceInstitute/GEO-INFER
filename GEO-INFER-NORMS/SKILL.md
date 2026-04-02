---
name: geo-infer-norms
description: "Normative inference and compliance tracking for geospatial governance. Use when checking if a land parcel complies with zoning regulations, evaluating spatial policy compliance against threshold/range/boolean criteria, comparing policy documents for normative overlap (Jaccard similarity), assessing economic and environmental impact of zoning changes, or tracking multi-criteria regulatory frameworks across jurisdictions."
prerequisites:
  required:
    - geo-infer-data
  recommended:
    - geo-infer-api
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-NORMS

## Instructions

### Workflow

1. **Define regulations and metrics** -- Create `ComplianceMetric` objects specifying evaluation type (`threshold`, `range`, `boolean`), primary field, and comparison rules
2. **Initialize a tracker** -- Instantiate `ComplianceTracker` with metrics bound to regulation IDs
3. **Validate metric binding** -- Verify each metric's `regulation_id` matches the target regulation; mismatched IDs silently return `compliance_level=0.0`
4. **Evaluate compliance** -- Call `tracker.evaluate_compliance(entity, regulation, data)` which returns a `ComplianceStatus` with weighted compliance level; check `status.metric_results` for per-metric pass/fail detail
5. **Query results** -- Use `get_entity_compliance()` or `get_regulation_compliance()` with explicit `as_of_date` for reproducible point-in-time queries
6. **Analyze impact** -- For policy changes, use `PolicyImpactAnalyzer` with context data to generate economic, social, and environmental impact reports

### Key Imports

```python
from geo_infer_norms.core.compliance_tracking import ComplianceTracker, ComplianceReport
from geo_infer_norms.core.normative_inference import NormativeInference, SocialNormDiffusion
from geo_infer_norms.core.policy_impact import PolicyImpactAnalyzer, RegulatoryImpactAssessment
from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer
from geo_infer_norms.models.compliance_status import ComplianceStatus, ComplianceMetric
from geo_infer_norms.models.regulation import Regulation
from geo_infer_norms.models.legal_entity import LegalEntity
```

## Examples

### Example 1: Multi-metric compliance evaluation

```python
from geo_infer_norms.core.compliance_tracking import ComplianceTracker
from geo_infer_norms.models.compliance_status import ComplianceMetric
from geo_infer_norms.models.regulation import Regulation
from geo_infer_norms.models.legal_entity import LegalEntity

# Define metrics for an air quality regulation
air_metric = ComplianceMetric.create(
    name="pm25_level",
    description="PM2.5 particulate threshold",
    regulation_id="reg-air-001",
    evaluation_type="threshold",
    primary_field="pm25",
    comparison="less_than",
    threshold_value=35.0,
    weight=2.0,
)
noise_metric = ComplianceMetric.create(
    name="noise_db",
    description="Acceptable noise range",
    regulation_id="reg-air-001",
    evaluation_type="range",
    primary_field="noise_level",
    range_min=0.0,
    range_max=70.0,
    weight=1.0,
)

tracker = ComplianceTracker(
    name="Environmental Compliance",
    compliance_metrics=[air_metric, noise_metric],
)

# Evaluate -- returns ComplianceStatus with weighted compliance_level
entity = LegalEntity(id="site-42", name="Industrial Site 42")
regulation = Regulation(id="reg-air-001", name="Air Quality Standard")
status = tracker.evaluate_compliance(
    entity, regulation, {"pm25": 28.0, "noise_level": 65}
)
print(f"Compliant: {status.is_compliant}, Level: {status.compliance_level:.2f}")
```

### Example 2: Bayesian normative inference with spatial constraints

```python
from geo_infer_norms.core.normative_inference import NormativeInference
from shapely.geometry import Point, Polygon

engine = NormativeInference()

# Add a speed-limit norm with a spatial boundary
zone = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
norm_id = engine.add_norm(
    name="speed_limit_30",
    condition=lambda obs: obs.get("speed", 0) <= 30,
    probability=0.95,
    spatial_constraint=zone,
)

# Record observations and infer compliance
engine.add_observation("vehicle-1", "speed", 25, location=Point(0.5, 0.5))
probability = engine.infer_compliance("vehicle-1", norm_id)
print(f"Compliance probability: {probability:.2f}")

# Identify violations across all norms below a threshold
violations = engine.identify_norm_violations("vehicle-1", threshold=0.3)
for v in violations:
    print(f"  Violation: {v['norm_name']} (severity {v['severity']:.2f})")
```

### Example 3: Policy impact assessment

```python
from geo_infer_norms.core.policy_impact import PolicyImpactAnalyzer

class ZoningPolicy:
    policy_type = "zoning_change"
    zoning_details = {"upzoning": True}

analyzer = PolicyImpactAnalyzer(
    policy=ZoningPolicy(),
    context_data={
        "economic_data": {
            "property_values": {"total_value": 5_000_000},
            "employment": {"total_jobs": 1200},
        }
    },
)
report = analyzer.generate_impact_report()
econ_df = report["economic"]
print(econ_df[["impact_category", "impact_type", "impact_value"]])
```

## Guidelines

### Error Handling

- `evaluate_compliance` logs a warning and returns `compliance_level=0.0` when no metrics match the regulation ID -- always bind metrics to the correct `regulation_id`
- `NormativeInference.check_norm_compliance` catches exceptions in user-supplied `condition` callables and returns `(False, 0.0)` -- keep condition functions pure and free of side effects
- Missing `required_fields` in evaluation data cause per-metric failures (logged), not full evaluation failure -- check `metric_results` in the returned `ComplianceStatus` for individual notes

### Common Pitfalls

- **Stale `as_of_date`**: `get_entity_compliance()` defaults to `datetime.now()` -- pass an explicit timestamp for reproducible queries
- **Weight normalization**: Overall compliance level is a weighted average across metrics; uneven weights can mask failing metrics that have low weight
- **Spatial constraint ordering**: Norm spatial constraints are checked before the condition callable -- an entity outside the polygon returns `(False, 1.0)` with full certainty, skipping the condition entirely
- **Norm relationships**: `infer_network_compliance` blends direct probability (70%) with relationship influence (30%) -- ensure `add_norm_relationship` uses correct `relationship_type` values (`"supports"` or `"conflicts"`)

### Integrations

- **METAGOV**: Governance compliance monitoring -- feed `ComplianceTracker` outputs into METAGOV dashboards
- **REQ**: Requirements compliance tracking -- map requirement IDs to `regulation_id` fields
- **SPACE**: Export compliance to GeoDataFrame via `export_compliance_to_geodataframe()` for spatial overlay analysis

### Testing

```bash
uv run python -m pytest GEO-INFER-NORMS/tests/ -v
```
