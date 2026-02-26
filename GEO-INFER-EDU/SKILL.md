---
name: geo-infer-edu
description: Educational technology for geospatial learning. Use when creating spatial analysis curricula, interactive GIS exercises, learning progression models, competency assessment for geographic concepts, or step-by-step spatial tutorials.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-EDU

## Instructions

### Core Capabilities

- **Curriculum design**: Learning progression modeling for GIS competencies
- **Exercises**: Interactive spatial analysis exercises (template-based with student code)
- **Assessment**: Competency evaluation and skill gap analysis
- **Tutorials**: Step-by-step guided spatial analysis workflows with checkpoints

### Key Imports

```python
from geo_infer_edu.core.curriculum import CurriculumDesigner
from geo_infer_edu.core.exercises import ExerciseGenerator
from geo_infer_edu.core.assessment import CompetencyAssessor
from geo_infer_edu.core.tutorials import TutorialBuilder
```

## Examples

```python
from geo_infer_edu.core.exercises import ExerciseGenerator

generator = ExerciseGenerator(difficulty="intermediate")
exercise = generator.create(
    topic="spatial_autocorrelation",
    dataset="crime_data",
    expected_tool="MoranI"
)
# Students fill in the `pass` block in the generated template
```

## Guidelines

- `exercises.py` contains a `pass` inside a template string for student exercises — this is not production code, it is intentional

### Integrations

- Integrates with MATH for spatial statistics exercises
- Integrates with SPACE for H3 indexing tutorials
- Test: `uv run python -m pytest GEO-INFER-EDU/tests/ -v`
