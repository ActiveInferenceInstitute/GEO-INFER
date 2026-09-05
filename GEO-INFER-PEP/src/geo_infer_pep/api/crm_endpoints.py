"""CRM API Endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
import logging

from ..models.crm_models import Customer
from ..core.data_store import pep_data_manager as store
from ..crm.importer import CSVCRMImporter
from ..crm.transformer import clean_customer_data, enrich_customer_data
from ..reporting.crm_reports import generate_customer_segmentation_report, generate_lead_conversion_report
from ..visualizations.crm_visuals import plot_customer_distribution_by_status
from ..utils import save_upload_file_tmp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
)


@router.post("/upload/csv", response_model=Dict[str, Any])
async def upload_crm_csv(
    file: UploadFile = File(...),
    clean_data: bool = Query(True, description="Perform data cleaning after import"),
    enrich_data: bool = Query(True, description="Perform data enrichment after cleaning")
) -> Dict[str, Any]:
    """
    Upload a CSV file with CRM data. Data will be imported, (optionally) cleaned and enriched,
    and then appended to the shared in-memory store (non-destructive).
    """
    if not file.filename or not file.filename.endswith('.csv'):
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
        
        # Appended to the shared in-memory store; in a real app you'd save
        # to a persistent database.
        store.customers.extend(processed_customers)
        
        return {
            "message": f"Successfully imported and processed {len(processed_customers)} customers from {file.filename}",
            "imported_count": len(imported_customers),
            "processed_count": len(processed_customers),
            "total_customers_in_store": len(store.customers),
            "cleaning_applied": clean_data,
            "enrichment_applied": enrich_data
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to data source: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Temporary CSV file not found after upload. This should not happen.")
    except Exception as e:
        # Log the full error for debugging on the server
        logger.error(f"Error during CSV processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred processing the CSV file: {e}")
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()

@router.get("/customers", response_model=List[Customer])
async def get_all_customers(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[Customer]:
    """Retrieve all customers from the in-memory store."""
    return store.customers[offset : offset + limit]

@router.get("/customers/count", response_model=Dict[str, int])
async def get_customers_count() -> Dict[str, int]:
    """Get the total number of customers in the in-memory store."""
    return {"total_customers": len(store.customers)}

@router.get("/reports/segmentation", response_model=Dict[str, Any])
async def get_crm_segmentation_report() -> Dict[str, Any]:
    """
    Generate and return a customer segmentation report.
    """
    if not store.customers:
        raise HTTPException(status_code=404, detail="No customer data available to generate report. Please upload data first.")
    report = generate_customer_segmentation_report(store.customers)
    return report

@router.get("/reports/lead-conversion", response_model=Dict[str, Any])
async def get_crm_lead_conversion_report() -> Dict[str, Any]:
    """
    Generate and return a lead conversion report.
    """
    if not store.customers:
        raise HTTPException(status_code=404, detail="No customer data available to generate report. Please upload data first.")
    report = generate_lead_conversion_report(store.customers)
    return report

@router.get("/visualizations/status-distribution", response_model=Dict[str, str])
async def get_status_distribution_plot() -> Dict[str, str]:
    """
    Generate a customer status distribution plot and return its path.
    (In a real app, you might return the image directly or a URL).
    """
    if not store.customers:
        raise HTTPException(status_code=404, detail="No customer data available to generate visualization. Please upload data first.")
    
    # Create a temporary directory for this request's plot if needed, or use a shared one
    # For simplicity, using the default from crm_visuals
    plot_path = plot_customer_distribution_by_status(store.customers)
    if plot_path:
        return {"message": "Plot generated successfully", "plot_file_path": plot_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate plot.")

# Planned endpoints (see GEO-INFER-PEP roadmap):
#   GET  /customers/{customer_id}
#   POST /customers
#   PUT  /customers/{customer_id}
#   DELETE /customers/{customer_id}
#   Additional report and visualisation endpoints

# To run this (conceptual, assuming main.py wires this router):
# uvicorn main:app --reload 