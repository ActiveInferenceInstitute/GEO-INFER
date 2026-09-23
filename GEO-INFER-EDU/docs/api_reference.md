# GEO-INFER-EDU API Reference

Complete class and method reference for the GEO-INFER-EDU education analytics module.

---

## core.curriculum

### EducationLevel (Enum)

| Value | Description |
|-------|------------|
| `ELEMENTARY` | Ages 6-11 |
| `MIDDLE_SCHOOL` | Ages 11-14 |
| `HIGH_SCHOOL` | Ages 14-18 |
| `INTERMEDIATE` | Upper secondary / pre-university |
| `UNDERGRADUATE` | University |
| `GRADUATE` | Masters/PhD |
| `PROFESSIONAL` | Practitioners |

### PedagogicalApproach (Enum)

| Value | Description |
|-------|------------|
| `CONSTRUCTIVIST` | Build knowledge through experience |
| `INQUIRY_BASED` | Question-driven exploration |
| `PROJECT_BASED` | Real-world project learning |
| `COMPETENCY_BASED` | Master skills before advancing |
| `EXPERIENTIAL` | Hands-on field and lab work |

### LearningObjective (dataclass)

```python
@dataclass
class LearningObjective:
    id: str
    description: str
    bloom_level: str            # remember, understand, apply, analyze, evaluate, create
    competency_area: str
    assessment_criteria: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
```

### CurriculumModule (dataclass)

```python
@dataclass
class CurriculumModule:
    id: str
    title: str
    description: str
    learning_objectives: List[LearningObjective]
    duration_hours: float
    content_sections: List[Dict[str, Any]] = field(default_factory=list)
    activities: List[Dict[str, Any]] = field(default_factory=list)
    assessments: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
```

### Curriculum (dataclass)

```python
@dataclass
class Curriculum:
    id: str
    title: str
    description: str
    level: EducationLevel
    duration_weeks: int
    modules: List[CurriculumModule] = field(default_factory=list)
    standards_alignment: Dict[str, List[str]] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    target_competencies: List[str] = field(default_factory=list)
```

### CurriculumDesigner

Design and generate standards-aligned geospatial curricula. Supports the standards keys `bok`, `gistbok`, and `ngss`.

```python
class CurriculumDesigner:
    def __init__(
        self,
        standards: Optional[List[str]] = None,
        pedagogical_approach: str = "constructivist",
        assessment_framework: str = "competency_based",
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `standards` | `Optional[List[str]]` | `None` | Standards keys to align against (`bok`, `gistbok`, `ngss`) |
| `pedagogical_approach` | `str` | `"constructivist"` | Teaching methodology name |
| `assessment_framework` | `str` | `"competency_based"` | Assessment framework name |

#### `design(topic: str, level: str, duration: str, learning_objectives: Optional[List[str]] = None) -> Curriculum`

Design a complete curriculum for a topic (e.g. `design("geospatial_analysis", "undergraduate", "8_weeks")`).

#### `generate_modules(topic: str, level: EducationLevel, duration_weeks: int, objectives: List[LearningObjective], hours_per_module: float = 4.0) -> List[CurriculumModule]`

Generate curriculum modules from a topic and objectives.

#### `align_with_standards(curriculum: Curriculum, target_standards: List[str], coverage_report: bool = False) -> Dict[str, Any]`

Align a curriculum with target standards; optionally returns a coverage report.

#### `create_learning_pathway(learner_profile: Dict[str, Any], target_competencies: List[str], available_time: str, optimization: str = "efficiency") -> Dict[str, Any]`

Create a personalized learning pathway for a learner profile.

#### `export_curriculum(curriculum: Curriculum, format: str = "yaml") -> str`

Export a curriculum to `yaml` or `json`.

---

## core.progress

### CompetencyLevel (Enum)

| Value | Description |
|-------|------------|
| `NOT_STARTED` | No exposure |
| `EMERGING` | Initial exposure, guided practice |
| `DEVELOPING` | Building skills, some independence |
| `PROFICIENT` | Consistent independent performance |
| `EXEMPLARY` | Expert-level, can teach others |

### LearnerActivity (dataclass)

```python
@dataclass
class LearnerActivity:
    activity_id: str
    activity_type: str          # exercise, reading, video, assessment
    topic: str
    start_time: datetime
    end_time: Optional[datetime] = None
    completion_status: str = "in_progress"  # in_progress, completed, abandoned
    score: Optional[float] = None           # 0.0 to 1.0
    time_spent_minutes: float = 0
    attempts: int = 1
