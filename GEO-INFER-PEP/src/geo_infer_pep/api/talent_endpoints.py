"""Talent Acquisition API Endpoints."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pathlib import Path
import tempfile

from ..models.talent_models import Candidate, JobRequisition, CandidateStatus
from ..talent.importer import CSVTalentImporter # Assuming CSV importer
from ..talent.transformer import clean_candidate_data, enrich_candidate_data
from ..reporting.talent_reports import generate_candidate_pipeline_report, calculate_time_to_hire
from ..visualizations.talent_visuals import plot_candidate_pipeline_by_status, plot_time_to_hire_distribution

router = APIRouter(
    prefix="/talent",
    tags=["Talent"],
)

# In-memory storage (replace with DB in production)
DB_CANDIDATES: List[Candidate] = []
DB_REQUISITIONS: List[JobRequisition] = []

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

@router.post("/upload/candidates/csv", response_model=Dict[str, Any])
async def upload_candidates_csv(file: UploadFile = File(...)):
    """Upload a CSV file with candidate data."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files.")
    temp_file_path = await save_upload_file_tmp(file)
    try:
        importer = CSVTalentImporter(candidate_file_path=str(temp_file_path))
        imported_candidates = importer.import_candidates()
        processed_candidates = clean_candidate_data(imported_candidates)
        # processed_candidates = enrich_candidate_data(processed_candidates, DB_REQUISITIONS) # Requires requisitions loaded
        
        global DB_CANDIDATES
        DB_CANDIDATES.clear()
        DB_CANDIDATES.extend(processed_candidates)
        return {"message": f"Imported {len(DB_CANDIDATES)} candidates from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing candidate CSV: {e}")
    finally:
        if temp_file_path.exists(): temp_file_path.unlink()

@router.get("/candidates", response_model=List[Candidate])
async def get_all_candidates(limit: Optional[int] = Query(100, ge=1, le=1000), offset: Optional[int] = Query(0, ge=0)):
    return DB_CANDIDATES[offset : offset + limit]

@router.get("/reports/candidate-pipeline", response_model=Dict[str, Any])
async def get_talent_candidate_pipeline_report():
    if not DB_CANDIDATES:
        raise HTTPException(status_code=404, detail="No candidate data. Upload data first.")
    return generate_candidate_pipeline_report(DB_CANDIDATES, DB_REQUISITIONS)

@router.get("/reports/time-to-hire", response_model=Dict[str, Any])
async def get_talent_time_to_hire_report():
    hired_candidates = [cand for cand in DB_CANDIDATES if cand.status == CandidateStatus.HIRED]
    if not hired_candidates:
        raise HTTPException(status_code=404, detail="No hired candidates found for TTH report.")
    return calculate_time_to_hire(hired_candidates)

@router.get("/visualizations/candidate-pipeline-status", response_model=Dict[str, str])
async def get_candidate_pipeline_status_plot():
    if not DB_CANDIDATES:
        raise HTTPException(status_code=404, detail="No candidate data for visualization.")
    plot_path = plot_candidate_pipeline_by_status(DB_CANDIDATES)
    if plot_path:
        return {"message": "Plot generated", "plot_file_path": plot_path}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate plot.")

# TODO: Endpoints for JobRequisitions (CRUD)
# TODO: Endpoints for specific candidate by ID, updating candidate status, interviews, offers.
# TODO: More sophisticated error handling and data validation. 