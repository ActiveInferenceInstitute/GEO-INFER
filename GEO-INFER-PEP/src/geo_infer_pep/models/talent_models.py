"""Talent Acquisition and Management specific data models."""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from enum import Enum

from .hr_models import Employee # For hiring manager, interviewers

class JobRequisitionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    FILLED = "filled"
    CANCELLED = "cancelled"

class CandidateStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class InterviewType(str, Enum):
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    HM_INTERVIEW = "hm_interview"
    FINAL = "final"

class InterviewFeedback(BaseModel):
    interviewer_id: str # Could be Employee ID
    interviewer_name: Optional[str] = None # Denormalized for convenience
    rating: Optional[float] = None # e.g., 1-5 scale
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    notes: Optional[str] = None
    recommend_hire: Optional[bool] = None
    feedback_submitted_at: datetime = Field(default_factory=datetime.now)

class Interview(BaseModel):
    interview_id: str
    interview_type: InterviewType
    scheduled_at: datetime
    interviewers: List[str] # List of Employee IDs
    feedback: List[InterviewFeedback] = []
    status: str = "scheduled" # e.g., scheduled, completed, cancelled

class Offer(BaseModel):
    offer_id: str
    offered_at: date
    expires_at: Optional[date] = None
    salary_offered: Optional[float] = None
    currency: Optional[str] = "USD"
    bonus_offered: Optional[float] = None
    stock_options_offered: Optional[int] = None
    start_date_proposed: Optional[date] = None
    status: str = "pending" # e.g., pending, accepted, declined, rescinded
    accepted_at: Optional[date] = None
    declined_at: Optional[date] = None

class Candidate(BaseModel):
    candidate_id: str = Field(..., description="Unique identifier for the candidate")
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    linkedin_profile: Optional[HttpUrl] = None
    resume_url: Optional[HttpUrl] = None # Or store as blob/file path
    portfolio_url: Optional[HttpUrl] = None
    source: Optional[str] = None # e.g., "LinkedIn", "Referral", "Careers Page"
    applied_at: datetime = Field(default_factory=datetime.now)
    status: CandidateStatus = CandidateStatus.APPLIED
    job_requisition_id: Optional[str] = None # Link to JobRequisition
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    skills: List[str] = []
    interviews: List[Interview] = []
    offer: Optional[Offer] = None
    notes: Optional[str] = None
    tags: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.now)

class JobRequisition(BaseModel):
    requisition_id: str = Field(..., description="Unique identifier for the job requisition")
    job_title: str
    department: str
    location: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    qualifications: Optional[List[str]] = None
    status: JobRequisitionStatus = JobRequisitionStatus.OPEN
    opened_at: date
    closed_at: Optional[date] = None
    hiring_manager_id: Optional[str] = None # Employee ID
    priority: Optional[str] = "medium" # e.g., high, medium, low
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "USD"
    candidates: List[Candidate] = [] # Candidates associated with this req
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 