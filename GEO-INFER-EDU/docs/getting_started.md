# Getting Started with GEO-INFER-EDU

This guide covers installation, core concepts, and building your first geospatial education analysis.

## Installation

```bash
uv pip install -e ./GEO-INFER-EDU
```

For spatial exercises and data integration:

```bash
uv pip install -e ./GEO-INFER-EDU ./GEO-INFER-SPACE ./GEO-INFER-DATA
```

### Dependencies

GEO-INFER-EDU requires Python 3.9+ with:

- `pyyaml` -- Curriculum configuration loading
- Standard library (`datetime`, `dataclasses`, `enum`)

Optional:

- `geo_infer_space` -- Spatial analysis for interactive exercises
- `geo_infer_data` -- Curated geospatial datasets for learning

## Core Concepts

### Education Levels

GEO-INFER-EDU supports six education levels, each with appropriate content complexity and pedagogical strategies:

| Level | Target | Content Complexity |
|-------|--------|-------------------|
| `ELEMENTARY` | Ages 6-11 | Map reading, basic spatial concepts |
| `MIDDLE_SCHOOL` | Ages 11-14 | Coordinate systems, simple GIS |
| `HIGH_SCHOOL` | Ages 14-18 | Spatial analysis, remote sensing basics |
| `UNDERGRADUATE` | University | GIS, spatial statistics, geodatabases |
| `GRADUATE` | Masters/PhD | Advanced spatial analysis, research methods |
| `PROFESSIONAL` | Practitioners | Applied techniques, industry workflows |

### Pedagogical Approaches

| Approach | Description | Best For |
|----------|------------|---------|
| `CONSTRUCTIVIST` | Learners build knowledge through experience | Conceptual understanding |
| `INQUIRY_BASED` | Question-driven exploration | Scientific reasoning |
| `PROJECT_BASED` | Real-world projects as learning vehicles | Practical skills |
| `COMPETENCY_BASED` | Master specific skills before advancing | Professional certification |
| `EXPERIENTIAL` | Hands-on field and lab work | Technical proficiency |

### Competency Levels

Progress through five levels with increasing independence and complexity:

| Level | Description | Evidence Required |
|-------|------------|------------------|
| `NOT_STARTED` | No exposure to competency | None |
| `EMERGING` | Initial exposure, guided practice | Completion of introductory activities |
| `DEVELOPING` | Building skills, some independence | Passing formative assessments |
| `PROFICIENT` | Consistent independent performance | Passing summative assessments |
| `EXEMPLARY` | Expert-level, can teach others | Portfolio evidence, peer teaching |

## First Example: School Walkability Scores

Compute walkability scores for schools using H3 hexagonal indexing to map walking distances from residential areas.

```python
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class School:
    """Represents a school facility."""
    school_id: str
    name: str
    lat: float
    lng: float
    level: str  # elementary, middle, high
    capacity: int

@dataclass
class ResidentialArea:
    """A residential area with student population."""
    area_id: str
    centroid_lat: float
    centroid_lng: float
    student_population: int
    school_age_children: int

# Define schools
schools = [
    School("sch_001", "Lincoln Elementary", 47.610, -122.335, "elementary", 450),
    School("sch_002", "Washington Middle", 47.615, -122.320, "middle", 600),
    School("sch_003", "Roosevelt High", 47.605, -122.310, "high", 1200),
    School("sch_004", "Jefferson Elementary", 47.620, -122.345, "elementary", 400),
    School("sch_005", "Adams Middle", 47.600, -122.340, "middle", 550),
]

# Define residential areas
areas = [
    ResidentialArea("res_001", 47.612, -122.330, 850, 120),
    ResidentialArea("res_002", 47.608, -122.325, 620, 85),
    ResidentialArea("res_003", 47.618, -122.340, 930, 140),
    ResidentialArea("res_004", 47.602, -122.315, 510, 70),
    ResidentialArea("res_005", 47.614, -122.350, 770, 105),
    ResidentialArea("res_006", 47.606, -122.342, 680, 95),
    ResidentialArea("res_007", 47.622, -122.328, 440, 60),
    ResidentialArea("res_008", 47.598, -122.335, 590, 80),
]

def haversine_km(lat1, lng1, lat2, lng2) -> float:
    """Distance in km between two points."""
    R = 6371.0
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Compute walkability scores
WALK_THRESHOLD_KM = 1.5  # Maximum comfortable walking distance

print("--- School Walkability Analysis ---")
print(f"Walk threshold: {WALK_THRESHOLD_KM} km\n")

for school in schools:
    walkable_population = 0
    total_student_pop = 0
    distances = []

    for area in areas:
        dist = haversine_km(area.centroid_lat, area.centroid_lng, school.lat, school.lng)
        distances.append(dist)
        total_student_pop += area.school_age_children

        if dist <= WALK_THRESHOLD_KM:
            walkable_population += area.school_age_children

    walkability = walkable_population / total_student_pop if total_student_pop > 0 else 0
    avg_dist = sum(distances) / len(distances)

    print(f"{school.name} ({school.level})")
    print(f"  Walkable students: {walkable_population}/{total_student_pop} ({walkability:.1%})")
    print(f"  Average distance: {avg_dist:.2f} km")
    print(f"  Capacity utilization: {walkable_population}/{school.capacity} "
          f"({walkable_population/school.capacity:.1%})")
    print()
```

