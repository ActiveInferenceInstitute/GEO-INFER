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

Design and generate standards-aligned geospatial curricula.

```python
class CurriculumDesigner:
    def __init__(
        self,
        education_standard: str = "geospatial_bok",
        pedagogical_approach: PedagogicalApproach = PedagogicalApproach.PROJECT_BASED,
        level: EducationLevel = EducationLevel.UNDERGRADUATE,
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `education_standard` | `str` | `"geospatial_bok"` | Standards framework (geospatial_bok, gistbok, ngss) |
| `pedagogical_approach` | `PedagogicalApproach` | `PROJECT_BASED` | Teaching methodology |
| `level` | `EducationLevel` | `UNDERGRADUATE` | Target education level |

#### `create_module(title, description, objectives, duration_hours, **kwargs) -> CurriculumModule`

Create a curriculum module with learning objectives.

#### `generate_curriculum(title, description, modules, duration_weeks, **kwargs) -> Curriculum`

Generate a complete curriculum from modules.

#### `align_to_standard(curriculum, standard) -> Dict[str, List[str]]`

Map curriculum objectives to educational standard competencies.

#### `sequence_modules(modules) -> List[CurriculumModule]`

Order modules based on prerequisite dependencies using topological sort.

#### `generate_assessment(objectives, assessment_type) -> Dict[str, Any]`

Generate assessment items for given learning objectives. Assessment types: `quiz`, `project`, `portfolio`, `practical`.

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

#### `add_learner(learner_id: str) -> LearnerProgress`

Register a new learner in the tracking system.

#### `record_activity(learner_id, activity: LearnerActivity) -> None`

Record a learning activity for a learner.

#### `assess_competency(learner_id, competency_id, evidence) -> CompetencyRecord`

Assess a learner's competency level based on evidence (activity scores, assessment results).

#### `get_progress(learner_id) -> LearnerProgress`

Get complete progress record for a learner.

#### `identify_gaps(learner_id, target_competencies) -> List[Dict[str, Any]]`

Identify competency gaps between current level and target requirements. Returns list of gaps with competency ID, current level, target level, and recommended activities.

#### `detect_at_risk(threshold_days: int = 7) -> List[str]`

Identify learners who have not engaged for longer than `threshold_days`. Returns list of at-risk learner IDs.

#### `generate_analytics(learner_id) -> Dict[str, Any]`

Generate learning analytics summary: activity distribution, time patterns, score progression, competency progress, and engagement metrics.

---

## core.exercises

### ExerciseGenerator

Generate interactive geospatial exercises.

```python
class ExerciseGenerator:
    def __init__(self, difficulty: str = "intermediate")
```

#### `generate_exercise(topic, exercise_type, **kwargs) -> Dict[str, Any]`

Generate an exercise. Types: `map_reading`, `spatial_query`, `coordinate_conversion`, `data_analysis`, `visualization`.

#### `assess_submission(exercise_id, submission) -> Dict[str, Any]`

Assess a learner's exercise submission. Returns score, feedback, and competency mapping.

---

## core.personalization

### PersonalizedPathBuilder

Build adaptive learning paths.

```python
class PersonalizedPathBuilder:
    def __init__(self, learner_profile: Dict[str, Any])
```

#### `build_path(target_competencies, available_modules) -> List[CurriculumModule]`

Build an ordered learning path to achieve target competencies, considering prerequisites and learner's current state.

#### `adapt_path(current_progress, path) -> List[CurriculumModule]`

Adjust an existing learning path based on updated progress (skip mastered content, add remediation for weak areas).

---

## core.professional

### ProfessionalDevelopment

Continuing education resources.

```python
class ProfessionalDevelopment:
    def __init__(self, certification_body: str = "gis_professional")
```

#### `get_certification_requirements(certification: str) -> Dict[str, Any]`

Get requirements for a professional certification (GISP, GIS-P, etc.).

#### `track_credits(professional_id, activity) -> Dict[str, Any]`

Track continuing education credits for professional certification maintenance.

#### `recommend_development(professional_id, career_goals) -> List[Dict[str, Any]]`

Recommend professional development activities based on career goals and current competencies.
