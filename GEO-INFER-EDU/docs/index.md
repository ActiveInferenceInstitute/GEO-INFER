# GEO-INFER-EDU Documentation

GEO-INFER-EDU provides geospatial education tools including curriculum design, learning progress tracking, personalized learning paths, and professional development resources. The module supports standards-aligned curriculum generation across multiple education levels and pedagogical approaches.

## Module Overview

GEO-INFER-EDU operates across four functional areas:

1. **Curriculum Design** -- Standards-aligned curriculum generation for geospatial education with learning objectives mapped to Bloom's taxonomy, module sequencing, and assessment design.
2. **Progress Tracking** -- Competency-based learning analytics with activity tracking, gap identification, at-risk learner detection, and FERPA-compliant privacy handling.
3. **Personalization** -- Adaptive learning path generation based on learner profiles, prior knowledge, and learning preferences.
4. **Professional Development** -- Continuing education resources for GIS professionals and spatial data practitioners.

## Core Capabilities

- **Multi-level curriculum design**: Elementary through professional levels with pedagogical approach selection (constructivist, inquiry-based, project-based, competency-based, experiential).
- **Standards alignment**: Maps to geospatial Body of Knowledge (BOK), GISTBOK, and NGSS educational standards.
- **Bloom's taxonomy mapping**: Learning objectives classified across remember, understand, apply, analyze, evaluate, and create cognitive levels.
- **Competency tracking**: Five-level competency progression (not started, emerging, developing, proficient, exemplary) with evidence collection.
- **Learning analytics**: Activity duration tracking, completion rates, score distributions, streak tracking, and at-risk learner identification.
- **Exercise generation**: Interactive geospatial exercises with difficulty scaling and automated assessment.
- **Progress visualization**: Learning trajectory analysis and competency gap identification.

## Integration Points

| Module | Integration |
|--------|------------|
| GEO-INFER-SPACE | Spatial analysis exercises using H3 grids |
| GEO-INFER-DATA | Curated datasets for educational examples |
| GEO-INFER-APP | Web-based learning interfaces and interactive maps |
| GEO-INFER-INTRA | Central documentation system for learning resources |
| GEO-INFER-EXAMPLES | Example-driven learning modules |

## Documentation Contents

- [Getting Started](getting_started.md) -- Installation, core concepts, first curriculum
- [API Reference](api_reference.md) -- Class and method documentation
- [Basic Example: Education Access Mapping](examples/basic_example.md) -- School service area analysis
- [Advanced Example: Education Equity Analysis](examples/advanced_example.md) -- Multi-factor equity index

## Architecture

```
geo_infer_edu/
  core/
    curriculum.py       -- CurriculumDesigner, Curriculum, CurriculumModule
    progress.py         -- ProgressTracker, LearnerProgress, CompetencyRecord
    exercises.py        -- ExerciseGenerator, interactive exercises
    personalization.py  -- PersonalizedPathBuilder, learning path adaptation
    professional.py     -- ProfessionalDevelopment, continuing education
  models/
    education_models.py -- Data models for educational entities
  api/
    endpoints.py        -- REST API for education analytics
  utils/
    standards.py        -- Educational standards mappings
```

## Quick Start

```python
from geo_infer_edu.core.curriculum import (
    CurriculumDesigner,
    EducationLevel,
    PedagogicalApproach,
    LearningObjective,
)

designer = CurriculumDesigner(
    education_standard="geospatial_bok",
    pedagogical_approach=PedagogicalApproach.PROJECT_BASED,
)

# Create a learning objective
objective = LearningObjective(
    id="obj_001",
    description="Apply H3 hexagonal indexing to aggregate point data into spatial bins",
    bloom_level="apply",
    competency_area="spatial_analysis",
    assessment_criteria=[
        "Convert lat/lng points to H3 cells at resolution 8",
        "Aggregate values within each hexagonal cell",
        "Visualize the resulting hexagonal heatmap",
    ],
    prerequisites=["obj_intro_gis", "obj_coordinate_systems"],
)

# Generate a curriculum module
module = designer.create_module(
    title="Spatial Indexing with H3",
    description="Learn hexagonal hierarchical spatial indexing for geospatial analysis",
    objectives=[objective],
    duration_hours=4.0,
)

print(f"Module: {module.title}")
print(f"Duration: {module.duration_hours} hours")
print(f"Objectives: {len(module.learning_objectives)}")
```

## Key Concepts

**Bloom's taxonomy** provides a hierarchical classification of cognitive learning objectives: remember (recall facts), understand (explain concepts), apply (use in new situations), analyze (break into parts), evaluate (make judgments), create (produce new work). Higher levels indicate deeper learning.

**Competency-based assessment** evaluates learners against defined competencies rather than time-in-seat. Each competency has a five-level progression from not started to exemplary, with evidence requirements at each level.

**Geospatial Body of Knowledge (BOK)** defines the core competencies for geospatial professionals, covering spatial thinking, cartography, GIS, remote sensing, and spatial analysis.
