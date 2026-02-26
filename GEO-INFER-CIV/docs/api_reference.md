# GEO-INFER-CIV API Reference

Complete class and method reference for the GEO-INFER-CIV civic analytics module.

---

## core.civic_engagement

### MeetingType (Enum)

Types of civic meetings.

| Value | Description |
|-------|------------|
| `CITY_COUNCIL` | Regular city council sessions |
| `PLANNING_COMMISSION` | Land use and development planning |
| `PUBLIC_HEARING` | Formal public hearing on specific topics |
| `TOWN_HALL` | Open town hall meetings |
| `WORKSHOP` | Interactive community workshops |
| `COMMUNITY_FORUM` | Community-organized discussion forums |
| `BUDGET_HEARING` | Budget review and approval hearings |

### CommentCategory (Enum)

Categories for classifying public comments.

| Value | Description |
|-------|------------|
| `SUPPORT` | Comment expresses support for the proposal |
| `OPPOSITION` | Comment expresses opposition |
| `QUESTION` | Comment poses a question |
| `SUGGESTION` | Comment offers a suggestion or alternative |
| `CONCERN` | Comment raises a concern without explicit opposition |
| `NEUTRAL` | Comment is informational or neutral |

### MeetingRecord (dataclass)

```python
@dataclass
class MeetingRecord:
    meeting_id: str
    meeting_type: MeetingType
    date: float                             # Unix timestamp
    registered_attendees: int
    actual_attendees: int
    public_comments_count: int = 0
    duration_minutes: float = 60.0
    location: Optional[Tuple[float, float]] = None
    topic: Optional[str] = None
```

### PublicComment (dataclass)

```python
@dataclass
class PublicComment:
    comment_id: str
    meeting_id: str
    category: CommentCategory
    word_count: int
    timestamp: float
    submitter_id: Optional[str] = None
    topic: Optional[str] = None
    sentiment_score: float = 0.0            # Range: [-1.0, 1.0]
```

### AttendanceTrend (dataclass)

Result of attendance trend analysis.

| Field | Type | Description |
|-------|------|-------------|
| `average_attendance` | `float` | Mean actual attendees across meetings |
| `attendance_rate` | `float` | Total actual / total registered |
| `trend_direction` | `str` | `"increasing"`, `"decreasing"`, or `"stable"` |
| `trend_slope` | `float` | Linear regression slope (attendees per meeting) |
| `peak_meeting_type` | `str` | Meeting type with highest average attendance |
| `lowest_meeting_type` | `str` | Meeting type with lowest average attendance |
| `meeting_count` | `int` | Number of meetings analyzed |

### AttendanceTracker

Track and analyze civic meeting attendance patterns.

```python
class AttendanceTracker:
    def __init__(self) -> None
```

#### `add_meeting(meeting: MeetingRecord) -> None`

Add a single meeting record to the tracker.

#### `add_meetings(meetings: List[MeetingRecord]) -> None`

Add multiple meeting records.

#### `compute_attendance_trend(meeting_type: Optional[MeetingType] = None) -> AttendanceTrend`

Compute attendance trend using linear regression on attendance over time. Optionally filter by meeting type.

The trend direction is determined by the regression slope:
- `slope > 0.5` -> `"increasing"`
- `slope < -0.5` -> `"decreasing"`
- Otherwise -> `"stable"`

Raises `ValueError` if no meeting records are available for the given filter.

#### `get_meeting_effectiveness(meeting_id: str) -> Dict[str, Any]`

Compute effectiveness for a specific meeting. The effectiveness score combines attendance rate (60% weight) and comment engagement rate (40% weight, capped at 1.0).

Returns: `meeting_id`, `meeting_type`, `attendance_rate`, `comment_rate`, `effectiveness_score`, `actual_attendees`, `registered_attendees`.

Raises `ValueError` if the meeting is not found.

---

### CommentAnalysis (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `total_comments` | `int` | Number of comments analyzed |
| `category_distribution` | `Dict[str, float]` | Proportion of each comment category |
| `average_word_count` | `float` | Mean words per comment |
| `average_sentiment` | `float` | Mean sentiment score |
| `unique_submitters` | `int` | Number of distinct submitters |
| `topics` | `Dict[str, int]` | Topic frequency counts |
| `engagement_depth_score` | `float` | Composite engagement quality (0-1) |

### PublicCommentAnalyzer

Analyze public comments submitted to civic processes.

```python
class PublicCommentAnalyzer:
    def __init__(self) -> None
```

#### `add_comment(comment: PublicComment) -> None` / `add_comments(comments: List[PublicComment]) -> None`

Add comment records.

#### `analyze(meeting_id: Optional[str] = None) -> CommentAnalysis`

Analyze all comments or filter by meeting. Engagement depth score is computed as:

```
depth = 0.4 * normalized_category_diversity + 0.3 * length_score + 0.3 * submitter_ratio
```

Where:
- `normalized_category_diversity` = Shannon entropy of category counts / max possible entropy
- `length_score` = min(avg_word_count / 200, 1.0)
- `submitter_ratio` = unique_submitters / total_comments

Returns empty `CommentAnalysis` with zero values if no comments match.

---

### VoterTurnoutModel

Model and predict voter turnout for civic elections.

```python
class VoterTurnoutModel:
    def __init__(self) -> None
```

#### `add_election(election_id, eligible_voters, actual_voters, election_type, date, is_contested=True, media_coverage_score=0.5) -> None`

Add a historical election record. Turnout rate is computed as `actual_voters / eligible_voters`.

#### `compute_average_turnout(election_type: Optional[str] = None) -> float`

Average turnout rate across all or filtered elections. Raises `ValueError` if no records match.

