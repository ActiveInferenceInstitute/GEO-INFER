import pytest
import os
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import csv # Ensure csv is imported at the top level

from geo_infer_pep.models.hr_models import Employee, EmploymentStatus, Gender, Compensation, JobHistoryEntry
from geo_infer_pep.hr.importer import CSVHRImporter
from geo_infer_pep.hr.transformer import clean_employee_data, enrich_employee_data, convert_employees_to_dataframe
from geo_infer_pep.reporting.hr_reports import generate_headcount_report, generate_diversity_report
from geo_infer_pep.visualizations.hr_visuals import plot_headcount_by_department, plot_gender_distribution

# Fixtures
@pytest.fixture
def sample_employee_data_list():
    """Provides a list of Employee Pydantic models for testing."""
    return [
        Employee(
            employee_id="emp1",
            first_name="Alice",
            last_name="Wonderland",
            email="alice.wonder@example.com",
            hire_date=date(2022, 1, 10),
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Engineer",
            department="Technology",
            gender=Gender.FEMALE
        ),
        Employee(
            employee_id="emp2",
            first_name="Bob",
            last_name="Builder",
            email="bob.builder@example.com",
            hire_date=date(2021, 5, 15),
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Manager",
            department="Operations",
            gender=Gender.MALE
        ),
        Employee(
            employee_id="emp3",
            first_name="Charlie",
            last_name="Chocolate",
            email="charlie.choco@example.com",
            hire_date=date(2023, 3, 1),
            employment_status=EmploymentStatus.PENDING_HIRE,
            job_title="Analyst",
            department="Finance",
            gender=Gender.MALE
        ),
         Employee(
            employee_id="emp4",
            first_name="Diana",
            last_name="Prince",
            email="diana.prince@example.com",
            hire_date=date(2020, 7, 20),
            employment_status=EmploymentStatus.ACTIVE,
            job_title="Specialist",
            department="Technology", # Same dept as Alice for grouping
            gender=Gender.FEMALE
        )
    ]

@pytest.fixture
def dummy_hr_csv_file(tmp_path):
    """Creates a dummy HR CSV file for importer testing."""
    csv_path = tmp_path / "dummy_hr.csv"
    headers = ['employee_id', 'first_name', 'last_name', 'email', 'hire_date', 'status', 'job_title', 'department', 'gender']
    row1 = ['emp_csv_001', 'CSVFirst', 'CSVLast', 'csv.user@example.com', '2023-01-15', 'active', 'Tester', 'QA', 'female']
    row2 = ['emp_csv_002', 'Another', 'User', 'another.user@example.com', '2022-11-20', 'on_leave', 'Developer', 'R&D', 'male']
    row_bad_date = ['emp_csv_003', 'Bad', 'Date', 'baddate@example.com', '202-13-99', 'active', 'Analyst', 'Data', 'non_binary'] # Invalid date
    row_minimal = ['emp_csv_004', 'Min', 'Imal', 'min@example.com', '2024-02-01', 'pending_hire', 'Intern', 'HR', ''] # Empty gender

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(row1)
        writer.writerow(row2)
        writer.writerow(row_bad_date)
        writer.writerow(row_minimal)
    return csv_path

# Model Tests
def test_employee_model():
    comp = Compensation(salary=50000, currency="USD", pay_frequency="annual")
    history = JobHistoryEntry(job_title="Previous Role", department="Old Dept", start_date=date(2020,1,1), end_date=date(2021,12,31))
    emp = Employee(
        employee_id="test_emp001",
        first_name="Testy",
        last_name="McTestFace",
        email="testy@example.com",
        hire_date=date(2022, 2, 2),
        employment_status=EmploymentStatus.ACTIVE,
        job_title="Chief Tester",
        department="Testing",
        compensation=comp,
        job_history=[history]
    )
    assert emp.employee_id == "test_emp001"
    assert emp.compensation.salary == 50000
    assert emp.full_name == "Testy McTestFace"

