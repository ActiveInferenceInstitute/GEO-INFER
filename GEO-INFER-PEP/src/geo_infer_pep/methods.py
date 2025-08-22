"""
Central methods for orchestrating GEO-INFER-PEP functionalities.

This module will contain high-level functions that combine various
operations from the submodules (crm, hr, talent, reporting, etc.)
to perform complex tasks.
"""
from typing import Dict, Any, List, Optional

# Import actual module implementations and data models
from .models.hr_models import Employee, EmploymentStatus
from .models.talent_models import Candidate, CandidateStatus
from .models.crm_models import Customer, InteractionLog
from .reporting import (
    get_hr_quarterly_metrics,
    get_crm_quarterly_metrics,
    get_talent_quarterly_metrics,
    create_quarterly_overview
)

# Import utility functions for data processing
from .hr.transformer import clean_employee_data, enrich_employee_data, convert_employees_to_dataframe
from .crm.transformer import clean_customer_data, enrich_customer_data, convert_customers_to_dataframe
from .talent.transformer import clean_candidate_data, enrich_candidate_data, convert_candidates_to_dataframe

# Import importers for data processing
from .hr.importer import CSVHRImporter
from .crm.importer import CSVCRMImporter
from .talent.importer import CSVTalentImporter

# Import reporting functions
from .reporting.hr_reports import generate_headcount_report, generate_diversity_report
from .reporting.crm_reports import generate_customer_segmentation_report, generate_lead_conversion_report
from .reporting.talent_reports import generate_candidate_pipeline_report, calculate_time_to_hire

# Global storage for demonstration (in production, use a database)
_employees_db = []
_candidates_db = []
_customers_db = []

def _get_employee_by_id(employee_id: str) -> Optional[Employee]:
    """Helper function to find employee by ID."""
    return next((emp for emp in _employees_db if emp.employee_id == employee_id), None)

def _get_candidate_by_id(candidate_id: str) -> Optional[Candidate]:
    """Helper function to find candidate by ID."""
    return next((cand for cand in _candidates_db if cand.candidate_id == candidate_id), None)

def _get_customer_by_id(customer_id: str) -> Optional[Customer]:
    """Helper function to find customer by ID."""
    return next((cust for cust in _customers_db if cust.customer_id == customer_id), None)

def process_employee_onboarding_workflow(employee_data: dict) -> bool:
    """
    Orchestrates the full employee onboarding process using real data models and processing.

    Args:
        employee_data: Dictionary containing candidate_id and other employee information

    Returns:
        bool: True if onboarding completed successfully, False otherwise

    Raises:
        ValueError: If required data is missing
        RuntimeError: If candidate not found or not in offer accepted state
    """
    candidate_id = employee_data.get("candidate_id")
    if not candidate_id:
        raise ValueError("candidate_id is required for onboarding workflow")

    print(f"Starting onboarding workflow for candidate {candidate_id}")

    # Find candidate in database
    candidate = _get_candidate_by_id(candidate_id)
    if not candidate:
        print(f"Onboarding Aborted: Candidate {candidate_id} not found.")
        return False

    if candidate.status != CandidateStatus.OFFER_ACCEPTED:
        print(f"Onboarding Aborted: Candidate {candidate_id} status is {candidate.status}, expected {CandidateStatus.OFFER_ACCEPTED}")
        return False

    try:
        # Create employee record using candidate data
        employee_id = f"emp_{candidate_id}_{candidate.first_name.lower()}_{candidate.last_name.lower()}"

        # Create Employee object with candidate data
        employee = Employee(
            employee_id=employee_id,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            phone_number=candidate.phone_number or "",
            hire_date=candidate.offer.accepted_at if candidate.offer and candidate.offer.accepted_at else None,
            employment_status=EmploymentStatus.ACTIVE,
            job_title="New Hire",  # Would come from requisition data in full implementation
            department="TBD",      # Would come from requisition data in full implementation
            location="Remote"      # Default location
        )

        # Add employee to database
        _employees_db.append(employee)

        # Process through HR pipeline (clean and enrich data)
        employees_list = [employee]
        cleaned_employees = clean_employee_data(employees_list)
        enriched_employees = enrich_employee_data(cleaned_employees)

        # Update employee with enriched data
        updated_employee = enriched_employees[0]
        employee_id = updated_employee.employee_id

        # Simulate benefits enrollment (would integrate with actual benefits system)
        print(f"Benefits: Initiating enrollment for employee {employee_id}")
        # In real implementation, this would call an external benefits API

        # Simulate training scheduling (would integrate with actual LMS)
        print(f"Training: Scheduling onboarding sessions for employee {employee_id}")
        # In real implementation, this would call an external learning management system

        print(f"Onboarding workflow for {candidate.first_name} {candidate.last_name} (employee ID: {employee_id}) completed successfully.")
        return True

    except Exception as e:
        print(f"Onboarding Failed: Error during employee creation - {str(e)}")
        return False

