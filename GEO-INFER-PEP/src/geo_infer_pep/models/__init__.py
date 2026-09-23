# Data models for GEO-INFER-PEP

from .crm_models import Customer, InteractionLog, Address
from .hr_models import (
    Employee,
    EmploymentStatus,
    Gender,
    Compensation,
    JobHistoryEntry,
    PerformanceReview,
)
from .talent_models import (
    JobRequisition,
    Candidate,
    Offer,
    Interview,
    InterviewFeedback,
    JobRequisitionStatus,
    CandidateStatus,
    InterviewType,
)
from .learning_models import LearningCourse, LearningEnrollment
from .conflict_models import ConflictCase
from .survey_models import Survey, SurveyResponse

__all__ = [
    # CRM Models
    "Customer",
    "InteractionLog",
    "Address",
    # HR Models
    "Employee",
    "EmploymentStatus",
    "Gender",
    "Compensation",
    "JobHistoryEntry",
    "PerformanceReview",
    # Talent Models
    "JobRequisition",
    "JobRequisitionStatus",
    "Candidate",
    "CandidateStatus",
    "Offer",
    "Interview",
    "InterviewType",
    # Learning & Development Models
    "LearningCourse",
    "LearningEnrollment",
    # Conflict Resolution Models
    "ConflictCase",
    # Survey Models
    "Survey",
    "SurveyResponse",
]
