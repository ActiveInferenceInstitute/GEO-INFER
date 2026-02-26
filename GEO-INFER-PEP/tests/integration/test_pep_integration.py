"""
Integration tests for GEO-INFER-PEP: PEP engine and data manager pipeline.

Tests PEPDataManager and PEPEngine working together for employee management,
data storage, health checks, and system lifecycle operations.
"""

import pytest
from datetime import date, datetime

pytestmark = [pytest.mark.integration]


@pytest.fixture
def employees():
    """Create test employee data."""
    from geo_infer_pep.models.hr_models import Employee, EmploymentStatus, Compensation

    return [
        Employee(
            employee_id="EMP001",
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Senior Engineer",
            department="Engineering",
            hire_date=date(2020, 3, 15),
            compensation=Compensation(salary=150000, currency="USD", pay_frequency="annual"),
        ),
        Employee(
            employee_id="EMP002",
            first_name="Bob",
            last_name="Smith",
            email="bob.smith@example.com",
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Product Manager",
            department="Product",
            hire_date=date(2021, 7, 1),
            compensation=Compensation(salary=130000, currency="USD", pay_frequency="annual"),
        ),
        Employee(
            employee_id="EMP003",
            first_name="Carol",
            last_name="Davis",
            email="carol.davis@example.com",
            employment_status=EmploymentStatus.ON_LEAVE,
            job_title="Data Scientist",
            department="Engineering",
            hire_date=date(2019, 1, 10),
        ),
        Employee(
            employee_id="EMP004",
            first_name="David",
            last_name="Wilson",
            email="david.wilson@example.com",
            employment_status=EmploymentStatus.TERMINATED,
            job_title="QA Engineer",
            department="Engineering",
            hire_date=date(2018, 6, 20),
            termination_date=date(2024, 12, 31),
        ),
    ]


class TestPEPDataManager:
    """Test PEPDataManager data operations."""

    def test_add_and_retrieve_employees(self, employees):
        """Test adding employees and retrieving them."""
        from geo_infer_pep.core.pep_engine import PEPDataManager

        manager = PEPDataManager()
        count = manager.add_employees(employees)
        assert count == 4

        all_emps = manager.get_employees()
        assert len(all_emps) == 4

    def test_filter_employees_by_department(self, employees):
        """Test filtering employees by department."""
        from geo_infer_pep.core.pep_engine import PEPDataManager

        manager = PEPDataManager()
        manager.add_employees(employees)

        eng_emps = manager.get_employees(filters={"department": "Engineering"})
        assert len(eng_emps) == 3  # Alice, Carol, David

        prod_emps = manager.get_employees(filters={"department": "Product"})
        assert len(prod_emps) == 1
        assert prod_emps[0].first_name == "Bob"

    def test_filter_employees_by_status(self, employees):
        """Test filtering employees by employment status."""
        from geo_infer_pep.core.pep_engine import PEPDataManager

        manager = PEPDataManager()
        manager.add_employees(employees)

        active_emps = manager.get_employees(filters={"status": "active"})
        assert len(active_emps) == 2
        assert all(e.employment_status.value == "active" for e in active_emps)

    def test_data_summary(self, employees):
        """Test data summary generation."""
        from geo_infer_pep.core.pep_engine import PEPDataManager

        manager = PEPDataManager()
        manager.add_employees(employees)

        summary = manager.get_data_summary()
        assert summary["employees"]["total"] == 4
        assert summary["employees"]["active"] == 2
        assert summary["employees"]["departments"] == 2  # Engineering, Product
        assert summary["customers"]["total"] == 0
        assert summary["candidates"]["total"] == 0
        assert "last_updated" in summary

    def test_clear_all_data(self, employees):
        """Test clearing all data from the store."""
        from geo_infer_pep.core.pep_engine import PEPDataManager

        manager = PEPDataManager()
        manager.add_employees(employees)
        assert len(manager.get_employees()) == 4

        result = manager.clear_all_data()
        assert result is True
        assert len(manager.get_employees()) == 0


