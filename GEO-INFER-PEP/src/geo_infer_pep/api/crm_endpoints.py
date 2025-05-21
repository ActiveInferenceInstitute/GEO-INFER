"""CRM API Endpoints."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File, Depends
from pathlib import Path
import tempfile

from ..models.crm_models import Customer
from ..crm.importer import CSVCRMImporter # Assuming CSV importer
from ..crm.transformer import clean_customer_data, enrich_customer_data, convert_customers_to_dataframe
from ..reporting.crm_reports import generate_customer_segmentation_report, generate_lead_conversion_report
from ..visualizations.crm_visuals import plot_customer_distribution_by_status, plot_customer_distribution_by_source

router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
)

# In-memory storage for simplicity for this example, replace with a database in a real app
# This also means data is lost on server restart and not shared between workers if scaled.
DB_CUSTOMERS: List[Customer] = []

# --- Helper for file uploads ---
async def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        # Create a temporary file
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
async def upload_crm_csv(
    file: UploadFile = File(...),
    clean_data: bool = Query(True, description="Perform data cleaning after import"),
    enrich_data: bool = Query(True, description="Perform data enrichment after cleaning")
):
    """
    Upload a CSV file with CRM data. Data will be imported, (optionally) cleaned and enriched,
    and then stored in memory (for this example).
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are accepted.")

    temp_file_path = await save_upload_file_tmp(file)

    try:
        importer = CSVCRMImporter(file_path=str(temp_file_path))
        imported_customers = importer.import_customers()
        
        processed_customers = imported_customers
        if clean_data:
            processed_customers = clean_customer_data(processed_customers)
        if enrich_data:
            processed_customers = enrich_customer_data(processed_customers)
        
        # For this example, we add to or replace the in-memory DB_CUSTOMERS
        # In a real app, you'd save to a persistent database.
        global DB_CUSTOMERS
        DB_CUSTOMERS.clear() # Replace existing data for simplicity
        DB_CUSTOMERS.extend(processed_customers)
        
        return {
            "message": f"Successfully imported and processed {len(DB_CUSTOMERS)} customers from {file.filename}",
            "imported_count": len(imported_customers),
            "processed_count": len(DB_CUSTOMERS),
            "cleaning_applied": clean_data,
            "enrichment_applied": enrich_data
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to data source: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Temporary CSV file not found after upload. This should not happen.")
    except Exception as e:
        # Log the full error for debugging on the server
        print(f"Error during CSV processing: {e}") # TODO: Replace with proper logging
        raise HTTPException(status_code=500, detail=f"An error occurred processing the CSV file: {e}")
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()

@router.get("/customers", response_model=List[Customer])
async def get_all_customers(
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0)
):
    """Retrieve all customers from the in-memory store."""
    return DB_CUSTOMERS[offset : offset + limit]

@router.get("/customers/count", response_model=Dict[str, int])
async def get_customers_count():
    """Get the total number of customers in the in-memory store."""
    return {"total_customers": len(DB_CUSTOMERS)}

@router.get("/reports/segmentation", response_model=Dict[str, Any])
async def get_crm_segmentation_report():
    """
    Generate and return a customer segmentation report.
    """
    if not DB_CUSTOMERS:
        raise HTTPException(status_code=404, detail="No customer data available to generate report. Please upload data first.")
    report = generate_customer_segmentation_report(DB_CUSTOMERS)
    return report

@router.get("/reports/lead-conversion", response_model=Dict[str, Any])
async def get_crm_lead_conversion_report():
    """
    Generate and return a lead conversion report.
    """
    if not DB_CUSTOMERS:
        raise HTTPException(status_code=404, detail="No customer data available to generate report. Please upload data first.")
    report = generate_lead_conversion_report(DB_CUSTOMERS)
    return report

@router.get("/visualizations/status-distribution", response_model=Dict[str, str])
async def get_status_distribution_plot():
    """
    Generate a customer status distribution plot and return its path.
    (In a real app, you might return the image directly or a URL).
    """
    if not DB_CUSTOMERS:
        raise HTTPException(status_code=404, detail="No customer data available to generate visualization. Please upload data first.")
    
    # Create a temporary directory for this request's plot if needed, or use a shared one
    # For simplicity, using the default from crm_visuals
    plot_path = plot_customer_distribution_by_status(DB_CUSTOMERS)
    if plot_path:
        return {"message": "Plot generated successfully", "plot_file_path": plot_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate plot.")

# TODO: Add more endpoints:
# - GET /customers/{customer_id}
# - POST /customers
# - PUT /customers/{customer_id}
# - DELETE /customers/{customer_id}
# - Endpoints for other reports and visualizations

# To run this (conceptual, assuming main.py wires this router):
# uvicorn main:app --reload 