"""Unit tests for PEPValidator validate_* pass/fail paths (GS19-18)."""

from datetime import date, datetime, timedelta

from geo_infer_pep.core.validator import PEPValidator, ValidationResult
from geo_infer_pep.models.crm_models import Customer, InteractionLog
from geo_infer_pep.models.hr_models import Employee, EmploymentStatus
from geo_infer_pep.models.talent_models import (
    Candidate,
    CandidateStatus,
    JobRequisition,
    JobRequisitionStatus,
    Offer,
)

validator = PEPValidator()


def _valid_employee() -> Employee:
    return Employee(
        employee_id="emp-1",
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        phone_number="+1 555 0100",
        hire_date=date.today() - timedelta(days=365),
        job_title="Engineer",
        department="Engineering",
    )


def _valid_customer() -> Customer:
    return Customer(customer_id="cust-1", last_name="Doe", email="doe@example.com")


def _valid_candidate() -> Candidate:
    return Candidate(
        candidate_id="cand-1",
        first_name="Grace",
        last_name="Hopper",
        email="grace@example.com",
        applied_at=datetime.now() - timedelta(days=7),
        skills=["python"],
    )


# --- Employee ------------------------------------------------------------


def test_validate_employee_pass():
    result = validator.validate_employee(_valid_employee())
    assert result.is_valid is True
    assert result.errors == []


def test_validate_employee_missing_required_fields():
    employee = Employee(
        employee_id=" ",
        first_name="",
        last_name="",
        email="",
        job_title="",
        department="",
    )
    result = validator.validate_employee(employee)
    assert result.is_valid is False
    for message in (
        "Employee ID is required",
        "First name is required",
        "Last name is required",
        "Email is required",
        "Job title is required",
        "Department is required",
    ):
        assert message in result.errors
    assert len(result.errors) == 6


def test_validate_employee_rejects_future_hire_date():
    employee = _valid_employee()
    employee.hire_date = date.today() + timedelta(days=1)
    result = validator.validate_employee(employee)
    assert "Hire date cannot be in the future" in result.errors


def test_validate_employee_active_cannot_have_termination_date():
    employee = _valid_employee()
    employee.termination_date = date.today()
    result = validator.validate_employee(employee)
    assert "Active employee cannot have termination date" in result.errors


def test_validate_employee_cannot_be_own_manager():
    employee = _valid_employee()
    employee.manager_id = employee.employee_id
    result = validator.validate_employee(employee)
    assert "Employee cannot be their own manager" in result.errors


def test_validate_employee_rejects_bad_email_and_short_phone():
    employee = _valid_employee()
    employee.email = "not-an-email"
    employee.phone_number = "123"
    result = validator.validate_employee(employee)
    assert "Invalid email format: Invalid email format" in result.errors
    assert "Invalid phone format: Phone number must have 7-15 digits" in result.errors


def test_validate_employee_flags_underage_as_error():
    employee = _valid_employee()
    employee.date_of_birth = date.today() - timedelta(days=10 * 365)
    result = validator.validate_employee(employee)
    assert "Employee appears to be underage (under 14)" in result.errors


def test_validate_employee_terminated_without_date_warns_but_stays_valid():
    employee = _valid_employee()
    employee.employment_status = EmploymentStatus.TERMINATED
    result = validator.validate_employee(employee)
    assert result.is_valid is True
    assert "Terminated employee should have termination date" in result.warnings


def test_validate_employee_strict_mode_turns_warnings_into_errors():
    employee = _valid_employee()
    employee.employment_status = EmploymentStatus.TERMINATED
    result = validator.validate_employee(employee, strict=True)
    assert result.is_valid is False
    assert any(
        error.startswith("Strict mode: Terminated employee should have")
        for error in result.errors
    )


# --- Customer ------------------------------------------------------------


def test_validate_customer_pass():
    result = validator.validate_customer(_valid_customer())
    assert result.is_valid is True
    assert result.errors == []