## Curriculum Design

Create a structured curriculum for teaching geospatial concepts.

```python
from geo_infer_edu.core.curriculum import (
    CurriculumDesigner,
    EducationLevel,
    PedagogicalApproach,
    LearningObjective,
    CurriculumModule,
    Curriculum,
)

designer = CurriculumDesigner(
    education_standard="geospatial_bok",
    pedagogical_approach=PedagogicalApproach.PROJECT_BASED,
)

# Define learning objectives
objectives = [
    LearningObjective(
        id="obj_01",
        description="Explain the purpose and structure of hexagonal spatial indexing systems",
        bloom_level="understand",
        competency_area="spatial_indexing",
        assessment_criteria=["Define H3 resolution levels", "Explain hexagonal vs square grids"],
    ),
    LearningObjective(
        id="obj_02",
        description="Apply H3 indexing to convert point data into hexagonal aggregations",
        bloom_level="apply",
        competency_area="spatial_indexing",
        assessment_criteria=["Use latlng_to_cell for point encoding", "Aggregate data by hex cell"],
        prerequisites=["obj_01"],
    ),
    LearningObjective(
        id="obj_03",
        description="Analyze spatial patterns in hexagonal grid data",
        bloom_level="analyze",
        competency_area="spatial_analysis",
        assessment_criteria=["Identify clusters", "Compute spatial autocorrelation"],
        prerequisites=["obj_02"],
    ),
]

# Create a curriculum module
module = CurriculumModule(
    id="mod_hex_indexing",
    title="Hexagonal Spatial Indexing with H3",
    description="Learn to use H3 hexagonal indexing for spatial data aggregation and analysis",
    learning_objectives=objectives,
    duration_hours=6.0,
    content_sections=[
        {"title": "What is H3?", "duration_minutes": 30},
        {"title": "Resolution and Hierarchy", "duration_minutes": 45},
        {"title": "Point-to-Hex Conversion", "duration_minutes": 60},
        {"title": "Aggregation Techniques", "duration_minutes": 45},
        {"title": "Spatial Pattern Analysis", "duration_minutes": 60},
    ],
)

print(f"Module: {module.title}")
print(f"Duration: {module.duration_hours} hours")
print(f"Objectives: {len(module.learning_objectives)}")
print(f"Content sections: {len(module.content_sections)}")
for section in module.content_sections:
    print(f"  - {section['title']} ({section['duration_minutes']} min)")
```

## Progress Tracking

Track learner progress through competency assessments.

```python
from geo_infer_edu.core.progress import (
    ProgressTracker,
    LearnerActivity,
    CompetencyRecord,
    CompetencyLevel,
    LearnerProgress,
)
from datetime import datetime, timedelta

tracker = ProgressTracker(
    competency_framework="geospatial_bok",
    analytics_level="detailed",
    privacy_compliance="ferpa",
)

# Simulate learner activities
learner_id = "student_042"
base_time = datetime(2024, 1, 15, 9, 0)

activities = [
    LearnerActivity("act_01", "reading", "h3_introduction", base_time,
                     base_time + timedelta(minutes=30), "completed", 0.85, 30, 1),
    LearnerActivity("act_02", "exercise", "h3_point_conversion", base_time + timedelta(days=1),
                     base_time + timedelta(days=1, minutes=45), "completed", 0.72, 45, 2),
    LearnerActivity("act_03", "exercise", "h3_aggregation", base_time + timedelta(days=3),
                     base_time + timedelta(days=3, minutes=60), "completed", 0.91, 60, 1),
    LearnerActivity("act_04", "assessment", "spatial_indexing_quiz", base_time + timedelta(days=5),
                     base_time + timedelta(days=5, minutes=25), "completed", 0.88, 25, 1),
    LearnerActivity("act_05", "video", "h3_resolution_demo", base_time + timedelta(days=2),
                     base_time + timedelta(days=2, minutes=15), "completed", None, 15, 1),
]

# Create learner progress
progress = LearnerProgress(
    learner_id=learner_id,
    activities=activities,
    total_time_hours=sum(a.time_spent_minutes for a in activities) / 60,
    completion_rate=len([a for a in activities if a.completion_status == "completed"]) / len(activities),
)

print(f"\n--- Learner Progress: {learner_id} ---")
print(f"Total activities: {len(progress.activities)}")
print(f"Total time: {progress.total_time_hours:.1f} hours")
print(f"Completion rate: {progress.completion_rate:.1%}")

# Compute competency assessment
scored_activities = [a for a in activities if a.score is not None]
avg_score = sum(a.score for a in scored_activities) / len(scored_activities)
print(f"Average score: {avg_score:.1%}")

if avg_score >= 0.85:
    level = CompetencyLevel.PROFICIENT
elif avg_score >= 0.70:
    level = CompetencyLevel.DEVELOPING
else:
    level = CompetencyLevel.EMERGING

print(f"Competency level: {level.value}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for complete method documentation
- Follow the [Basic Example](examples/basic_example.md) for education access mapping
- Explore the [Advanced Example](examples/advanced_example.md) for education equity analysis
