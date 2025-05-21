"""HR Reporting functions."""
from typing import List, Dict, Any
import pandas as pd
from ..models.hr_models import Employee, EmploymentStatus
from ..hr.transformer import convert_employees_to_dataframe

def generate_headcount_report(employees: List[Employee], group_by: List[str] = None) -> Dict[str, Any]:
    """
    Generates a headcount report, optionally grouped by specified fields (e.g., department, location).
    """
    if not employees:
        return {"message": "No employee data for headcount report."}

    df = convert_employees_to_dataframe(employees)
    if df.empty:
        return {"message": "Employee data is empty after conversion to DataFrame."}

    report = {"total_headcount": len(df[df['employment_status'] == EmploymentStatus.ACTIVE])}

    if group_by:
        active_employees_df = df[df['employment_status'] == EmploymentStatus.ACTIVE]
        for field in group_by:
            if field in active_employees_df.columns:
                report[f'headcount_by_{field}'] = active_employees_df.groupby(field).size().to_dict()
            else:
                report[f'headcount_by_{field}'] = f"Field '{field}' not found for grouping."
    
    print("Generated headcount report.")
    return report

def generate_diversity_report(employees: List[Employee], diversity_fields: List[str] = None) -> Dict[str, Any]:
    """
    Generates a diversity report based on specified fields (e.g., gender, nationality).
    (This is a simplified example and needs careful consideration of privacy and ethics.)
    """
    if not employees:
        return {"message": "No employee data for diversity report."}
    
    df = convert_employees_to_dataframe(employees)
    if df.empty:
        return {"message": "Employee data is empty after conversion to DataFrame."}

    active_employees_df = df[df['employment_status'] == EmploymentStatus.ACTIVE]
    report = {"total_active_employees_for_diversity_metrics": len(active_employees_df)}

    if not diversity_fields:
        diversity_fields = ['gender'] # Default to gender if no fields specified

    for field in diversity_fields:
        if field in active_employees_df.columns:
            counts = active_employees_df[field].value_counts()
            percentages = active_employees_df[field].value_counts(normalize=True) * 100
            report[f'diversity_by_{field}'] = {
                "counts": counts.to_dict(),
                "percentages": percentages.round(2).to_dict()
            }
        else:
            report[f'diversity_by_{field}'] = f"Field '{field}' not found for diversity metrics."
            
    print("Generated diversity report.")
    return report

def get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]:
    """Simulates fetching HR quarterly metrics."""
    print(f"Fetching HR quarterly metrics for Q{quarter} {year} (simulated).")
    return {
        "quarter": quarter,
        "year": year,
        "headcount_end_of_quarter": 105, # Simulated
        "attrition_rate_percent": 2.5, # Simulated
        "new_hires": 10, # Simulated
        "diversity_snapshot": {"gender_female_percent": 45.0} # Simulated
    }

# Add more HR-specific reporting functions here, e.g.:
# - Attrition rate report
# - Compensation summary report
# - Performance review completion status 