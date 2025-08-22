"""HR API Endpoints."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Depends
from pathlib import Path
import tempfile # For handling file uploads

from ..models.hr_models import Employee
from ..hr.importer import CSVHRImporter # Assuming CSV importer for now
from ..hr.transformer import clean_employee_data, enrich_employee_data
from ..reporting.hr_reports import generate_headcount_report, generate_diversity_report
from ..visualizations.hr_visuals import plot_headcount_by_department, plot_gender_distribution

router = APIRouter(
    prefix="/hr",
    tags=["HR"],
)

# In-memory storage for HR data (replace with database in production)
DB_EMPLOYEES: List[Employee] = []

# Helper from crm_endpoints, consider moving to a shared utils if used often
async def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=upload_file.filename) as tmp:
            contents = await upload_file.read()
            tmp.write(contents)
            tmp_path = Path(tmp.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file: {e}")
    finally:
        await upload_file.close()
    return tmp_path

@router.post("/upload/csv", response_model=Dict[str, Any])
async def upload_hr_csv(
    file: UploadFile = File(...),
    clean_data: bool = Query(True, description="Perform data cleaning after import"),
    enrich_data: bool = Query(True, description="Perform data enrichment after cleaning")
):
    """
    Upload a CSV file with HR employee data. Data will be imported, (optionally) cleaned 
    and enriched, and then stored in memory.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are accepted.")

    temp_file_path = await save_upload_file_tmp(file)

    try:
        importer = CSVHRImporter(file_path=str(temp_file_path))
        imported_employees = importer.import_employees() # This uses the skeleton CSVHRImporter
        
        processed_employees = imported_employees
        if clean_data:
            processed_employees = clean_employee_data(processed_employees)
        if enrich_data:
            processed_employees = enrich_employee_data(processed_employees)
        
        global DB_EMPLOYEES
        DB_EMPLOYEES.clear() # Replace for simplicity
        DB_EMPLOYEES.extend(processed_employees)
        
        return {
            "message": f"Successfully imported and processed {len(DB_EMPLOYEES)} employees from {file.filename}",
            "imported_count": len(imported_employees),
            "processed_count": len(DB_EMPLOYEES),
            "cleaning_applied": clean_data,
            "enrichment_applied": enrich_data
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to HR data source: {e}")
    except FileNotFoundError:
        # This might occur if the temp_file_path is not handled correctly or CSVHRImporter fails before connect
        raise HTTPException(status_code=500, detail=f"HR CSV file not found. Path: {temp_file_path}")
    except Exception as e:
        print(f"Error during HR CSV processing: {e}") # TODO: Proper logging
        raise HTTPException(status_code=500, detail=f"An error occurred processing the HR CSV file: {e}")
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()

@router.get("/employees", response_model=List[Employee])
async def get_all_employees(
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0)
):
    """Retrieve all employees from the in-memory store."""
    return DB_EMPLOYEES[offset : offset + limit]

@router.get("/employees/count", response_model=Dict[str, int])
async def get_employees_count():
    """Get the total number of employees in the in-memory store."""
    return {"total_employees": len(DB_EMPLOYEES)}

@router.get("/reports/headcount", response_model=Dict[str, Any])
async def get_hr_headcount_report(group_by: Optional[List[str]] = Query(None, description="Fields to group by, e.g., department,location")):
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data. Upload data first.")
    return generate_headcount_report(DB_EMPLOYEES, group_by=group_by if group_by else [])

@router.get("/reports/diversity", response_model=Dict[str, Any])
async def get_hr_diversity_report(diversity_fields: Optional[List[str]] = Query(None, description="Fields for diversity metrics, e.g., gender,nationality")):
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data. Upload data first.")
    return generate_diversity_report(DB_EMPLOYEES, diversity_fields=diversity_fields if diversity_fields else ['gender'])

