"""Tests for the core PEP engine data manager."""
import pytest
from datetime import datetime, date

from geo_infer_pep.core.pep_engine import PEPDataManager
from geo_infer_pep.models.hr_models import Employee, EmploymentStatus


def _make_employee(emp_id: str = "emp-001", dept: str = "Engineering") -> Employee:
    return Employee(
        employee_id=emp_id,
        first_name="John",
        last_name="Doe",
        email=f"{emp_id}@example.com",
        job_title="Engineer",
        department=dept,
        employment_status=EmploymentStatus.ACTIVE,
    )


class TestPEPDataManager:
    def test_init(self):
        mgr = PEPDataManager()
        assert len(mgr._employees) == 0
        assert len(mgr._customers) == 0

    def test_add_employees(self):
        mgr = PEPDataManager()
        employees = [_make_employee("emp-001"), _make_employee("emp-002")]
        count = mgr.add_employees(employees)
        assert count == 2
        assert len(mgr._employees) == 2

    def test_get_employees_no_filter(self):
        mgr = PEPDataManager()
        mgr.add_employees([_make_employee("emp-001"), _make_employee("emp-002")])
        result = mgr.get_employees()
        assert len(result) == 2

    def test_get_employees_filter_department(self):
        mgr = PEPDataManager()
        mgr.add_employees([
            _make_employee("emp-001", "Engineering"),
            _make_employee("emp-002", "Marketing"),
        ])
        result = mgr.get_employees({"department": "Engineering"})
        assert len(result) == 1
        assert result[0].department == "Engineering"

    def test_get_data_summary_empty(self):
        mgr = PEPDataManager()
        summary = mgr.get_data_summary()
        assert summary["employees"]["total"] == 0
        assert summary["customers"]["total"] == 0

    def test_get_data_summary_with_data(self):
        mgr = PEPDataManager()
        mgr.add_employees([_make_employee("emp-001"), _make_employee("emp-002", "Marketing")])
        summary = mgr.get_data_summary()
        assert summary["employees"]["total"] == 2
        assert summary["employees"]["active"] == 2
        assert summary["employees"]["departments"] == 2
