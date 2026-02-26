---
title: "GEO-INFER-EDU: Geospatial Educational Technology"
description: "Geospatial education, curriculum development, and learning experiences"
purpose: "Provide educational tools for geospatial learning, interactive exercises, and professional development"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "DATA", "APP", "EXAMPLES"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-DATA", "GEO-INFER-APP", "GEO-INFER-EXAMPLES"]
tags: ["education", "learning", "curriculum", "training", "gis-education"]
difficulty: "Beginner"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-EDU: Geospatial Educational Technology

## Overview

**GEO-INFER-EDU** provides comprehensive educational technology capabilities for geospatial learning. The module supports:

- **Curriculum Development**: Standards-aligned geospatial curriculum design
- **Interactive Learning**: Hands-on exercises with real spatial data
- **Progress Tracking**: Learning analytics and competency assessment
- **Professional Development**: Continuing education for GIS professionals
- **Personalized Learning**: Adaptive learning paths based on learner progress

## Features

### Curriculum Design

```python
from geo_infer_edu import CurriculumDesigner

# Design a geospatial curriculum
designer = CurriculumDesigner()

curriculum = designer.design(
    topic="geospatial_analysis",
    level="intermediate",
    duration="8_weeks",
    standards=["NCGE", "ISTE"],
    learning_outcomes=[
        "Perform spatial analysis",
        "Create thematic maps",
        "Analyze remote sensing data"
    ]
)

# Generate learning modules
modules = curriculum.generate_modules()
print(f"Created {len(modules)} learning modules")
```

### Interactive Exercises

```python
from geo_infer_edu import InteractiveExerciseGenerator

# Create interactive learning activities
generator = InteractiveExerciseGenerator()

exercises = generator.create(
    concepts=["spatial_analysis", "remote_sensing", "geostatistics"],
    format="interactive_map",
    difficulty="progressive",
    feedback="immediate"
)

# Launch exercise
exercise = exercises[0]
exercise.start(learner_id="student_001")
```

### Progress Tracking

```python
from geo_infer_edu import ProgressTracker

# Track learner progress
tracker = ProgressTracker()

progress = tracker.assess(
    learner=student_id,
    competencies=[
        "data_collection",
        "spatial_analysis",
        "visualization",
        "interpretation"
    ]
)

print(f"Overall progress: {progress.completion_percentage}%")
print(f"Mastered: {progress.mastered_competencies}")
print(f"Needs work: {progress.areas_for_improvement}")
```

### Resource Recommendations

```python
from geo_infer_edu import ResourceRecommender

# Get personalized learning recommendations
recommender = ResourceRecommender()

recommendations = recommender.suggest(
    learner_profile=learner,
    current_topic="geostatistics",
    learning_style="visual",
    time_available="30_minutes"
)

for rec in recommendations:
    print(f"{rec.title}: {rec.type} - {rec.estimated_time}")
```

## Learning Modules

### GIS Fundamentals

| Module | Topics | Duration | Level |
|--------|--------|----------|-------|
| **Spatial Thinking** | Coordinate systems, projections | 2 hours | Beginner |
| **Data Types** | Vector, raster, point clouds | 3 hours | Beginner |
| **Map Design** | Cartography, symbology | 2 hours | Beginner |

### Spatial Analysis

| Module | Topics | Duration | Level |
|--------|--------|----------|-------|
| **Overlay Analysis** | Intersect, union, buffer | 3 hours | Intermediate |
| **Network Analysis** | Routing, service areas | 4 hours | Intermediate |
| **Geostatistics** | Interpolation, kriging | 5 hours | Advanced |

### Remote Sensing

| Module | Topics | Duration | Level |
|--------|--------|----------|-------|
| **Image Interpretation** | Visual analysis, band combinations | 3 hours | Beginner |
| **Classification** | Supervised, unsupervised methods | 4 hours | Intermediate |
| **Change Detection** | Multi-temporal analysis | 4 hours | Advanced |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-APP** | Interactive learning interfaces |
| **GEO-INFER-EXAMPLES** | Sample datasets and tutorials |
| **GEO-INFER-SPACE** | Core spatial concepts for teaching |
| **GEO-INFER-DATA** | Educational dataset management |
| **GEO-INFER-COG** | Cognitive learning models |

## Installation

```bash
# Install the education module
uv pip install -e "./GEO-INFER-EDU"

# Install with all dependencies
uv pip install -e "./GEO-INFER-EDU[full]"
```

## Use Cases

### 1. University GIS Course

```python
from geo_infer_edu import CourseManager

# Set up a university course
course = CourseManager(
    name="Introduction to GIS",
    institution="geo_university",
    semester="fall_2026"
)

# Add students
course.enroll_students(student_roster)

# Assign modules
course.assign_module("spatial_thinking", due_date="2026-02-15")
course.assign_module("data_types", due_date="2026-03-01")

# Track class progress
class_progress = course.get_class_progress()
```

### 2. Professional Workshop

```python
from geo_infer_edu import WorkshopManager

# Create professional development workshop
workshop = WorkshopManager(
    title="Advanced Spatial Analysis",
    duration="2_days",
    target_audience="GIS Analysts"
)

# Add hands-on exercises
workshop.add_exercise("network_analysis_practical")
workshop.add_exercise("spatial_statistics_lab")

# Generate certificates
workshop.generate_certificates(participants)
```

## Related Documentation

- [GEO-INFER-EXAMPLES](../GEO-INFER-EXAMPLES/README.md): Example datasets
- [GEO-INFER-APP](../GEO-INFER-APP/README.md): User interfaces
- [AGENTS.md](./AGENTS.md): Educational agent capabilities

---

**Status**: Alpha - Core functionality implemented

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
