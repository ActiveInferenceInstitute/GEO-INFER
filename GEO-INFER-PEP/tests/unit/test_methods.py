from geo_infer_pep.methods import (
    process_employee_onboarding_workflow,
    generate_quarterly_people_report,
    clear_all_data,
)

# Import the candidate DB so we can populate it directly
import geo_infer_pep.methods as methods_module


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


def test_process_employee_onboarding_workflow_success(capsys):
    """Test the successful run of the onboarding workflow using real candidate DB."""
    clear_all_data()
    candidate = _make_candidate("cand123_workflow")
    methods_module._candidates_db.append(candidate)

    employee_data = {"candidate_id": "cand123_workflow"}
    result = process_employee_onboarding_workflow(employee_data)
    assert result is True

    captured = capsys.readouterr()
    assert "Starting onboarding workflow for candidate cand123_workflow" in captured.out
    assert "Onboarding workflow for New Hire" in captured.out


def test_process_employee_onboarding_workflow_candidate_not_found(capsys):
    """Test failure when candidate is not in the DB."""
    clear_all_data()  # Ensure DB is empty

    employee_data = {"candidate_id": "cand_ghost"}
    result = process_employee_onboarding_workflow(employee_data)
    assert result is False

    captured = capsys.readouterr()
    assert "Onboarding Aborted: Candidate cand_ghost not found." in captured.out


def test_generate_quarterly_people_report_success(capsys):
    """Test successful generation of the quarterly report."""
    quarter = "Q1"
    year = 2025
    clear_all_data()

    report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")

    captured = capsys.readouterr()
    assert f"Generating quarterly people report for {quarter} {year}..." in captured.out
    assert "QQ1" not in captured.out
    assert "Quarterly people report generated" in captured.out


def test_generate_quarterly_report_no_data(capsys):
    """Test report generation with no data."""
    quarter = "Q2"
    year = 2025
    clear_all_data()

    report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")

    captured = capsys.readouterr()
    assert f"Generating quarterly people report for {quarter} {year}..." in captured.out


def test_generate_quarterly_report_normalizes_numeric_quarter(capsys):
    """Test report generation normalizes numeric quarter input."""
    quarter = "3"
    year = 2025
    clear_all_data()

    report_path = generate_quarterly_people_report(quarter, year)

    assert report_path.endswith(".json")

    captured = capsys.readouterr()
    assert (
        f"Generating quarterly people report for Q{quarter} {year}..." in captured.out
    )
    assert "QQ3" not in captured.out
