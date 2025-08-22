"""HR specific data models."""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum

class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    PENDING_HIRE = "pending_hire"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"

class Compensation(BaseModel):
    salary: float
    currency: str = "USD"
    pay_frequency: str # e.g., "annual", "monthly", "hourly"
    bonus_potential: Optional[float] = None
    stock_options: Optional[int] = None

class JobHistoryEntry(BaseModel):
    job_title: str
    department: str
    start_date: date
    end_date: Optional[date] = None
    manager_id: Optional[str] = None # Employee ID of the manager
    is_current: bool = False

class PerformanceReview(BaseModel):
    review_id: str
    review_date: date
    reviewer_id: str # Employee ID of the reviewer
    overall_rating: float # e.g., on a scale of 1-5
    comments: Optional[str] = None
    goals_set: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None

class Employee(BaseModel):
    employee_id: str = Field(..., description="Unique identifier for the employee")
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: str
    personal_email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    nationality: Optional[str] = None
    
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    job_title: str
    department: str
    manager_id: Optional[str] = None # Employee ID of the direct manager
    location: Optional[str] = None # e.g., Office name, "Remote"
    
    compensation: Optional[Compensation] = None
    job_history: List[JobHistoryEntry] = []
    performance_reviews: List[PerformanceReview] = []
    
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    custom_fields: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    # Add other HR-related models like:
    # - Department
    # - LeaveRequest
    # - TrainingRecord
    # - BenefitEnrollment

    # Add other HR-related models like:
    # - Department
    # - LeaveRequest
    # - TrainingRecord
    # - BenefitEnrollment 