```

### CompetencyRecord (dataclass)

```python
@dataclass
class CompetencyRecord:
    competency_id: str
    competency_name: str
    level: CompetencyLevel
    evidence: List[str] = field(default_factory=list)
    last_assessed: Optional[datetime] = None
    confidence: float = 0.0     # 0.0 to 1.0
```

### LearnerProgress (dataclass)

```python
@dataclass
class LearnerProgress:
    learner_id: str
    activities: List[LearnerActivity] = field(default_factory=list)
    competencies: Dict[str, CompetencyRecord] = field(default_factory=dict)
    total_time_hours: float = 0
    completion_rate: float = 0
    current_streak_days: int = 0
    last_activity_date: Optional[datetime] = None
```

### ProgressTracker

Track and analyze learner progress with competency-based assessment.

```python
class ProgressTracker:
    def __init__(
        self,
        competency_framework: str = "geospatial_bok",
        analytics_level: str = "detailed",
        privacy_compliance: str = "ferpa",
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `competency_framework` | `str` | `"geospatial_bok"` | Competency framework for assessment |
| `analytics_level` | `str` | `"detailed"` | Analytics detail level (basic, detailed) |
| `privacy_compliance` | `str` | `"ferpa"` | Privacy regulation compliance (ferpa, gdpr) |

#### `track_progress(learner_id: str, activity_log: List[Dict[str, Any]], assessments: Optional[List[Dict[str, Any]]] = None) -> LearnerProgress`

Record a learner's activity log (and optional assessment results) and return the updated `LearnerProgress`.

#### `generate_competency_report(learner_id: str, competencies: Optional[List[str]] = None, visualization: str = "radar_chart") -> Dict[str, Any]`

Generate a competency achievement report, optionally restricted to named competencies.

#### `export_progress(learner_id, format: str = "json") -> str`

Export a learner's progress honouring the configured privacy policy. Under `ferpa` the student identifier is replaced with a one-way pseudonym; under `gdpr` data-retention metadata (retention period, erasure availability) is attached; under `none` the raw identifier is included.

#### `identify_gaps(learner_progress: LearnerProgress, required_competencies: List[str], recommendations: bool = True) -> Dict[str, Any]`

Identify knowledge gaps between the learner's current competencies and the required set; optionally includes recommended activities.

#### `generate_analytics(cohort: List[str], metrics: List[str], aggregation: str = "weekly", visualization: str = "dashboard") -> Dict[str, Any]`

Generate learning analytics for a cohort of learner IDs over the requested metrics.

#### `identify_at_risk(cohort: List[str], risk_indicators: List[str], intervention_recommendations: bool = True) -> List[Dict[str, Any]]`

Identify learners at risk of failure from the given risk indicators; optionally attaches intervention recommendations.

---

## core.exercises

### ExerciseGenerator

Generate interactive geospatial exercises.

```python
class ExerciseGenerator:
    def __init__(
        self,
        exercise_types: Optional[List[str]] = None,
        difficulty_scaling: str = "adaptive",
        feedback_mode: str = "immediate",
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exercise_types` | `Optional[List[str]]` | `["mapping", "analysis", "coding"]` | Exercise types to generate |
| `difficulty_scaling` | `str` | `"adaptive"` | `'adaptive'`, `'fixed'`, or `'progressive'` |
| `feedback_mode` | `str` | `"immediate"` | `'immediate'`, `'delayed'`, or `'on_submit'` |

#### `create(concepts: List[str], format: str = "interactive_map", difficulty: str = "progressive", include_hints: bool = True) -> List[Exercise]`

Create exercises covering the given concepts. Formats: `interactive_map`, `code`, `quiz`, `practical`.

#### `create_coding_exercises(topic: str, language: str = "python", framework: str = "geo_infer", test_cases: bool = True, starter_code: bool = True) -> List[Exercise]`

Generate coding exercises for a topic, optionally with test cases and starter code.

#### `create_pbl_scenario(context: str, problem: str, data_provided: List[str], expected_deliverables: List[str]) -> Exercise`

Create a problem-based learning scenario for a real-world context.

#### `create_assessment(learning_objectives: List[Dict[str, str]], item_types: List[str], difficulty_distribution: Dict[str, float], rubrics: bool = True) -> Assessment`

Create an assessment with multiple items over the given objectives. Item types: `multiple_choice`, `practical`, `project`.

---

## core.personalization

### PersonalizedLearning

Provide personalized learning experiences through adaptive pathways, intelligent recommendations, and spaced repetition.

```python
class PersonalizedLearning:
    def __init__(
        self,
        adaptation_method: str = "knowledge_tracing",
        recommendation_algorithm: str = "collaborative_filtering",
        learning_styles: Optional[List[str]] = None,
    )
```

#### `register_resource(resource: LearningResource | Dict[str, Any]) -> LearningResource`

Register a learning resource supplied by the content owner.

#### `register_learner(learner_profile: Dict[str, Any]) -> LearnerProfile`

Register a new learner. Mastery state is initialized only for genuinely new learners; re-registering an existing learner keeps accumulated mastery.

#### `create_pathway(learner_profile: Dict[str, Any], learning_goals: List[str], constraints: Dict[str, Any], optimization: str = "mastery") -> LearningPathway`

Create a personalized learning pathway toward the given learning goals under the supplied constraints.

#### `recommend_resources(learner_id: str, current_topic: str, resource_types: Optional[List[str]] = None, difficulty: str = "appropriate") -> List[Dict[str, Any]]`

Recommend learning resources for a learner.

#### `deliver_adaptive_content(learner_id: str, topic: str, format_preference: Optional[str] = None, mastery_level: Optional[float] = None) -> Dict[str, Any]`

Deliver adaptive content tailored to the learner's mastery level and preferred format.

#### `schedule_review(learner_id: str, mastered_topics: List[str], retention_model: str = "forgetting_curve", review_frequency: str = "optimal") -> List[Dict[str, Any]]`

Schedule spaced-repetition reviews for mastered topics.

#### `update_mastery(learner_id: str, topic: str, performance_score: float) -> float`

Update a learner's mastery level for a topic based on a performance score.

---

## core.professional

### ProfessionalDevelopment

Continuing education and professional development for GIS professionals.

```python
class ProfessionalDevelopment:
    def __init__(
        self,
        certification_bodies: Optional[List[str]] = None,
        credit_tracking: bool = True,
        competency_framework: str = "professional",
    )
```

#### `register_professional(profile_data: Dict[str, Any]) -> ProfessionalProfile`

Register a professional in the system from a profile data dict.

#### `track_continuing_education(professional_id: str, activities: List[Dict[str, Any]], credits_earned: Optional[float] = None) -> Dict[str, Any]`

Track continuing education activities and credit totals for a professional.

#### `create_certification_pathway(target_certification: str, current_qualifications: Dict[str, Any], timeline: str = "12_months") -> CertificationPathway`

Create a pathway toward a target certification from current qualifications.

#### `analyze_career_skills(current_skills: List[str], target_role: str, job_market_data: Optional[Dict[str, Any]] = None, recommendations: bool = True) -> Dict[str, Any]`

Analyze skill gaps for a target career role, optionally against job-market data.

#### `develop_portfolio(projects: List[Dict[str, Any]], competencies_demonstrated: Dict[str, List[str]], format: str = "professional_portfolio") -> Dict[str, Any]`

Develop a professional portfolio from projects and demonstrated competencies.

#### `get_recertification_status(professional_id: str, certification: str) -> Dict[str, Any]`

Check recertification status for a certification.
