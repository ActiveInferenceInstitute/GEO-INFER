"""Talent Acquisition API Endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
import logging

from ..models.talent_models import Candidate, CandidateStatus
from ..core.data_store import pep_data_manager as store
from ..talent.importer import CSVTalentImporter
from ..talent.transformer import clean_candidate_data, enrich_candidate_data
from ..reporting.talent_reports import generate_candidate_pipeline_report, calculate_time_to_hire
from ..visualizations.talent_visuals import plot_candidate_pipeline_by_status
from ..utils import save_upload_file_tmp

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/talent",
    tags=["Talent"],
)


@router.post("/upload/candidates/csv", response_model=Dict[str, Any])
async def upload_candidates_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a CSV file with candidate data."""
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files.")
    temp_file_path = await save_upload_file_tmp(file)
    try:
        importer = CSVTalentImporter(candidate_file_path=str(temp_file_path))
        imported_candidates = importer.import_candidates()
        processed_candidates = clean_candidate_data(imported_candidates)
        processed_candidates = enrich_candidate_data(processed_candidates, store.requisitions)

        store.candidates.extend(processed_candidates)
        return {"message": f"Imported {len(store.candidates)} candidates from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing candidate CSV: {e}")
    finally:
        if temp_file_path.exists(): temp_file_path.unlink()

@router.get("/candidates", response_model=List[Candidate])
async def get_all_candidates(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[Candidate]:
    return store.candidates[offset : offset + limit]

@router.get("/reports/candidate-pipeline", response_model=Dict[str, Any])
async def get_talent_candidate_pipeline_report() -> Dict[str, Any]:
    if not store.candidates:
        raise HTTPException(status_code=404, detail="No candidate data. Upload data first.")
    return generate_candidate_pipeline_report(store.candidates, store.requisitions)

@router.get("/reports/time-to-hire", response_model=Dict[str, Any])
async def get_talent_time_to_hire_report() -> Dict[str, Any]:
    hired_candidates = [cand for cand in store.candidates if cand.status == CandidateStatus.HIRED]
    if not hired_candidates:
        raise HTTPException(status_code=404, detail="No hired candidates found for TTH report.")
    return calculate_time_to_hire(hired_candidates)

@router.get("/visualizations/candidate-pipeline-status", response_model=Dict[str, str])
async def get_candidate_pipeline_status_plot() -> Dict[str, str]:
    if not store.candidates:
        raise HTTPException(status_code=404, detail="No candidate data for visualization.")
    plot_path = plot_candidate_pipeline_by_status(store.candidates)
    if plot_path:
        return {"message": "Plot generated", "plot_file_path": plot_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate plot.")

# Future enhancements:
# - Endpoints for JobRequisitions (CRUD operations)
# - Endpoints for specific candidate by ID, updating candidate status, interviews, offers
# - Enhanced error handling and data validation with Pydantic models 