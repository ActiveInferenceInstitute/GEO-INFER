# Data models for GEO-INFER-PEP

from .crm_models import Customer, InteractionLog, Address
from .hr_models import Employee, EmploymentStatus, Gender, Compensation, JobHistoryEntry, PerformanceReview
from .talent_models import (JobRequisition, Candidate, Offer, Interview, InterviewFeedback,
                            JobRequisitionStatus, CandidateStatus, InterviewType)

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
    "InterviewFeedback"
]

