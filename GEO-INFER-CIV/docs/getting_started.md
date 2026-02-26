# Getting Started with GEO-INFER-CIV

This guide covers installation, core concepts, and building your first civic participation analysis.

## Installation

```bash
uv pip install -e ./GEO-INFER-CIV
```

For spatial analysis and economic integration:

```bash
uv pip install -e ./GEO-INFER-CIV ./GEO-INFER-SPACE ./GEO-INFER-ECON ./GEO-INFER-DATA
```

### Dependencies

GEO-INFER-CIV requires Python 3.9+ with standard library only for core functionality. No heavy dependencies are needed for the engagement, participation, and policy analysis classes.

Optional dependencies for spatial and data integration:

- `geo_infer_space` -- H3 hexagonal grid mapping
- `geo_infer_data` -- Census and election data ingestion
- `geo_infer_econ` -- Economic modeling for cost-benefit analysis

## Core Concepts

### Civic Engagement Metrics

GEO-INFER-CIV measures civic engagement through three lenses:

**Meeting Attendance** (`AttendanceTracker`): Track registered vs. actual attendees across meeting types (city council, planning commission, public hearing, town hall, workshop, community forum, budget hearing). Compute linear regression trends, per-type averages, and meeting effectiveness scores.

**Public Comments** (`PublicCommentAnalyzer`): Categorize comments (support, opposition, question, suggestion, concern, neutral), measure engagement depth through Shannon entropy of category diversity, comment length, and unique submitter ratio.

**Voter Turnout** (`VoterTurnoutModel`): Model historical election turnout by type, predict future turnout with adjustments for contestedness and media coverage.

### Participation Analysis

`ParticipationAnalyzer` scores engagement across eight participation methods:

| Method | Description |
|--------|------------|
| `SURVEY` | Written or online survey responses |
| `PUBLIC_COMMENT` | Formal public comment submissions |
| `TOWN_HALL` | In-person town hall attendance |
| `WORKSHOP` | Participatory workshop sessions |
| `ONLINE_FORUM` | Digital forum participation |
| `BALLOT` | Voting in elections or referenda |
| `PETITION` | Petition signing |
| `MAP_ANNOTATION` | Spatial feedback through map tools |

The engagement score combines four components with configurable weights:

- **Method-weighted participation rates** (35%): How many people participated via each method, weighted by method importance.
- **Temporal consistency** (20%): How evenly participation is distributed over time, measured by chi-squared deviation from uniform distribution.
- **Method diversity** (20%): Shannon entropy of participation methods used, normalized to [0, 1].
- **Reach ratio** (25%): Unique participants divided by target population.

### Policy Impact Assessment

`CostBenefitAnalyzer` evaluates policy proposals through:

- **Net Present Value (NPV)**: Future costs and benefits discounted to present value.
- **Benefit-Cost Ratio**: Total discounted benefits divided by total discounted costs.
- **Internal Rate of Return**: Discount rate at which NPV equals zero.
- **Risk-Adjusted NPV**: NPV weighted by probability of each cost/benefit occurring.

`EquityScore` evaluates distributional fairness across demographics using Gini coefficients and disparate impact detection.

## First Example: Civic Engagement Index

Compute an engagement score for a city using meeting attendance and public comment data.

```python
from geo_infer_civ.core.civic_engagement import (
    AttendanceTracker,
    MeetingRecord,
    MeetingType,
    PublicCommentAnalyzer,
    PublicComment,
    CommentCategory,
)

# ---- Meeting Attendance ----
tracker = AttendanceTracker()

# Add 6 months of meeting data
meetings = [
    MeetingRecord("mtg_001", MeetingType.CITY_COUNCIL, 1704067200.0, 200, 145, 23),
    MeetingRecord("mtg_002", MeetingType.CITY_COUNCIL, 1706745600.0, 200, 162, 31),
    MeetingRecord("mtg_003", MeetingType.PLANNING_COMMISSION, 1704672000.0, 80, 52, 15),
    MeetingRecord("mtg_004", MeetingType.PLANNING_COMMISSION, 1707350400.0, 80, 61, 19),
    MeetingRecord("mtg_005", MeetingType.PUBLIC_HEARING, 1705276800.0, 150, 98, 42),
    MeetingRecord("mtg_006", MeetingType.TOWN_HALL, 1705881600.0, 300, 187, 56),
    MeetingRecord("mtg_007", MeetingType.BUDGET_HEARING, 1708041600.0, 120, 78, 28),
    MeetingRecord("mtg_008", MeetingType.COMMUNITY_FORUM, 1708646400.0, 100, 89, 35),
]
tracker.add_meetings(meetings)

# Compute overall attendance trend
trend = tracker.compute_attendance_trend()
print("--- Attendance Trend ---")
print(f"Average attendance: {trend.average_attendance}")
print(f"Attendance rate: {trend.attendance_rate:.1%}")
print(f"Trend direction: {trend.trend_direction} (slope={trend.trend_slope:.2f})")
print(f"Peak meeting type: {trend.peak_meeting_type}")
print(f"Lowest meeting type: {trend.lowest_meeting_type}")

# Meeting effectiveness for town hall
effectiveness = tracker.get_meeting_effectiveness("mtg_006")
print(f"\nTown Hall effectiveness: {effectiveness['effectiveness_score']:.3f}")

# ---- Public Comments ----
analyzer = PublicCommentAnalyzer()

comments = [
    PublicComment("c01", "mtg_005", CommentCategory.SUPPORT, 150, 1705276900.0, "p001", "zoning"),
    PublicComment("c02", "mtg_005", CommentCategory.OPPOSITION, 280, 1705277000.0, "p002", "zoning"),
    PublicComment("c03", "mtg_005", CommentCategory.QUESTION, 45, 1705277100.0, "p003", "zoning"),
    PublicComment("c04", "mtg_005", CommentCategory.SUGGESTION, 200, 1705277200.0, "p004", "transit"),
    PublicComment("c05", "mtg_005", CommentCategory.CONCERN, 120, 1705277300.0, "p005", "transit"),
    PublicComment("c06", "mtg_005", CommentCategory.SUPPORT, 90, 1705277400.0, "p001", "transit"),
    PublicComment("c07", "mtg_005", CommentCategory.NEUTRAL, 60, 1705277500.0, "p006", "zoning"),
    PublicComment("c08", "mtg_006", CommentCategory.OPPOSITION, 350, 1705881700.0, "p007", "budget"),
    PublicComment("c09", "mtg_006", CommentCategory.SUPPORT, 180, 1705881800.0, "p008", "budget"),
    PublicComment("c10", "mtg_006", CommentCategory.CONCERN, 220, 1705881900.0, "p009", "parks"),
]
analyzer.add_comments(comments)

# Analyze comments for the public hearing
analysis = analyzer.analyze(meeting_id="mtg_005")
print("\n--- Public Comment Analysis (Public Hearing) ---")
print(f"Total comments: {analysis.total_comments}")
print(f"Category distribution: {analysis.category_distribution}")
print(f"Average word count: {analysis.average_word_count}")
print(f"Unique submitters: {analysis.unique_submitters}")
print(f"Engagement depth score: {analysis.engagement_depth_score:.3f}")
```