#### `predict_turnout(eligible_voters, election_type, is_contested=True, media_coverage_score=0.5) -> Dict[str, Any]`

Predict turnout for an upcoming election. The model starts with the average turnout for the election type (or overall average if no type-specific data), then applies:

- **Contest adjustment**: Difference between contested and uncontested average turnout rates
- **Media adjustment**: `(media_coverage_score - 0.5) * 0.10`

Returns: `predicted_turnout_rate`, `predicted_voters`, `eligible_voters`, `confidence`, `base_rate`, `adjustments` (contest_effect, media_effect).

Confidence = min(1.0, n_records / 10).

#### `get_turnout_summary() -> Dict[str, Any]`

Summary with `total_elections`, `overall_average_turnout`, and `by_type` breakdown (count, average, min, max per election type).

---

## core.participation

### ParticipationMethod (Enum)

Eight methods of civic participation: `SURVEY`, `PUBLIC_COMMENT`, `TOWN_HALL`, `WORKSHOP`, `ONLINE_FORUM`, `BALLOT`, `PETITION`, `MAP_ANNOTATION`.

### ParticipantRecord (dataclass)

```python
@dataclass
class ParticipantRecord:
    participant_id: str
    method: ParticipationMethod
    timestamp: float
    demographic_group: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    sentiment_score: Optional[float] = None
    weight: float = 1.0
```

### EngagementScore (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `overall_score` | `float` | Weighted composite score (0-1) |
| `method_scores` | `Dict[str, float]` | Per-method participation rates |
| `temporal_consistency` | `float` | Evenness of participation over time (0-1) |
| `diversity_index` | `float` | Normalized Shannon entropy of methods (0-1) |
| `reach_ratio` | `float` | Unique participants / target population |

### RepresentationReport (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `group_proportions` | `Dict[str, float]` | Participation proportions per group |
| `population_proportions` | `Dict[str, float]` | Population proportions (input) |
| `representation_indices` | `Dict[str, float]` | Participation proportion / population proportion |
| `overall_representation_score` | `float` | 1.0 minus standard deviation of indices |
| `underrepresented_groups` | `List[str]` | Groups with index < 0.8 |
| `overrepresented_groups` | `List[str]` | Groups with index > 1.2 |

### ParticipationAnalyzer

```python
class ParticipationAnalyzer:
    def __init__(self, method_weights: Optional[Dict[ParticipationMethod, float]] = None)
```

Default: equal weights for all methods.

#### `add_record(record) -> None` / `add_records(records) -> None` / `clear_records() -> None`

Manage participation records.

#### `compute_engagement_score(target_population: int, time_window: Optional[Tuple[float, float]] = None) -> EngagementScore`

Compute the composite engagement score. Raises `ValueError` if `target_population <= 0`.

Weights: method_avg=0.35, temporal_consistency=0.20, diversity=0.20, reach=0.25.

#### `compute_participation_index(target_population: int, baseline_rate: float = 0.10) -> float`

Normalized participation index = (unique_participants / target_population) / baseline_rate. A value of 1.0 means participation matches the baseline.

#### `analyze_representation(population_demographics: Dict[str, float]) -> RepresentationReport`

Analyze demographic representation. `population_demographics` maps group names to their population proportion (should sum to 1.0). Raises `ValueError` if empty.

#### `get_participation_summary() -> Dict[str, Any]`

Returns `total_records`, `unique_participants`, `method_counts`, `average_sentiment`.

---

## core.policy_analysis

### ImpactLevel (Enum)

`VERY_NEGATIVE` (-2), `NEGATIVE` (-1), `NEUTRAL` (0), `POSITIVE` (1), `VERY_POSITIVE` (2).

### PolicyDomain (Enum)

`LAND_USE`, `TRANSPORTATION`, `HOUSING`, `ENVIRONMENT`, `PUBLIC_SAFETY`, `ECONOMIC_DEVELOPMENT`, `EDUCATION`, `HEALTH`, `INFRASTRUCTURE`.

### CostBenefitItem (dataclass)

```python
@dataclass
class CostBenefitItem:
    name: str
    amount: float
    is_benefit: bool
    probability: float = 1.0
    time_horizon_years: int = 1
    category: Optional[str] = None
    description: Optional[str] = None
```

### StakeholderImpact (dataclass)

```python
@dataclass
class StakeholderImpact:
    group_name: str
    population_size: int
    impact_level: ImpactLevel
    economic_impact: float = 0.0
    quality_of_life_impact: float = 0.0
    environmental_impact: float = 0.0
    accessibility_impact: float = 0.0
```

### CostBenefitAnalyzer

```python
class CostBenefitAnalyzer:
    def __init__(self, discount_rate: float = 0.05)
```

Raises `ValueError` if `discount_rate` is not in [0, 1).

#### `add_item(item: CostBenefitItem) -> None`

Add a cost or benefit item.

#### `analyze() -> CostBenefitResult`

Run cost-benefit analysis. Returns `total_costs`, `total_benefits`, `net_present_value`, `benefit_cost_ratio`, `internal_rate_of_return`, `payback_period_years`, `risk_adjusted_npv`, `category_breakdown`.

### EquityScore (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `overall_equity_score` | `float` | Composite equity metric (0-1) |
| `gini_coefficient` | `float` | Inequality measure (0=equal, 1=unequal) |
| `impact_distribution` | `Dict[str, float]` | Per-group net impact |
| `most_impacted_group` | `str` | Group with largest absolute impact |
| `least_impacted_group` | `str` | Group with smallest absolute impact |
| `disparate_impact_flags` | `List[str]` | Groups with disproportionate impacts |
