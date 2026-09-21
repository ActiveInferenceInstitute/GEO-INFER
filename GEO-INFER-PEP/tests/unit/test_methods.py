import pytest

from geo_infer_pep.methods import (
    process_employee_onboarding_workflow,
    generate_quarterly_people_report,
    clear_all_data,
    import_hr_data_from_csv,
    import_crm_data_from_csv,
    import_talent_data_from_csv,
    generate_comprehensive_hr_dashboard,
    generate_comprehensive_crm_dashboard,
    generate_comprehensive_talent_dashboard,
)

# Import the candidate DB so we can populate it directly
import geo_infer_pep.methods as methods_module

from geo_infer_pep.core.data_store import pep_data_manager
from geo_infer_pep.models.hr_models import Employee, EmploymentStatus, Gender
from geo_infer_pep.models.crm_models import Customer


def _make_candidate(candidate_id="cand123_workflow", status="offer_accepted"):
    """Create a real Candidate object and insert into the in-memory DB."""
    from geo_infer_pep.models.talent_models import Candidate, CandidateStatus, Offer
    from datetime import datetime

    status_map = {
        "offer_accepted": CandidateStatus.OFFER_ACCEPTED,
    }

    candidate = Candidate(
        candidate_id=candidate_id,
        first_name="New",
        last_name="Hire",
        email="new.hire@example.com",
        applied_at=datetime.now(),
        status=status_map.get(status, CandidateStatus.OFFER_ACCEPTED),
        offer=Offer(
            offer_id="offer123",
            offered_at=datetime.now().date(),
            accepted_at=datetime.now().date(),
        ),
    )
    return candidate


def test_process_employee_onboarding_workflow_success(caplog):
    """Test the successful run of the onboarding workflow using real candidate DB."""
    clear_all_data()
    candidate = _make_candidate("cand123_workflow")
    methods_module._candidates_db.append(candidate)

    employee_data = {"candidate_id": "cand123_workflow"}
    with caplog.at_level("INFO", logger="geo_infer_pep.methods"):
        result = process_employee_onboarding_workflow(employee_data)
    assert result is True
    assert any(
        "Starting onboarding workflow for candidate cand123_workflow" in r.getMessage()
        for r in caplog.records
    )
    assert any(
        "Onboarding workflow for New Hire" in r.getMessage() for r in caplog.records
    )


def test_onboarding_invokes_benefits_client_with_created_employee():
    """GS-251: a callable benefits_client must be invoked exactly once with
    the created employee record, and onboarding must still succeed."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand251_benefits")
    methods_module._candidates_db.append(candidate)

    received = []
    employee_data = {
        "candidate_id": "cand251_benefits",
        "benefits_client": received.append,
    }

    result = process_employee_onboarding_workflow(employee_data)

    assert result is True
    assert len(received) == 1
    employee = received[0]
    assert employee.employee_id == "emp_cand251_benefits_new_hire"
    assert employee.first_name == candidate.first_name
    assert employee.last_name == candidate.last_name
    assert len(pep_data_manager.employees) == 1


def test_onboarding_invokes_learning_client_with_created_employee():
    """GS-251: a callable learning_client must be invoked exactly once with
    the created employee record, and onboarding must still succeed."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand251_learning")
    methods_module._candidates_db.append(candidate)

    received = []
    employee_data = {
        "candidate_id": "cand251_learning",
        "learning_client": received.append,
    }

    result = process_employee_onboarding_workflow(employee_data)

    assert result is True
    assert len(received) == 1
    employee = received[0]
    assert employee.employee_id == "emp_cand251_learning_new_hire"
    assert employee.first_name == candidate.first_name
    assert employee.last_name == candidate.last_name
    assert len(pep_data_manager.employees) == 1


def test_onboarding_invokes_both_clients_in_order():
    """GS-251: both clients configured together run benefits then learning,
    each with the same created employee record."""
    candidate = _make_candidate("cand251_both")
    methods_module._candidates_db.append(candidate)

    calls = []
    employee_data = {
        "candidate_id": "cand251_both",
        "benefits_client": lambda e: calls.append(("benefits", e)),
        "learning_client": lambda e: calls.append(("learning", e)),
    }

    assert process_employee_onboarding_workflow(employee_data) is True
    assert [name for name, _ in calls] == ["benefits", "learning"]
    assert calls[0][1] is calls[1][1]
    assert calls[0][1].employee_id == "emp_cand251_both_new_hire"


def test_process_employee_onboarding_workflow_candidate_not_found(caplog):
    """Test failure when candidate is not in the DB."""
    clear_all_data()  # Ensure DB is empty

    employee_data = {"candidate_id": "cand_ghost"}
    with caplog.at_level("ERROR", logger="geo_infer_pep.methods"):
        result = process_employee_onboarding_workflow(employee_data)
    assert result is False
    assert any(
        "Candidate cand_ghost not found." in r.getMessage() for r in caplog.records
    )


