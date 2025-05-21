import pytest
from unittest.mock import patch, MagicMock

from geo_infer_pep.methods import (
    process_employee_onboarding_workflow,
    generate_quarterly_people_report,
    # Import the placeholder instances to allow mocking their methods
    talent_module as methods_talent_module,
    hr_module as methods_hr_module,
    benefits_module as methods_benefits_module,
    training_module as methods_training_module
)
# Import the actual reporting functions that methods.py now uses
from geo_infer_pep.reporting import (
    get_hr_quarterly_metrics,
    get_crm_quarterly_metrics,
    get_talent_quarterly_metrics,
    create_quarterly_overview
)

@patch("geo_infer_pep.methods.training_module.schedule_onboarding_sessions")
@patch("geo_infer_pep.methods.benefits_module.initiate_enrollment")
@patch("geo_infer_pep.methods.hr_module.create_employee")
@patch("geo_infer_pep.methods.talent_module.get_candidate_by_id")
def test_process_employee_onboarding_workflow_success(
    mock_get_candidate, mock_create_hr_record, 
    mock_initiate_benefits, mock_schedule_training, capsys
):
    """Test the successful run of the onboarding workflow with actual calls mocked."""
    employee_data = {"name": "New Hire Full Name", "candidate_id": "cand123_workflow"}
    
    mock_get_candidate.return_value = {"candidate_id": "cand123_workflow", "name": "New Hire Full Name", "status": "Offer Accepted", "email": "new.hire@example.com"}
    mock_create_hr_record.return_value = {"employee_id": "emp_newhirefullname", "status": "active"}
    mock_initiate_benefits.return_value = True
    mock_schedule_training.return_value = True

    result = process_employee_onboarding_workflow(employee_data)
    assert result is True
    
    captured = capsys.readouterr()
    assert "Starting onboarding workflow for New Hire Full Name" in captured.out
    assert "Onboarding workflow for New Hire Full Name (employee ID: emp_newhirefullname) completed." in captured.out
    
    mock_get_candidate.assert_called_once_with("cand123_workflow")
    mock_create_hr_record.assert_called_once_with(employee_data)
    mock_initiate_benefits.assert_called_once_with("emp_newhirefullname")
    mock_schedule_training.assert_called_once_with("emp_newhirefullname")

@patch("geo_infer_pep.methods.talent_module.get_candidate_by_id")
def test_process_employee_onboarding_workflow_candidate_not_found(mock_get_candidate, capsys):
    employee_data = {"name": "Ghost User", "candidate_id": "cand_ghost"}
    mock_get_candidate.return_value = None # Simulate candidate not found
    
    result = process_employee_onboarding_workflow(employee_data)
    assert result is False
    captured = capsys.readouterr()
    assert "Onboarding Aborted: Candidate cand_ghost not found or not in 'Offer Accepted' state." in captured.out
    mock_get_candidate.assert_called_once_with("cand_ghost")


@patch("geo_infer_pep.methods.create_quarterly_overview")
@patch("geo_infer_pep.methods.get_talent_quarterly_metrics")
@patch("geo_infer_pep.methods.get_crm_quarterly_metrics")
@patch("geo_infer_pep.methods.get_hr_quarterly_metrics")
def test_generate_quarterly_people_report_success(
    mock_get_hr_metrics, mock_get_crm_metrics, 
    mock_get_talent_metrics, mock_create_overview, capsys
):
    """Test successful generation of the quarterly report with actual calls mocked."""
    quarter = "Q1"
    year = 2025
    
    mock_hr_metrics_data = {"quarter": quarter, "year": year, "headcount": 110}
    mock_crm_metrics_data = {"quarter": quarter, "year": year, "new_leads": 120}
    mock_talent_metrics_data = {"quarter": quarter, "year": year, "time_to_hire": 40}
    simulated_report_path = f"/tmp/final_Q{quarter}_{year}_report.txt"

    mock_get_hr_metrics.return_value = mock_hr_metrics_data
    mock_get_crm_metrics.return_value = mock_crm_metrics_data
    mock_get_talent_metrics.return_value = mock_talent_metrics_data
    mock_create_overview.return_value = simulated_report_path

    report_path = generate_quarterly_people_report(quarter, year)
    
    assert report_path == simulated_report_path
    
    captured = capsys.readouterr()
    assert f"Generating quarterly people report for Q{quarter} {year}..." in captured.out
    assert f"Quarterly people report generated at {simulated_report_path}." in captured.out

    mock_get_hr_metrics.assert_called_once_with(quarter, year)
    mock_get_crm_metrics.assert_called_once_with(quarter, year)
    mock_get_talent_metrics.assert_called_once_with(quarter, year)
    mock_create_overview.assert_called_once_with(mock_hr_metrics_data, mock_crm_metrics_data, mock_talent_metrics_data)

@patch("geo_infer_pep.methods.get_hr_quarterly_metrics", side_effect=Exception("HR Data Service Unavailable"))
def test_generate_quarterly_report_hr_fetch_failure(
    mock_get_hr_metrics_fails, capsys
):
    """Test report generation when fetching HR metrics fails."""
    quarter = "Q2"
    year = 2025

    # This test now expects an exception because the call is no longer wrapped in a try-except within methods.py itself
    with pytest.raises(Exception, match="HR Data Service Unavailable"):
        generate_quarterly_people_report(quarter, year)
    
    mock_get_hr_metrics_fails.assert_called_once_with(quarter, year)
    captured = capsys.readouterr()
    # Ensure the initial print still happens before the failure
    assert f"Generating quarterly people report for Q{quarter} {year}..." in captured.out 