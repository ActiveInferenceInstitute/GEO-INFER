# GEO-INFER-CIV Documentation

GEO-INFER-CIV provides spatial analytics for civic participation, engagement measurement, and policy impact assessment. The module quantifies civic processes -- meeting attendance, public comment analysis, voter turnout, demographic representation -- and connects them to geographic contexts for equity and accessibility analysis.

## Module Overview

GEO-INFER-CIV operates across three functional areas:

1. **Civic Engagement Tracking** -- Measure and trend meeting attendance, analyze public comment sentiment and depth, model voter turnout patterns.
2. **Participation Analysis** -- Score engagement quality across multiple participation methods, compute participation indices against baselines, and analyze demographic representation.
3. **Policy Impact Assessment** -- Cost-benefit analysis with net present value, stakeholder impact matrices, and equity scoring with disparate impact detection.

## Core Capabilities

- **Attendance tracking**: Linear regression trends over time, per-meeting-type averages, effectiveness scoring combining attendance rate and comment engagement.
- **Public comment analysis**: Category distribution (support, opposition, question, suggestion, concern, neutral), Shannon entropy-based engagement depth scoring, sentiment analysis, unique submitter tracking.
- **Voter turnout modeling**: Historical turnout analysis by election type, prediction with adjustments for contestedness and media coverage, confidence estimation.
- **Participation scoring**: Multi-method engagement scores (survey, public comment, town hall, workshop, online forum, ballot, petition, map annotation), temporal consistency measurement, reach ratio calculation.
- **Representation analysis**: Group representation indices (participation proportion / population proportion), underrepresentation/overrepresentation detection at 0.8/1.2 thresholds, Gini coefficient for equity measurement.
- **Cost-benefit analysis**: Net present value with discount rates, benefit-cost ratios, internal rate of return, risk-adjusted NPV, category-level breakdowns.
- **Equity scoring**: Disparate impact flags, impact distribution across demographics, per-group economic, quality-of-life, environmental, and accessibility impact.

## Integration Points

| Module | Integration |
|--------|------------|
| GEO-INFER-SPACE | H3 spatial indexing for mapping civic data to hexagonal grids |
| GEO-INFER-DATA | Ingestion of census, election, and public records datasets |
| GEO-INFER-NORMS | Normative compliance checking for policy proposals |
| GEO-INFER-ECON | Economic impact modeling for cost-benefit analysis |
| GEO-INFER-PEP | Community relationship management and stakeholder tracking |

## Documentation Contents

- [Getting Started](getting_started.md) -- Installation, core concepts, first civic analysis
- [API Reference](api_reference.md) -- Class and method documentation
- [Basic Example: Civic Participation Index](examples/basic_example.md) -- Engagement scoring for a city
- [Advanced Example: Community Resilience Score](examples/advanced_example.md) -- Multi-criteria equity analysis

## Architecture

```
geo_infer_civ/
  core/
    civic_engagement.py  -- AttendanceTracker, PublicCommentAnalyzer, VoterTurnoutModel
    participation.py     -- ParticipationAnalyzer, EngagementScore, RepresentationReport
    policy_analysis.py   -- CostBenefitAnalyzer, StakeholderImpact, EquityScore
  models/
    engagement_models.py -- Data models for civic engagement
  api/
    endpoints.py         -- REST API for civic analytics
  utils/
    data_loader.py       -- Census and election data loading
```

## Quick Start

```python
from geo_infer_civ.core.civic_engagement import (
    AttendanceTracker, MeetingRecord, MeetingType,
)

tracker = AttendanceTracker()

# Add meeting records
tracker.add_meeting(MeetingRecord(
    meeting_id="mtg_001",
    meeting_type=MeetingType.CITY_COUNCIL,
    date=1700000000.0,
    registered_attendees=200,
    actual_attendees=145,
    public_comments_count=23,
))

tracker.add_meeting(MeetingRecord(
    meeting_id="mtg_002",
    meeting_type=MeetingType.PLANNING_COMMISSION,
    date=1700100000.0,
    registered_attendees=80,
    actual_attendees=52,
    public_comments_count=15,
))

# Compute attendance trend
trend = tracker.compute_attendance_trend()
print(f"Average attendance: {trend.average_attendance}")
print(f"Attendance rate: {trend.attendance_rate:.1%}")
print(f"Trend direction: {trend.trend_direction}")
```

## Key Concepts

**Engagement depth** measures the quality of civic participation beyond simple headcounts. It combines category diversity (Shannon entropy of comment types), comment length (depth of thought), and unique submitter ratio (breadth of participation).

**Representation indices** compare the proportion of each demographic group in civic participation against their proportion in the overall population. A ratio of 1.0 means perfect representation. Groups below 0.8 are flagged as underrepresented; above 1.2 as overrepresented.

**Participation index** normalizes actual participation rates against a baseline. An index of 1.0 means participation matches expectations; values above 1.0 indicate higher-than-expected engagement.
