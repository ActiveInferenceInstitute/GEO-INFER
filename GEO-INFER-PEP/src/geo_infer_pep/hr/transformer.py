"""HR Data Transformers."""
from typing import List
import pandas as pd
from ..models.hr_models import Employee

def clean_employee_data(employees: List[Employee]) -> List[Employee]:
    """
    Performs basic cleaning operations on a list of Employee objects.
    - Example: Validates email formats (Pydantic does some of this).
    - Example: Standardizes string case for certain fields.
    """
    cleaned_employees = []
    for emp in employees:
        # Add cleaning rules here
        # e.g., if emp.department: emp.department = emp.department.title()
        cleaned_employees.append(emp)
    print(f"Performed cleaning on {len(cleaned_employees)} employee records (simulated).")
    return cleaned_employees

def enrich_employee_data(employees: List[Employee], org_data: dict = None) -> List[Employee]:
    """
    Enriches employee data.
    - Example: Calculate tenure.
    - Example: Link to manager's Employee object if ID is present.
    """
    enriched_employees = []
    for emp in employees:
        # Add enrichment rules here
        # e.g., from datetime import date
        # if emp.hire_date:
        #    today = date.today()
        #    emp.tenure_years = today.year - emp.hire_date.year - ((today.month, today.day) < (emp.hire_date.month, emp.hire_date.day))
        enriched_employees.append(emp)
    print(f"Performed enrichment on {len(enriched_employees)} employee records (simulated).")
    return enriched_employees

def convert_employees_to_dataframe(employees: List[Employee]) -> pd.DataFrame:
    """
    Converts a list of Employee Pydantic models to a Pandas DataFrame.
    """
    if not employees:
        return pd.DataFrame()
    
    employee_dicts = [emp.model_dump() for emp in employees]
    df = pd.DataFrame(employee_dicts)
    # Further processing like flattening nested structures (e.g., compensation, job_history)
    # can be done here if needed for specific analyses.
    print(f"Converted {len(df)} employee records to DataFrame.")
    return df 