---
name: geo-infer-metagov
description: "Designs governance structures, maps stakeholder relationships, and resolves spatial resource conflicts for geospatial decision-making. Use when planning land use governance across jurisdictions, running multi-stakeholder spatial planning, analyzing institutional arrangements at multiple governance levels, mediating overlapping territorial claims, or setting up adaptive governance triggers for natural resource management."
prerequisites:
  required:
    - geo-infer-data
    - geo-infer-api
  recommended:
    - geo-infer-norms
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-METAGOV

## Instructions

### Step 1: Set Up Governance Context

Define the governance scope by initializing the polycentric governance framework with jurisdictional boundaries and decision centers. Every governance workflow starts here.

```python
from geo_infer_metagov.core.polycentric import PolycentricGovernance
from geo_infer_metagov.core.multi_level import MultiLevelAnalyzer

governance = PolycentricGovernance(region="watershed_district_7")
governance.add_decision_center("municipal", level="local", authority=["zoning", "permits"])
governance.add_decision_center("regional_authority", level="regional", authority=["water_rights", "environmental"])

# Validate hierarchy before proceeding -- catches circular authority delegation
governance.validate_hierarchy()
```

### Step 2: Map and Analyze Stakeholders

Register all relevant stakeholders with power and interest scores (0.0-1.0). Build the power-interest matrix to identify engagement priorities.

```python
from geo_infer_metagov.core.stakeholder import StakeholderAnalyzer

analyzer = StakeholderAnalyzer()
analyzer.register("community_group", power=0.3, interest=0.9)
analyzer.register("government", power=0.8, interest=0.6)
analyzer.register("private_developer", power=0.7, interest=0.8)
matrix = analyzer.build_power_interest_matrix()
strategies = analyzer.recommend_strategies()
# Verify at least 2 stakeholders registered (matrix degenerates with fewer)
assert len(analyzer.get_registered()) >= 2, "Need at least 2 stakeholders for meaningful analysis"
```

### Step 3: Detect and Resolve Conflicts

Run spatial conflict detection across overlapping jurisdictions or competing land-use claims. Use mediation workflows when conflicts are found.

```python
from geo_infer_metagov.core.conflict_resolution import ConflictResolver

resolver = ConflictResolver(governance_context=governance)
conflicts = resolver.detect_spatial_conflicts(region="watershed_district_7")
for conflict in conflicts:
    resolution = resolver.mediate(conflict, stakeholders=analyzer.get_registered())
```

### Step 4: Configure Adaptive Governance and Monitoring

Set up scenario planning and performance monitoring to enable the governance framework to adapt to changing conditions.

```python
from geo_infer_metagov.core.adaptation import AdaptiveGovernance
from geo_infer_metagov.core.accountability import AccountabilityTracker

adaptive = AdaptiveGovernance(governance)
adaptive.add_scenario("drought", triggers=["rainfall_below_threshold"])
adaptive.add_scenario("rapid_development", triggers=["permit_rate_above_threshold"])

tracker = AccountabilityTracker(governance)
tracker.enable_audit_trail()
tracker.set_transparency_level("public")
```

## Examples

### Example 1: Stakeholder Power-Interest Analysis

Map stakeholders for a coastal development project and generate engagement recommendations.

```python
from geo_infer_metagov.core.stakeholder import StakeholderAnalyzer

analyzer = StakeholderAnalyzer()
analyzer.register("fishing_cooperative", power=0.2, interest=0.95)
analyzer.register("port_authority", power=0.85, interest=0.7)
analyzer.register("environmental_ngo", power=0.4, interest=0.9)
analyzer.register("tourism_board", power=0.5, interest=0.6)

matrix = analyzer.build_power_interest_matrix()
# Returns quadrant classification: manage_closely, keep_satisfied, keep_informed, monitor
strategies = analyzer.recommend_strategies()
# fishing_cooperative -> keep_informed (low power, high interest)
# port_authority -> manage_closely (high power, high interest)
```

### Example 2: Multi-Level Institutional Analysis

Analyze governance structures across nested jurisdictional levels for a transboundary resource.