def test_generate_quarterly_people_report_success(caplog):
    """Test successful generation of the quarterly report."""
    quarter = "Q1"
    year = 2025
    clear_all_data()

    with caplog.at_level("INFO", logger="geo_infer_pep.methods"):
        report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")

    messages = [r.getMessage() for r in caplog.records]
    assert any(
        f"Generating quarterly people report for {quarter} {year}..." in m
        for m in messages
    )
    assert not any("QQ1" in m for m in messages)
    assert any("Quarterly people report generated" in m for m in messages)


def test_generate_quarterly_report_no_data(caplog):
    """Test report generation with no data."""
    quarter = "Q2"
    year = 2025
    clear_all_data()

    with caplog.at_level("INFO", logger="geo_infer_pep.methods"):
        report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")
    assert any(
        f"Generating quarterly people report for {quarter} {year}..." in r.getMessage()
        for r in caplog.records
    )


def test_generate_quarterly_report_normalizes_numeric_quarter(caplog):
    """Test report generation normalizes numeric quarter input."""
    quarter = "3"
    year = 2025
    clear_all_data()

    with caplog.at_level("INFO", logger="geo_infer_pep.methods"):
        report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")

    messages = [r.getMessage() for r in caplog.records]
    assert any(
        f"Generating quarterly people report for Q{quarter} {year}..." in m
        for m in messages
    )
    assert not any("QQ3" in m for m in messages)


def test_onboarding_failure_with_raising_benefits_client_leaves_store_unchanged():
    """GS-249: a failing downstream client must not leave a partial employee
    record in the shared store (the FastAPI layer serves the same list)."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand249_benefits_fail")
    methods_module._candidates_db.append(candidate)

    employee_data = {
        "candidate_id": "cand249_benefits_fail",
        "benefits_client": lambda e: (_ for _ in ()).throw(
            RuntimeError("benefits down")
        ),
    }
    before = len(pep_data_manager.employees)

    result = process_employee_onboarding_workflow(employee_data)

    assert result is False
    assert len(pep_data_manager.employees) == before


def test_onboarding_failure_with_raising_learning_client_leaves_store_unchanged():
    """GS-249: a learning-client failure after successful benefits must also
    abort cleanly with no employee persisted."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand249_learning")
    methods_module._candidates_db.append(candidate)

    employee_data = {
        "candidate_id": "cand249_learning",
        "benefits_client": lambda employee: None,
        "learning_client": lambda e: (_ for _ in ()).throw(
            RuntimeError("learning down")
        ),
    }
    before = len(pep_data_manager.employees)

    result = process_employee_onboarding_workflow(employee_data)

    assert result is False
    assert len(pep_data_manager.employees) == before