# Importer Tests
def test_csv_hr_importer(dummy_hr_csv_file, capsys):
    importer = CSVHRImporter(file_path=str(dummy_hr_csv_file))
    employees = importer.import_employees()
    
    captured = capsys.readouterr() # To check for warnings
    assert "Warning: Could not parse hire_date for record: emp_csv_003" in captured.out

    assert len(employees) == 3 # emp_csv_003 hire_date is None, but still processed. row_minimal gender is None.
                               # One record (emp_csv_003) had a bad date and thus hire_date=None, still valid Employee object.
                               # The fourth record (row_minimal) has empty gender, which becomes None.
                               # CSVHRImporter will print an error for bad date, but continue.
                               # The test actually expects 3 valid employees to be created from the CSV,
                               # The one with bad date will have hire_date=None. The one with empty gender will have gender=None.
                               # Re-evaluating: The importer currently creates Employee objects even with parsing errors, setting problematic fields to None.
                               # The question is whether a record with a critical parsing error (like a malformed required field that doesn't have a default)
                               # *should* result in an Employee object. Pydantic validation is key here.
                               # For `hire_date` (Optional in model if it's `date | None`), it's fine.
                               # Let's adjust to expect 4 employees, as the model can handle `hire_date=None` and `gender=None`.

    # We should have 4 employees because the one with bad date still gets created with hire_date = None
    # and the one with empty gender also gets created with gender = None.
    assert len(employees) == 4

    emp1 = next(e for e in employees if e.employee_id == "emp_csv_001")
    assert emp1.first_name == "CSVFirst"
    assert emp1.email == "csv.user@example.com"
    assert emp1.hire_date == date(2023, 1, 15)
    assert emp1.employment_status == EmploymentStatus.ACTIVE
    assert emp1.gender == Gender.FEMALE

    emp_bad_date = next(e for e in employees if e.employee_id == "emp_csv_003")
    assert emp_bad_date.hire_date is None # Due to parsing error
    assert emp_bad_date.gender == Gender.NON_BINARY

    emp_minimal = next(e for e in employees if e.employee_id == "emp_csv_004")
    assert emp_minimal.gender is None # Empty string in CSV becomes None
    assert emp_minimal.employment_status == EmploymentStatus.PENDING_HIRE

# Transformer Tests (simulated, as actual transformation from CSV depends on importer populating fields)
# These tests remain largely the same as transformers are simple pass-throughs for now.
def test_clean_employee_data(sample_employee_data_list):
    cleaned = clean_employee_data(sample_employee_data_list) # Currently a pass-through
    assert len(cleaned) == 4
    # Add specific assertions if/when cleaning logic is implemented

def test_enrich_employee_data(sample_employee_data_list):
    enriched = enrich_employee_data(sample_employee_data_list) # Currently a pass-through
    assert len(enriched) == 4
    # Add specific assertions if/when enrichment logic is implemented (e.g., tenure calculation)

def test_convert_employees_to_dataframe(sample_employee_data_list):
    df = convert_employees_to_dataframe(sample_employee_data_list)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4
    assert 'email' in df.columns

# Reporting Tests
def test_generate_headcount_report(sample_employee_data_list):
    report = generate_headcount_report(sample_employee_data_list, group_by=["department"])
    assert report["total_headcount"] == 3 # emp3 is PENDING_HIRE
    assert report["headcount_by_department"]["Technology"] == 2
    assert report["headcount_by_department"]["Operations"] == 1

def test_generate_diversity_report(sample_employee_data_list):
    report = generate_diversity_report(sample_employee_data_list, diversity_fields=["gender", "department"])
    assert report["total_active_employees_for_diversity_metrics"] == 3
    assert "counts" in report["diversity_by_gender"]
    assert report["diversity_by_gender"]["counts"].get(Gender.FEMALE.value) == 2
    assert report["diversity_by_gender"]["counts"].get(Gender.MALE.value) == 1
    assert "percentages" in report["diversity_by_department"]

# Visualization Tests
def test_plot_headcount_by_department(sample_employee_data_list, tmp_path):
    output_dir = tmp_path / "hr_visuals"
    output_dir.mkdir()
    plot_path = plot_headcount_by_department(sample_employee_data_list, output_dir=output_dir)
    assert plot_path is not None
    assert os.path.exists(plot_path)
    assert Path(plot_path).name == "headcount_by_department.png"

def test_plot_gender_distribution(sample_employee_data_list, tmp_path):
    output_dir = tmp_path / "hr_visuals"
    # output_dir.mkdir() # Created by previous test or ensure it exists if run in parallel
    plot_path = plot_gender_distribution(sample_employee_data_list, output_dir=output_dir)
    assert plot_path is not None
    assert os.path.exists(plot_path)
    assert Path(plot_path).name == "gender_distribution.png"

# Test with empty data
def test_hr_reports_empty_data():
    empty_list = []
    headcount_report = generate_headcount_report(empty_list)
    assert "No employee data" in headcount_report.get("message", "")
    diversity_report = generate_diversity_report(empty_list)
    assert "No employee data" in diversity_report.get("message", "")

def test_hr_visuals_empty_data(tmp_path):
    empty_list = []
    output_dir = tmp_path / "hr_visuals_empty"
    output_dir.mkdir()
    dept_plot = plot_headcount_by_department(empty_list, output_dir=output_dir)
    assert dept_plot is None
    gender_plot = plot_gender_distribution(empty_list, output_dir=output_dir)
    assert gender_plot is None

# Test importer with non-existent file
def test_csv_hr_importer_file_not_found():
    importer = CSVHRImporter(file_path="non_existent_hr_file.csv")
    with pytest.raises(FileNotFoundError):
        importer.connect()
    with pytest.raises(FileNotFoundError): 
         importer.import_employees() 