def test_validate_customer_rejects_unknown_status():
    customer = _valid_customer()
    customer.status = "banana"
    result = validator.validate_customer(customer)
    assert any(error.startswith("Invalid status 'banana'") for error in result.errors)


def test_validate_customer_rejects_unschemed_website():
    customer = _valid_customer()
    customer.website = "example.com"
    result = validator.validate_customer(customer)
    assert "Website URL must start with http:// or https://" in result.errors


def test_validate_customer_rejects_future_created_at():
    customer = _valid_customer()
    customer.created_at = datetime.now() + timedelta(days=1)
    result = validator.validate_customer(customer)
    assert "Created date cannot be in the future" in result.errors


def test_validate_customer_rejects_bad_interactions():
    customer = _valid_customer()
    customer.interaction_history = [
        InteractionLog(
            timestamp=datetime.now() + timedelta(days=1),
            channel="email",
            summary="future contact",
        ),
        InteractionLog(channel="call", summary="  "),
    ]
    result = validator.validate_customer(customer)
    assert "Interaction timestamp cannot be in the future" in result.errors
    assert "Interaction summary cannot be empty" in result.errors


# --- Candidate -----------------------------------------------------------


def test_validate_candidate_pass():
    result = validator.validate_candidate(_valid_candidate())
    assert result.is_valid is True
    assert result.errors == []


def test_validate_candidate_rejects_blank_email_and_bad_links():
    candidate = _valid_candidate()
    candidate.email = " "
    candidate.linkedin_profile = "linkedin.com/in/grace"
    candidate.portfolio_url = "grace.dev"
    result = validator.validate_candidate(candidate)
    assert "Email is required" in result.errors
    assert "LinkedIn profile URL must start with http:// or https://" in result.errors
    assert "Portfolio URL must start with http:// or https://" in result.errors


def test_validate_candidate_rejects_future_application_date():
    candidate = _valid_candidate()
    candidate.applied_at = datetime.now() + timedelta(days=1)
    result = validator.validate_candidate(candidate)
    assert "Application date cannot be in the future" in result.errors


def test_validate_candidate_rejects_empty_skill():
    candidate = _valid_candidate()
    candidate.skills = ["  "]
    result = validator.validate_candidate(candidate)
    assert "Skills cannot be empty strings" in result.errors


def test_validate_candidate_offer_acceptance_before_application():
    candidate = _valid_candidate()
    candidate.status = CandidateStatus.OFFER_ACCEPTED
    candidate.offer = Offer(
        offer_id="offer-1",
        offered_at=date.today() - timedelta(days=10),
        accepted_at=date.today() - timedelta(days=9),
    )
    candidate.applied_at = datetime.now() - timedelta(days=1)
    result = validator.validate_candidate(candidate)
    assert "Offer acceptance date cannot be before application date" in result.errors


def test_validate_candidate_accepted_offer_after_application_passes():
    candidate = _valid_candidate()
    candidate.status = CandidateStatus.OFFER_ACCEPTED
    candidate.offer = Offer(
        offer_id="offer-1",
        offered_at=(datetime.now() - timedelta(days=9)).date(),
        accepted_at=(datetime.now() - timedelta(days=1)).date(),
    )
    result = validator.validate_candidate(candidate)
    assert result.is_valid is True


# --- Job requisition ------------------------------------------------------


def test_validate_job_requisition_pass():
    requisition = JobRequisition(
        requisition_id="req-1",
        job_title="Engineer",
        department="Engineering",
        opened_at=date.today(),
    )
    result = validator.validate_job_requisition(requisition)
    assert result.is_valid is True
    assert result.errors == []


def test_validate_job_requisition_rejects_closed_without_date():
    requisition = JobRequisition(
        requisition_id="req-1",
        job_title="Engineer",
        department="Engineering",
        opened_at=date.today(),
        status=JobRequisitionStatus.CLOSED,
    )
    result = validator.validate_job_requisition(requisition)
    assert result.is_valid is False
    assert "Closed requisition must have closing date" in result.errors