def test_onboarding_non_callable_benefits_client_raises_and_leaves_store_unchanged():
    """GS-249: the TypeError guard must escape the broad except (previously it
    was swallowed into return False with the employee already persisted)."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand249_typeerror")
    methods_module._candidates_db.append(candidate)

    employee_data = {
        "candidate_id": "cand249_typeerror",
        "benefits_client": "not-callable",
    }
    before = len(pep_data_manager.employees)

    with pytest.raises(TypeError, match="benefits_client must be callable"):
        process_employee_onboarding_workflow(employee_data)

    assert len(pep_data_manager.employees) == before


def test_onboarding_non_callable_learning_client_raises_and_leaves_store_unchanged():
    """GS-249: a non-callable learning_client must raise TypeError before any
    store mutation, not be swallowed into return False."""
    from geo_infer_pep.core.data_store import pep_data_manager

    clear_all_data()
    candidate = _make_candidate("cand249_typeerror_learning")
    methods_module._candidates_db.append(candidate)

    employee_data = {
        "candidate_id": "cand249_typeerror_learning",
        "learning_client": 42,
    }
    before = len(pep_data_manager.employees)

    with pytest.raises(TypeError, match="learning_client must be callable"):
        process_employee_onboarding_workflow(employee_data)

    assert len(pep_data_manager.employees) == before


# ---------------------------------------------------------------------------
# M7-03: store-backed import + dashboard method coverage
# Every test clears the process-wide store at start AND at end (finally) so no
# data leaks into other tests in the suite.
# ---------------------------------------------------------------------------


def test_import_hr_data_from_csv_round_trip(tmp_path):
    """HR CSV import round-trips one employee through the full pipeline and
    persists it in the shared employee store."""
    clear_all_data()
    try:
        csv_file = tmp_path / "hr.csv"
        csv_file.write_text(
            "employee_id,first_name,last_name,email,hire_date,status,job_title,"
            "department,gender\n"
            "h-1,Ada,Lovelace,ada@example.com,2024-01-15,active,Engineer,"
            "Engineering,female\n",
            encoding="utf-8",
        )

        result = import_hr_data_from_csv(str(csv_file))

        assert isinstance(result, list) and len(result) == 1
        employee = result[0]
        assert isinstance(employee, Employee)
        assert employee.employee_id == "h-1"
        assert employee.department == "Engineering"
        assert employee.employment_status == EmploymentStatus.ACTIVE

        store = pep_data_manager.employees
        assert any(e.employee_id == "h-1" for e in store)
    finally:
        clear_all_data()


def test_import_crm_data_from_csv_round_trip(tmp_path):
    """CRM CSV import round-trips one customer and persists it in the store."""
    clear_all_data()
    try:
        csv_file = tmp_path / "crm.csv"
        csv_file.write_text(
            "id,first_name,last_name,email,phone,company_name,title,lead_source,"
            "status\n"
            "c-1,Grace,Hopper,grace@example.com,555-0100,Acme,CTO,conference,"
            "active\n",
            encoding="utf-8",
        )

        result = import_crm_data_from_csv(str(csv_file))

        assert isinstance(result, list) and len(result) == 1
        customer = result[0]
        assert isinstance(customer, Customer)
        assert customer.customer_id == "c-1"
        assert customer.status == "active"

        store = pep_data_manager.customers
        assert any(c.customer_id == "c-1" for c in store)
    finally:
        clear_all_data()


def test_import_talent_data_from_csv_round_trip(tmp_path):
    """Talent CSV import persists candidates and requisitions and reports the
    post-extend store length for candidates."""
    clear_all_data()
    try:
        candidates_file = tmp_path / "candidates.csv"
        candidates_file.write_text(
            "candidate_id,first_name,last_name,email,status\n"
            "t-1,Alan,Turing,alan@example.com,applied\n",
            encoding="utf-8",
        )
        requisitions_file = tmp_path / "requisitions.csv"
        requisitions_file.write_text(
            "requisition_id,job_title,department,status,opened_at\n"
            "r-1,Engineer,Engineering,open,2026-01-01\n",
            encoding="utf-8",
        )

        result = import_talent_data_from_csv(str(candidates_file), str(requisitions_file))

        assert result["processed_successfully"] is True
        assert result["candidates"] == 1  # post-extend store length (store was cleared)
        assert result["requisitions"] == 1
        assert any(c.candidate_id == "t-1" for c in pep_data_manager.candidates)
        assert any(r.requisition_id == "r-1" for r in pep_data_manager.requisitions)
    finally:
        clear_all_data()


def test_generate_comprehensive_hr_dashboard_empty_and_populated():
    """HR dashboard reports an explicit empty-store message, then full metrics
    for two directly seeded employees."""
    clear_all_data()
    try:
        empty = generate_comprehensive_hr_dashboard()
        assert empty == {"message": "No employee data available for dashboard"}

        pep_data_manager.employees.extend(
            [
                Employee(
                    employee_id="hr-dash-1",
                    first_name="Ada",
                    last_name="Lovelace",
                    email="ada@example.com",
                    gender=Gender.FEMALE,
                    job_title="Engineer",
                    department="Engineering",
                ),
                Employee(
                    employee_id="hr-dash-2",
                    first_name="Alan",
                    last_name="Turing",
                    email="alan@example.com",
                    gender=Gender.MALE,
                    job_title="Engineer",
                    department="Engineering",
                ),
            ]
        )

        data = generate_comprehensive_hr_dashboard()
        assert data["total_employees"] == 2
        assert data["active_employees"] == 2
        assert data["headcount_by_department"] == {"Engineering": 2}
        assert data["headcount_report"]
        assert data["diversity_report"]
        assert data["data_freshness"] == "Based on 2 employee records"
    finally:
        clear_all_data()


def test_generate_comprehensive_crm_dashboard_empty_and_populated():
    """CRM dashboard reports an explicit empty-store message, then metrics for
    one seeded active customer."""
    clear_all_data()
    try:
        empty = generate_comprehensive_crm_dashboard()
        assert empty == {"message": "No customer data available for dashboard"}

        pep_data_manager.customers.append(
            Customer(
                customer_id="crm-dash-1",
                first_name="Grace",
                last_name="Hopper",
                email="grace@example.com",
                status="active",
            )
        )

        data = generate_comprehensive_crm_dashboard()
        assert data["total_customers"] == 1
        assert data["active_customers"] == 1
        assert data["status_breakdown"] == {"active": 1}
        assert data["segmentation_report"]
        assert data["conversion_report"]
        assert data["data_freshness"] == "Based on 1 customer records"
    finally:
        clear_all_data()


def test_generate_comprehensive_talent_dashboard_empty_and_populated():
    """Talent dashboard reports an explicit empty-store message, then metrics
    for one seeded candidate."""
    clear_all_data()
    try:
        empty = generate_comprehensive_talent_dashboard()
        assert empty == {"message": "No candidate data available for dashboard"}

        pep_data_manager.candidates.append(_make_candidate("cand_dash"))

        data = generate_comprehensive_talent_dashboard()
        assert data["total_candidates"] == 1
        assert data["status_breakdown"]
        assert data["pipeline_report"]
        assert data["time_to_hire_report"]
        assert data["data_freshness"] == "Based on 1 candidate records"
    finally:
        clear_all_data()
