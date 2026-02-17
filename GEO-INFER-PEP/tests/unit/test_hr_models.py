"""Tests for PEP HR data models."""
import pytest
from datetime import date

from geo_infer_pep.models.hr_models import (
    Employee,
    EmploymentStatus,
    Gender,
    Compensation,
    JobHistoryEntry,
    PerformanceReview,
)


class TestEmployee:
    def test_create_employee(self):
        emp = Employee(
            employee_id="emp-001",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            job_title="Senior Engineer",
            department="Engineering",
        )
        assert emp.employee_id == "emp-001"
        assert emp.employment_status == EmploymentStatus.ACTIVE

    def test_full_name(self):
        emp = Employee(
            employee_id="emp-002",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            job_title="Manager",
            department="Sales",
        )
        assert emp.full_name == "John Doe"

    def test_employee_with_compensation(self):
        comp = Compensation(
            salary=120000.0,
            currency="USD",
            pay_frequency="annual",
            bonus_potential=15000.0,
        )
        emp = Employee(
            employee_id="emp-003",
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            job_title="Director",
            department="Product",
            compensation=comp,
        )
        assert emp.compensation.salary == 120000.0

    def test_employee_with_gender(self):
        emp = Employee(
            employee_id="emp-004",
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com",
            job_title="Analyst",
            department="Finance",
            gender=Gender.MALE,
        )
        assert emp.gender == Gender.MALE


class TestEmploymentStatus:
    def test_active(self):
        assert EmploymentStatus.ACTIVE.value == "active"

    def test_terminated(self):
        assert EmploymentStatus.TERMINATED.value == "terminated"

    def test_on_leave(self):
        assert EmploymentStatus.ON_LEAVE.value == "on_leave"


class TestJobHistoryEntry:
    def test_create_entry(self):
        entry = JobHistoryEntry(
            job_title="Engineer",
            department="Engineering",
            start_date=date(2020, 1, 15),
            is_current=True,
        )
        assert entry.job_title == "Engineer"
        assert entry.is_current is True

    def test_past_entry(self):
        entry = JobHistoryEntry(
            job_title="Intern",
            department="R&D",
            start_date=date(2019, 6, 1),
            end_date=date(2019, 12, 31),
            is_current=False,
        )
        assert entry.end_date is not None
        assert entry.is_current is False


class TestPerformanceReview:
    def test_create_review(self):
        review = PerformanceReview(
            review_id="rev-001",
            review_date=date(2024, 12, 15),
            reviewer_id="emp-manager",
            overall_rating=4.5,
            comments="Excellent performance",
        )
        assert review.overall_rating == 4.5
        assert review.comments == "Excellent performance"