@router.get("/visualizations/headcount-by-department", response_model=Dict[str, str])
async def get_headcount_by_dept_plot():
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data for visualization.")
    plot_path = plot_headcount_by_department(DB_EMPLOYEES)
    if plot_path:
        return {"message": "Plot generated", "plot_file_path": plot_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate headcount plot.")

@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee_by_id(employee_id: str):
    """Get a specific employee by ID."""
    for emp in DB_EMPLOYEES:
        if emp.employee_id == employee_id:
            return emp
    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

@router.post("/employees", response_model=Employee)
async def create_employee(employee: Employee):
    """Create a new employee."""
    # Check if employee already exists
    for emp in DB_EMPLOYEES:
        if emp.employee_id == employee.employee_id:
            raise HTTPException(status_code=400, detail=f"Employee {employee.employee_id} already exists")

    # Validate employee data
    from ..core.validator import PEPValidator
    validator = PEPValidator()
    result = validator.validate_employee(employee)

    if not result.is_valid:
        raise HTTPException(status_code=400, detail=f"Validation failed: {result.errors}")

    DB_EMPLOYEES.append(employee)
    return employee

@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee_update: Dict[str, Any]):
    """Update an existing employee."""
    for i, emp in enumerate(DB_EMPLOYEES):
        if emp.employee_id == employee_id:
            # Update fields
            for key, value in employee_update.items():
                if hasattr(emp, key):
                    setattr(emp, key, value)

            # Re-validate
            from ..core.validator import PEPValidator
            validator = PEPValidator()
            result = validator.validate_employee(emp)

            if not result.is_valid:
                raise HTTPException(status_code=400, detail=f"Validation failed: {result.errors}")

            DB_EMPLOYEES[i] = emp
            return emp

    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    """Delete an employee."""
    for i, emp in enumerate(DB_EMPLOYEES):
        if emp.employee_id == employee_id:
            del DB_EMPLOYEES[i]
            return {"message": f"Employee {employee_id} deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

@router.get("/employees/search", response_model=List[Employee])
async def search_employees(
    department: Optional[str] = None,
    job_title: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Search employees with filters."""
    filtered_employees = DB_EMPLOYEES

    if department:
        filtered_employees = [emp for emp in filtered_employees if emp.department == department]

    if job_title:
        filtered_employees = [emp for emp in filtered_employees if emp.job_title == job_title]

    if status:
        filtered_employees = [emp for emp in filtered_employees
                            if emp.employment_status.value.lower() == status.lower()]

    return filtered_employees[:limit]

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_hr_dashboard():
    """Get comprehensive HR dashboard data."""
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data available")

    from ..methods import generate_comprehensive_hr_dashboard
    dashboard = generate_comprehensive_hr_dashboard()

    if "message" in dashboard and "No employee data" in dashboard["message"]:
        raise HTTPException(status_code=404, detail="No employee data available for dashboard")

    return dashboard

@router.get("/analytics/tenure", response_model=Dict[str, Any])
async def get_tenure_analytics():
    """Get employee tenure analytics."""
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data available")

    active_employees = [emp for emp in DB_EMPLOYEES if emp.employment_status.value == "ACTIVE"]
    tenure_values = []

    for emp in active_employees:
        if "tenure_years" in emp.custom_fields:
            tenure_values.append(emp.custom_fields["tenure_years"])

    if not tenure_values:
        return {"message": "No tenure data available"}

    import statistics
    return {
        "total_employees": len(active_employees),
        "employees_with_tenure_data": len(tenure_values),
        "average_tenure_years": statistics.mean(tenure_values),
        "median_tenure_years": statistics.median(tenure_values),
        "min_tenure_years": min(tenure_values),
        "max_tenure_years": max(tenure_values),
        "tenure_distribution": {
            "< 1 year": len([t for t in tenure_values if t < 1]),
            "1-3 years": len([t for t in tenure_values if 1 <= t < 3]),
            "3-5 years": len([t for t in tenure_values if 3 <= t < 5]),
            "5+ years": len([t for t in tenure_values if t >= 5])
        }
    }

@router.get("/analytics/turnover", response_model=Dict[str, Any])
async def get_turnover_analytics():
    """Get employee turnover analytics."""
    if not DB_EMPLOYEES:
        raise HTTPException(status_code=404, detail="No employee data available")

    terminated_employees = [emp for emp in DB_EMPLOYEES if emp.employment_status.value == "TERMINATED"]
    total_employees = len(DB_EMPLOYEES)

    # Calculate turnover rate
    turnover_rate = (len(terminated_employees) / total_employees * 100) if total_employees > 0 else 0

    # Analyze termination reasons (would need additional data field)
    termination_reasons = {}
    for emp in terminated_employees:
        reason = emp.custom_fields.get("termination_reason", "Unknown")
        termination_reasons[reason] = termination_reasons.get(reason, 0) + 1

    return {
        "total_employees": total_employees,
        "terminated_employees": len(terminated_employees),
        "turnover_rate_percent": round(turnover_rate, 2),
        "termination_reasons": termination_reasons,
        "average_tenure_at_termination": "Data not available"  # Would calculate from termination dates
    } 