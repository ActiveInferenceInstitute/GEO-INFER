"""Learning & Development data models."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LearningCourse(BaseModel):
    """A learning & development course offered to employees."""

    course_id: str = Field(..., description="Unique identifier for the course")
    title: str
    description: Optional[str] = None
    category: Optional[str] = None  # e.g., "compliance", "technical", "leadership"
    provider: Optional[str] = None
    duration_hours: Optional[float] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class LearningEnrollment(BaseModel):
    """An employee enrollment in a learning course."""

    enrollment_id: str = Field(..., description="Unique identifier for the enrollment")
    employee_id: str  # Employee ID of the enrolled employee
    course_id: str  # LearningCourse ID
    status: str = "enrolled"  # e.g., "enrolled", "completed", "dropped"
    enrolled_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    notes: Optional[str] = None