## Voter Turnout Modeling

```python
from geo_infer_civ.core.civic_engagement import VoterTurnoutModel

model = VoterTurnoutModel()

# Add historical election data
model.add_election("e01", 50000, 32000, "general", 1667260800.0, True, 0.8)
model.add_election("e02", 50000, 18000, "primary", 1654041600.0, True, 0.4)
model.add_election("e03", 48000, 12000, "special", 1640995200.0, False, 0.2)
model.add_election("e04", 52000, 35000, "general", 1699228800.0, True, 0.9)

# Predict turnout for upcoming election
prediction = model.predict_turnout(
    eligible_voters=55000,
    election_type="general",
    is_contested=True,
    media_coverage_score=0.7,
)
print("\n--- Turnout Prediction ---")
print(f"Predicted turnout rate: {prediction['predicted_turnout_rate']:.1%}")
print(f"Predicted voters: {prediction['predicted_voters']}")
print(f"Confidence: {prediction['confidence']:.2f}")
print(f"Base rate: {prediction['base_rate']:.1%}")
print(f"Adjustments: {prediction['adjustments']}")
```

## Participation Analysis with Representation

```python
from geo_infer_civ.core.participation import (
    ParticipationAnalyzer,
    ParticipantRecord,
    ParticipationMethod,
)

analyzer = ParticipationAnalyzer()

# Add participation records with demographics
records = [
    ParticipantRecord("p01", ParticipationMethod.TOWN_HALL, 1705276800.0, "group_a"),
    ParticipantRecord("p02", ParticipationMethod.SURVEY, 1705363200.0, "group_a"),
    ParticipantRecord("p03", ParticipationMethod.PUBLIC_COMMENT, 1705449600.0, "group_b"),
    ParticipantRecord("p04", ParticipationMethod.ONLINE_FORUM, 1705536000.0, "group_b"),
    ParticipantRecord("p05", ParticipationMethod.WORKSHOP, 1705622400.0, "group_c"),
    ParticipantRecord("p06", ParticipationMethod.MAP_ANNOTATION, 1705708800.0, "group_a"),
    ParticipantRecord("p07", ParticipationMethod.BALLOT, 1705795200.0, "group_b"),
    ParticipantRecord("p08", ParticipationMethod.PETITION, 1705881600.0, "group_c"),
    ParticipantRecord("p09", ParticipationMethod.TOWN_HALL, 1705968000.0, "group_a"),
    ParticipantRecord("p10", ParticipationMethod.SURVEY, 1706054400.0, "group_d"),
]
analyzer.add_records(records)

# Compute engagement score
score = analyzer.compute_engagement_score(target_population=5000)
print("\n--- Engagement Score ---")
print(f"Overall score: {score.overall_score:.3f}")
print(f"Method scores: {score.method_scores}")
print(f"Temporal consistency: {score.temporal_consistency:.3f}")
print(f"Diversity index: {score.diversity_index:.3f}")
print(f"Reach ratio: {score.reach_ratio:.4f}")

# Analyze demographic representation
report = analyzer.analyze_representation(
    population_demographics={
        "group_a": 0.40,
        "group_b": 0.30,
        "group_c": 0.20,
        "group_d": 0.10,
    }
)
print(f"\n--- Representation Report ---")
print(f"Overall representation score: {report.overall_representation_score:.3f}")
print(f"Representation indices: {report.representation_indices}")
print(f"Underrepresented: {report.underrepresented_groups}")
print(f"Overrepresented: {report.overrepresented_groups}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for complete method documentation
- Follow the [Basic Example](examples/basic_example.md) for a full city-level civic participation index
- Explore the [Advanced Example](examples/advanced_example.md) for multi-criteria community resilience scoring
