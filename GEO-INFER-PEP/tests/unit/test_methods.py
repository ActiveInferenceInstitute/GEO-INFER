import pytest
from unittest.mock import patch, MagicMock

from geo_infer_pep.methods import (
    process_employee_onboarding_workflow,
    generate_quarterly_people_report
)
# Import the actual reporting functions that methods.py now uses
from geo_infer_pep.reporting import (
    get_hr_quarterly_metrics,
    get_crm_quarterly_metrics,
    get_talent_quarterly_metrics,
    create_quarterly_overview
)

@patch("geo_infer_pep.methods._get_candidate_by_id")
def test_process_employee_onboarding_workflow_success(mock_get_candidate, capsys):
    """Test the successful run of the onboarding workflow with actual calls mocked."""
    from geo_infer_pep.models.talent_models import Candidate, CandidateStatus
    from geo_infer_pep.models.hr_models import Offer
    from datetime import datetime

    employee_data = {"candidate_id": "cand123_workflow"}

    # Create a mock candidate with offer accepted status
    mock_candidate = Candidate(
        candidate_id="cand123_workflow",
        first_name="New",
        last_name="Hire",
        email="new.hire@example.com",
        applied_at=datetime.now(),
        status=CandidateStatus.OFFER_ACCEPTED,
        offer=Offer(
            offer_id="offer123",
            offered_at=datetime.now().date(),
            accepted_at=datetime.now().date()
        )
    )

    mock_get_candidate.return_value = mock_candidate

    result = process_employee_onboarding_workflow(employee_data)
    assert result is True

    captured = capsys.readouterr()
    assert "Starting onboarding workflow for candidate cand123_workflow" in captured.out
    assert "Onboarding workflow for New Hire" in captured.out

    mock_get_candidate.assert_called_once_with("cand123_workflow")

@patch("geo_infer_pep.methods._get_candidate_by_id")
def test_process_employee_onboarding_workflow_candidate_not_found(mock_get_candidate, capsys):
    employee_data = {"candidate_id": "cand_ghost"}
    mock_get_candidate.return_value = None  # Simulate candidate not found

    result = process_employee_onboarding_workflow(employee_data)
    assert result is False
    captured = capsys.readouterr()
    assert "Onboarding Aborted: Candidate cand_ghost not found." in captured.out
    mock_get_candidate.assert_called_once_with("cand_ghost")


def test_generate_quarterly_people_report_success(capsys):
    """Test successful generation of the quarterly report."""
    quarter = "Q1"
    year = 2025

    # Clear any existing data first
    from geo_infer_pep.methods import clear_all_data
    clear_all_data()

    report_path = generate_quarterly_people_report(quarter, year)

    # Should return a path since there are no employees/candidates/customers
    assert report_path.endswith(f"quarterly_report_Q{quarter}_{year}.json")

    captured = capsys.readouterr()
    assert f"Generating quarterly people report for Q{quarter} {year}..." in captured.out
    assert "Quarterly people report generated" in captured.out

def test_generate_quarterly_report_no_data(capsys):
    """Test report generation with no data."""
    quarter = "Q2"
    year = 2025

    # Clear data to ensure no data is available
    from geo_infer_pep.methods import clear_all_data
    clear_all_data()

    report_path = generate_quarterly_people_report(quarter, year)

    # Should still generate a report path even with no data
    assert report_path.endswith(f"quarterly_report_Q{quarter}_{year}.json")

    captured = capsys.readouterr()
    assert f"Generating quarterly people report for Q{quarter} {year}..." in captured.out 