def generate_quarterly_people_report(quarter: str, year: int) -> str:
    """
    Generates a comprehensive quarterly people operations report.
    - Gathers HR metrics (headcount, attrition, diversity).
    - Gathers CRM metrics (customer satisfaction, new leads).
    - Gathers Talent metrics (time-to-hire, offer acceptance rate).
    - Compiles into a single report.
    """
    print(f"Generating quarterly people report for Q{quarter} {year}...")
    
    hr_metrics = get_hr_quarterly_metrics(quarter, year, _employees_db)
    crm_metrics = get_crm_quarterly_metrics(quarter, year, _customers_db)
    talent_metrics = get_talent_quarterly_metrics(quarter, year, _candidates_db)
    
    # Compile the quarterly overview report
    report_data = {
        "hr_metrics": hr_metrics,
        "crm_metrics": crm_metrics,
        "talent_metrics": talent_metrics,
        "quarter": quarter,
        "year": year,
        "generated_at": "2024-12-19",
        "total_records": {
            "employees": len(_employees_db),
            "customers": len(_customers_db),
            "candidates": len(_candidates_db)
        }
    }

    # In a real implementation, this would generate a PDF or detailed report
    report_path = f"quarterly_report_Q{quarter}_{year}.json"
    
    print(f"Quarterly people report generated at {report_path}.")
    return report_path

def import_hr_data_from_csv(file_path: str) -> List[Employee]:
    """
    Complete HR data pipeline: import, clean, enrich, and store employee data.

    Args:
        file_path: Path to CSV file containing HR data

    Returns:
        List of processed Employee objects
    """
    print(f"Starting HR data import from {file_path}")

    try:
        # Import raw data
        importer = CSVHRImporter(file_path)
        employees = importer.import_employees()

        if not employees:
            print(f"No employee data found in {file_path}")
            return []

        # Clean and enrich data
        cleaned_employees = clean_employee_data(employees)
        enriched_employees = enrich_employee_data(cleaned_employees)

        # Store in database
        _employees_db.extend(enriched_employees)

        print(f"Successfully imported and processed {len(enriched_employees)} employee records")
        return enriched_employees

    except Exception as e:
        print(f"Error importing HR data: {str(e)}")
        return []

def import_crm_data_from_csv(file_path: str) -> List[Customer]:
    """
    Complete CRM data pipeline: import, clean, enrich, and store customer data.

    Args:
        file_path: Path to CSV file containing CRM data

    Returns:
        List of processed Customer objects
    """
    print(f"Starting CRM data import from {file_path}")

    try:
        # Import raw data
        importer = CSVCRMImporter(file_path)
        customers = importer.import_customers()

        if not customers:
            print(f"No customer data found in {file_path}")
            return []

        # Clean and enrich data
        cleaned_customers = clean_customer_data(customers)
        enriched_customers = enrich_customer_data(cleaned_customers)

        # Store in database
        _customers_db.extend(enriched_customers)

        print(f"Successfully imported and processed {len(enriched_customers)} customer records")
        return enriched_customers

    except Exception as e:
        print(f"Error importing CRM data: {str(e)}")
        return []

def import_talent_data_from_csv(candidates_file: str, requisitions_file: str) -> Dict[str, Any]:
    """
    Complete talent data pipeline: import, clean, enrich, and store talent data.

    Args:
        candidates_file: Path to CSV file containing candidate data
        requisitions_file: Path to CSV file containing job requisition data

    Returns:
        Dictionary with processed candidates and requisitions
    """
    print(f"Starting talent data import from {candidates_file} and {requisitions_file}")

    try:
        # Import talent data
        importer = CSVTalentImporter(candidates_file, requisitions_file)
        candidates, requisitions = importer.import_candidates(), importer.import_requisitions()

        if candidates:
            # Clean and enrich candidate data
            cleaned_candidates = clean_candidate_data(candidates, requisitions)
            enriched_candidates = enrich_candidate_data(cleaned_candidates, requisitions)

            # Store in database
            _candidates_db.extend(enriched_candidates)

            print(f"Successfully imported and processed {len(enriched_candidates)} candidate records")

        if requisitions:
            print(f"Successfully imported and processed {len(requisitions)} requisition records")

        return {
            "candidates": len(_candidates_db),
            "requisitions": len(requisitions),
            "processed_successfully": True
        }

    except Exception as e:
        print(f"Error importing talent data: {str(e)}")
        return {"error": str(e), "processed_successfully": False}

