# GEO-INFER-EDU: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-EDU** module provides educational technology capabilities for agents, enabling curriculum design, interactive learning, and competency assessment in geospatial education.

## Agent Capabilities

### 1. Curriculum Design

```python
from geo_infer_edu import CurriculumDesigner

# Design geospatial curriculum
designer = CurriculumDesigner()

curriculum = designer.create(
    topic="spatial_analysis",
    level="intermediate",
    duration_weeks=8,
    learning_outcomes=[
        "Perform buffer analysis",
        "Create spatial joins",
        "Interpret results"
    ])

print(f"Modules: {len(curriculum.modules)}")
print(f"Assessments: {curriculum.assessments}")```

### 2. Interactive Exercises

```python
from geo_infer_edu import ExerciseGenerator

# Generate interactive exercises
generator = ExerciseGenerator()

exercises = generator.create(
    concepts=["coordinate_systems", "projections"],
    format="interactive_map",
    difficulty="progressive",
    auto_feedback=True)

# Start exercise session
session = exercises.start(learner_id="student_001")```

### 3. Progress Tracking

```python
from geo_infer_edu import ProgressTracker

# Track learner progress
tracker = ProgressTracker()

progress = tracker.get_progress(
    learner="student_001",
    course="gis_fundamentals")

print(f"Completion: {progress.completion}%")
print(f"Mastered topics: {progress.mastered}")
print(f"Recommendations: {progress.next_steps}")```

### 4. Adaptive Learning

```python
from geo_infer_edu import AdaptiveLearner

# Personalized learning paths
adaptive = AdaptiveLearner()

path = adaptive.recommend(
    learner_profile=student_profile,
    goal="become_gis_analyst",
    available_time="10_hours_week")

print(f"Recommended path: {path.modules}")
print(f"Estimated completion: {path.weeks} weeks")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Curriculum** | ✅ Ready | Course design |
| **Exercises** | ✅ Ready | Interactive learning |
| **Progress** | ✅ Ready | Competency tracking |
| **Adaptive** | ✅ Ready | Personalization |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **TutorAgent** | 🔮 High | Personal tutor |
| **AssessmentAgent** | 🔮 Medium | Auto-grading |

## Use Cases

### GIS Training Program

```python
from geo_infer_edu import TrainingProgram

program = TrainingProgram(name="GIS Analyst Certification")

program.add_modules([
    "gis_fundamentals",
    "spatial_analysis",
    "remote_sensing"])

program.deploy(platform="online")```

---

This AGENTS.md documents how GEO-INFER-EDU provides educational capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