def test_validate_job_requisition_rejects_inverted_salary_and_priority():
    requisition = JobRequisition(
        requisition_id="req-1",
        job_title="Engineer",
        department="Engineering",
        opened_at=date.today(),
        salary_min=100,
        salary_max=50,
        priority="banana",
    )
    result = validator.validate_job_requisition(requisition)
    assert result.is_valid is False
    assert "Minimum salary cannot be greater than maximum salary" in result.errors
    assert any(error.startswith("Invalid priority 'banana'") for error in result.errors)


# --- Workflow and integrity ------------------------------------------------


def _onboarding_ready_candidate() -> Candidate:
    candidate = _valid_candidate()
    candidate.status = CandidateStatus.OFFER_ACCEPTED
    candidate.offer = Offer(
        offer_id="offer-1",
        offered_at=(datetime.now() - timedelta(days=9)).date(),
        accepted_at=(datetime.now() - timedelta(days=1)).date(),
    )
    return candidate


def test_validate_onboarding_workflow_ready_candidate_passes():
    result = validator.validate_onboarding_workflow(
        "cand-1", [_valid_employee()], [_onboarding_ready_candidate()]
    )
    assert result.is_valid is True
    assert result.errors == []


def test_validate_onboarding_workflow_missing_candidate():
    result = validator.validate_onboarding_workflow(
        "ghost", [_valid_employee()], [_onboarding_ready_candidate()]
    )
    assert result.is_valid is False
    assert result.errors == ["candidate ghost not found"]


def test_validate_onboarding_workflow_rejects_existing_employee_email():
    employee = _valid_employee()
    employee.email = "grace@example.com"
    result = validator.validate_onboarding_workflow(
        "cand-1", [employee], [_onboarding_ready_candidate()]
    )
    assert "Employee with email grace@example.com already exists" in result.errors


def test_validate_onboarding_workflow_requires_offer():
    result = validator.validate_onboarding_workflow(
        "cand-1", [_valid_employee()], [_valid_candidate()]
    )
    assert "Candidate must have offer information for onboarding" in result.errors


def test_validate_data_integrity_aggregates_and_cross_references():
    invalid_employee = _valid_employee()
    invalid_employee.email = ""
    results = validator.validate_data_integrity(
        employees=[_valid_employee(), invalid_employee],
        customers=[_valid_customer()],
        candidates=[_onboarding_ready_candidate()],
    )
    assert set(results) == {"employees", "customers", "candidates", "cross_references"}
    assert results["employees"].is_valid is False
    assert results["customers"].is_valid is True
    assert results["candidates"].is_valid is True


def test_validate_data_integrity_flags_duplicate_emails():
    employee = _valid_employee()
    employee.email = "shared@example.com"
    candidate = _valid_candidate()
    candidate.email = "shared@example.com"
    results = validator.validate_data_integrity(
        employees=[employee], candidates=[candidate]
    )
    cross = results["cross_references"]
    assert cross.is_valid is False
    assert any("Duplicate emails" in error for error in cross.errors)


def test_validate_data_integrity_warns_on_unknown_manager():
    employee = _valid_employee()
    employee.manager_id = "ghost-manager"
    results = validator.validate_data_integrity(
        employees=[employee], candidates=[_valid_candidate()]
    )
    cross = results["cross_references"]
    assert cross.is_valid is True
    assert any("non-existent manager" in warning for warning in cross.warnings)


# --- ValidationResult shape ------------------------------------------------


def test_validation_result_add_error_flips_validity():
    result = ValidationResult(True)
    assert result.is_valid is True
    result.add_warning("heads up")
    assert result.is_valid is True
    result.add_error("broke")
    assert result.is_valid is False
    payload = result.to_dict()
    assert payload["is_valid"] is False
    assert payload["errors"] == ["broke"]
    assert payload["warnings"] == ["heads up"]
    assert payload["error_count"] == 1
    assert payload["warning_count"] == 1
    assert "validated_at" in payload
