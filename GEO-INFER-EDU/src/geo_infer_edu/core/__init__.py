"""
Core module exports for GEO-INFER-EDU.
"""

from .curriculum import CurriculumDesigner
from .exercises import ExerciseGenerator
from .progress import ProgressTracker
from .personalization import PersonalizedLearning
from .professional import ProfessionalDevelopment

__all__ = [
    "CurriculumDesigner",
    "ExerciseGenerator",
    "ProgressTracker",
    "PersonalizedLearning",
    "ProfessionalDevelopment",
]
