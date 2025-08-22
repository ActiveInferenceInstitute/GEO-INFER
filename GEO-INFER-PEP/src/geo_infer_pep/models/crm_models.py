"""CRM specific data models."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class InteractionLog(BaseModel):
    timestamp: datetime = datetime.now()
    channel: str # e.g., "email", "call", "meeting"
    summary: str
    agent_id: Optional[str] = None

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Customer(BaseModel):
    customer_id: str
    first_name: Optional[str] = None
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[Address] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    source: Optional[str] = None # e.g., "website_form", "referral", "cold_outreach"
    status: Optional[str] = "active" # e.g., "lead", "active_customer", "churned"
    tags: List[str] = []
    interaction_history: List[InteractionLog] = []
    website: Optional[str] = None
    linkedin_profile: Optional[str] = None
    notes: Optional[str] = None 