```python
from geo_infer_metagov.core.institutional import InstitutionalAnalysis
from geo_infer_metagov.core.multi_level import MultiLevelAnalyzer

ia = InstitutionalAnalysis()
ia.define_rules("constitutional", scope="national", rules=["water_framework_directive"])
ia.define_rules("collective_choice", scope="regional", rules=["basin_management_plan"])
ia.define_rules("operational", scope="local", rules=["irrigation_schedule", "extraction_limits"])

multi = MultiLevelAnalyzer(ia)
gaps = multi.identify_governance_gaps()
# Returns mismatches between levels (e.g., local rules conflicting with regional mandates)
overlaps = multi.find_jurisdictional_overlaps(region="danube_basin")
```

### Example 3: Conflict Detection and Adaptive Response

Detect spatial conflicts in a mixed-use zone and set up adaptive governance triggers.

```python
from geo_infer_metagov.core.polycentric import PolycentricGovernance
from geo_infer_metagov.core.conflict_resolution import ConflictResolver
from geo_infer_metagov.core.adaptation import AdaptiveGovernance

governance = PolycentricGovernance(region="mixed_use_zone_12")
governance.add_decision_center("city_planning", level="local", authority=["land_use"])
governance.add_decision_center("env_agency", level="regional", authority=["habitat_protection"])

resolver = ConflictResolver(governance_context=governance)
conflicts = resolver.detect_spatial_conflicts(region="mixed_use_zone_12")

adaptive = AdaptiveGovernance(governance)
adaptive.add_scenario("habitat_encroachment", triggers=["development_within_buffer_zone"])
adaptive.enable_auto_escalation(threshold="high_severity")
# When triggered, escalates conflict to regional level for mediation
```

## Guidelines

### Best Practices

- **Register all stakeholders before conflict detection**: The `ConflictResolver` uses stakeholder data to weight dispute severity and recommend appropriate mediation paths. Running detection without stakeholders yields generic results.
- **Define governance levels top-down**: Start with constitutional rules, then collective choice, then operational. The `MultiLevelAnalyzer` checks consistency downward through the hierarchy.
- **Enable audit trails early**: Call `tracker.enable_audit_trail()` before any governance decisions are recorded. Retroactive auditing misses decisions made before activation.
- **Use scenario triggers, not polling**: `AdaptiveGovernance` scenarios with defined triggers are more efficient than periodic checks. Triggers integrate with GEO-INFER-IOT sensor data when available.

### Common Pitfalls

- **Power/interest values out of range**: `StakeholderAnalyzer.register()` expects values in `[0.0, 1.0]`. Values outside this range raise `ValueError`. Normalize before registering.
- **Circular authority delegation**: When two decision centers delegate authority to each other, `PolycentricGovernance` raises a `GovernanceCycleError`. Check authority chains with `governance.validate_hierarchy()` before running analysis.
- **Missing governance context in resolver**: `ConflictResolver` requires a `governance_context` parameter. Initializing without one defaults to a flat single-level model, which misses cross-jurisdictional conflicts.
- **Stale scenario triggers**: Adaptive governance scenarios must be refreshed when underlying data sources change. Call `adaptive.refresh_triggers()` after updating connected data pipelines.

### Edge Cases

- **No conflicts found**: `resolver.detect_spatial_conflicts()` returns an empty list when no overlapping claims exist. Always check `len(conflicts)` before iterating to avoid silent no-ops in reporting pipelines.
- **Single stakeholder**: The power-interest matrix degenerates with fewer than two stakeholders. `recommend_strategies()` returns a warning and defaults to "manage closely" for solo entries.
- **Cross-module governance**: When governance spans multiple GEO-INFER regions, use `PolycentricGovernance.federate()` to link separate governance instances rather than creating one oversized context.

### Integrations

- Integrates with **GEO-INFER-NORMS** for normative governance rule validation and compliance checks.
- Integrates with **GEO-INFER-CIV** for participatory governance and civic engagement workflows.
- Integrates with **GEO-INFER-IOT** for real-time sensor triggers in adaptive governance scenarios.
- DAO mechanisms are in development (Alpha) — API may change.

### Testing

```bash
uv run python -m pytest GEO-INFER-METAGOV/tests/ -v
```