class TestPEPEngine:
    """Test PEPEngine orchestration."""

    def test_engine_initialization(self):
        """Test engine initialization lifecycle."""
        from geo_infer_pep.core.pep_engine import PEPEngine

        engine = PEPEngine()
        assert engine._initialized is False

        result = engine.initialize()
        assert result is True
        assert engine._initialized is True

        # Double initialization should return True without error
        result2 = engine.initialize()
        assert result2 is True

    def test_engine_system_status(self, employees):
        """Test system status reporting."""
        from geo_infer_pep.core.pep_engine import PEPEngine

        engine = PEPEngine()
        engine.initialize()
        engine.data_manager.add_employees(employees)

        status = engine.get_system_status()
        assert status["system_status"] == "operational"
        assert status["initialized"] is True
        assert status["data_summary"]["employees"]["total"] == 4
        assert "engine_version" in status

    def test_engine_health_check(self):
        """Test comprehensive health check."""
        from geo_infer_pep.core.pep_engine import PEPEngine

        engine = PEPEngine()
        engine.initialize()

        health = engine.run_health_check()
        assert health["overall_health"] == "healthy"
        assert "data_integrity" in health["checks"]
        assert "dependencies" in health["checks"]
        assert "data_processing" in health["checks"]
        assert health["checks"]["data_integrity"]["status"] == "healthy"
        assert health["checks"]["dependencies"]["status"] == "healthy"

    def test_engine_shutdown(self, employees):
        """Test graceful shutdown."""
        from geo_infer_pep.core.pep_engine import PEPEngine

        engine = PEPEngine()
        engine.initialize()
        engine.data_manager.add_employees(employees)
        assert len(engine.data_manager.get_employees()) > 0

        result = engine.shutdown()
        assert result is True
        assert engine._initialized is False
        assert len(engine.data_manager.get_employees()) == 0


class TestPEPEngineWithDataManager:
    """Test PEPEngine and PEPDataManager working together."""

    def test_shared_data_manager(self, employees):
        """Test that engine and data manager share state."""
        from geo_infer_pep.core.pep_engine import PEPEngine, PEPDataManager

        manager = PEPDataManager()
        engine = PEPEngine(data_manager=manager)
        engine.initialize()

        # Add employees via manager
        manager.add_employees(employees)

        # Engine should see the data
        status = engine.get_system_status()
        assert status["data_summary"]["employees"]["total"] == 4

        # Shutdown via engine should clear manager data
        engine.shutdown()
        assert len(manager.get_employees()) == 0

    def test_full_lifecycle(self, employees):
        """Test full engine lifecycle: init -> load -> query -> status -> shutdown."""
        from geo_infer_pep.core.pep_engine import PEPEngine

        # Initialize
        engine = PEPEngine()
        engine.initialize()

        # Load data
        engine.data_manager.add_employees(employees)

        # Query
        eng_team = engine.data_manager.get_employees(filters={"department": "Engineering"})
        assert len(eng_team) == 3

        # Check status
        status = engine.get_system_status()
        assert status["initialized"] is True
        assert status["data_summary"]["employees"]["total"] == 4

        # Health check
        health = engine.run_health_check()
        assert health["overall_health"] == "healthy"

        # Shutdown
        engine.shutdown()
        assert engine._initialized is False


class TestEmployeeModel:
    """Test Employee model properties and operations."""

    def test_employee_full_name(self):
        """Test employee full_name property."""
        from geo_infer_pep.models.hr_models import Employee, EmploymentStatus

        emp = Employee(
            employee_id="E100",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@test.com",
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Analyst",
            department="Finance",
        )
        assert emp.full_name == "Jane Doe"

    def test_employee_serialization(self, employees):
        """Test employee model serialization to dict."""
        emp = employees[0]
        data = emp.model_dump()

        assert data["employee_id"] == "EMP001"
        assert data["first_name"] == "Alice"
        assert data["department"] == "Engineering"
        assert data["employment_status"] == "active"
        assert data["compensation"]["salary"] == 150000

    def test_employee_with_job_history(self):
        """Test employee with job history entries."""
        from geo_infer_pep.models.hr_models import (
            Employee, EmploymentStatus, JobHistoryEntry,
        )

        emp = Employee(
            employee_id="E200",
            first_name="Test",
            last_name="User",
            email="test@test.com",
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Director",
            department="Operations",
            job_history=[
                JobHistoryEntry(
                    job_title="Manager",
                    department="Operations",
                    start_date=date(2020, 1, 1),
                    end_date=date(2023, 12, 31),
                ),
                JobHistoryEntry(
                    job_title="Director",
                    department="Operations",
                    start_date=date(2024, 1, 1),
                    is_current=True,
                ),
            ],
        )

        assert len(emp.job_history) == 2
        assert emp.job_history[1].is_current is True