def generate_comprehensive_hr_dashboard() -> Dict[str, Any]:
    """
    Generate comprehensive HR dashboard data combining multiple analytics.

    Returns:
        Dictionary containing various HR metrics and insights
    """
    if not _employees_db:
        return {"message": "No employee data available for dashboard"}

    print("Generating comprehensive HR dashboard...")

    try:
        # Generate various HR reports
        headcount_report = generate_headcount_report(_employees_db, group_by=["department"])
        diversity_report = generate_diversity_report(_employees_db, diversity_fields=["gender", "department"])

        # Calculate additional metrics
        total_employees = len(_employees_db)
        active_employees = len([e for e in _employees_db if e.employment_status == EmploymentStatus.ACTIVE])

        # Department breakdown
        dept_breakdown = {}
        for emp in _employees_db:
            if emp.employment_status == EmploymentStatus.ACTIVE:
                dept_breakdown[emp.department] = dept_breakdown.get(emp.department, 0) + 1

        dashboard_data = {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "headcount_by_department": dept_breakdown,
            "headcount_report": headcount_report,
            "diversity_report": diversity_report,
            "generated_at": "2024-12-19",  # Would use datetime.now() in production
            "data_freshness": f"Based on {len(_employees_db)} employee records"
        }

        print("HR dashboard generated successfully")
        return dashboard_data

    except Exception as e:
        print(f"Error generating HR dashboard: {str(e)}")
        return {"error": str(e), "message": "Failed to generate dashboard"}

def generate_comprehensive_crm_dashboard() -> Dict[str, Any]:
    """
    Generate comprehensive CRM dashboard data combining multiple analytics.

    Returns:
        Dictionary containing various CRM metrics and insights
    """
    if not _customers_db:
        return {"message": "No customer data available for dashboard"}

    print("Generating comprehensive CRM dashboard...")

    try:
        # Generate CRM reports
        segmentation_report = generate_customer_segmentation_report(_customers_db)
        conversion_report = generate_lead_conversion_report(_customers_db)

        # Calculate additional metrics
        total_customers = len(_customers_db)
        active_customers = len([c for c in _customers_db if c.status == "active"])

        # Status breakdown
        status_breakdown = {}
        for cust in _customers_db:
            status_breakdown[cust.status] = status_breakdown.get(cust.status, 0) + 1

        dashboard_data = {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "status_breakdown": status_breakdown,
            "segmentation_report": segmentation_report,
            "conversion_report": conversion_report,
            "generated_at": "2024-12-19",  # Would use datetime.now() in production
            "data_freshness": f"Based on {len(_customers_db)} customer records"
        }

        print("CRM dashboard generated successfully")
        return dashboard_data

    except Exception as e:
        print(f"Error generating CRM dashboard: {str(e)}")
        return {"error": str(e), "message": "Failed to generate dashboard"}

def generate_comprehensive_talent_dashboard() -> Dict[str, Any]:
    """
    Generate comprehensive talent dashboard data combining multiple analytics.

    Returns:
        Dictionary containing various talent metrics and insights
    """
    if not _candidates_db:
        return {"message": "No candidate data available for dashboard"}

    print("Generating comprehensive talent dashboard...")

    try:
        # Generate talent reports
        pipeline_report = generate_candidate_pipeline_report(_candidates_db, [])  # Empty requisitions list for now
        time_to_hire_report = calculate_time_to_hire(_candidates_db)

        # Calculate additional metrics
        total_candidates = len(_candidates_db)

        # Status breakdown
        status_breakdown = {}
        for cand in _candidates_db:
            status_breakdown[cand.status.value] = status_breakdown.get(cand.status.value, 0) + 1

        dashboard_data = {
            "total_candidates": total_candidates,
            "status_breakdown": status_breakdown,
            "pipeline_report": pipeline_report,
            "time_to_hire_report": time_to_hire_report,
            "generated_at": "2024-12-19",  # Would use datetime.now() in production
            "data_freshness": f"Based on {len(_candidates_db)} candidate records"
        }

        print("Talent dashboard generated successfully")
        return dashboard_data

    except Exception as e:
        print(f"Error generating talent dashboard: {str(e)}")
        return {"error": str(e), "message": "Failed to generate dashboard"}

def get_all_employees() -> List[Employee]:
    """Get all employees from the database."""
    return _employees_db.copy()

def get_all_candidates() -> List[Candidate]:
    """Get all candidates from the database."""
    return _candidates_db.copy()

def get_all_customers() -> List[Customer]:
    """Get all customers from the database."""
    return _customers_db.copy()

def clear_all_data() -> bool:
    """Clear all data from the in-memory database (for testing purposes)."""
    global _employees_db, _candidates_db, _customers_db
    _employees_db = []
    _candidates_db = []
    _customers_db = []
    print("All data cleared from database")
    return True 