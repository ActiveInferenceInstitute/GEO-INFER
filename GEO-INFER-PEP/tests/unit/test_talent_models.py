"""Tests for PEP talent/recruitment data models."""
import pytest
from datetime import date

from geo_infer_pep.models.talent_models import (
    Candidate,
    JobRequisition,
    CandidateStatus,
    JobRequisitionStatus,
)


class TestCandidate:
    def test_create_candidate(self):
        candidate = Candidate(
            candidate_id="cand-001",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            status=CandidateStatus.APPLIED,
        )
        assert candidate.candidate_id == "cand-001"
        assert candidate.status == CandidateStatus.APPLIED

    def test_candidate_with_requisition(self):
        candidate = Candidate(
            candidate_id="cand-002",
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            status=CandidateStatus.SCREENING,
            job_requisition_id="req-001",
        )
        assert candidate.job_requisition_id == "req-001"


class TestCandidateStatus:
    def test_status_values(self):
        assert CandidateStatus.APPLIED.value == "applied"
        assert CandidateStatus.SCREENING.value == "screening"
        assert CandidateStatus.INTERVIEWING.value == "interviewing"
        assert CandidateStatus.HIRED.value == "hired"
        assert CandidateStatus.REJECTED.value == "rejected"


class TestJobRequisition:
    def test_create_requisition(self):
        req = JobRequisition(
            requisition_id="req-001",
            job_title="Senior Engineer",
            department="Engineering",
            opened_at=date.today(),
            status=JobRequisitionStatus.OPEN,
        )
        assert req.requisition_id == "req-001"
        assert req.job_title == "Senior Engineer"
        assert req.status == JobRequisitionStatus.OPEN

    def test_requisition_status_values(self):
        assert JobRequisitionStatus.OPEN.value == "open"
        assert JobRequisitionStatus.CLOSED.value == "closed"
        assert JobRequisitionStatus.FILLED.value == "filled"
