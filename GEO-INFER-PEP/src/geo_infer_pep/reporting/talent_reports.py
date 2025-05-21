"""Talent Acquisition Reporting functions."""
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

from ..models.talent_models import Candidate, JobRequisition, CandidateStatus, JobRequisitionStatus
from ..talent.transformer import convert_candidates_to_dataframe, convert_requisitions_to_dataframe

def generate_candidate_pipeline_report(candidates: List[Candidate], requisitions: Optional[List[JobRequisition]] = None) -> Dict[str, Any]:
    """
    Generates a report on the current candidate pipeline status.
    """
    if not candidates:
        return {"message": "No candidate data for pipeline report."}

    cand_df = convert_candidates_to_dataframe(candidates)
    if cand_df.empty:
        return {"message": "Candidate data is empty after conversion."}

    report = {
        "total_candidates": len(cand_df),
        "candidates_by_status": cand_df['status'].value_counts().to_dict()
    }

    # If requisitions are provided, add pipeline by job requisition
    if requisitions:
        req_df = convert_requisitions_to_dataframe(requisitions)
        if not req_df.empty:
            # Merge or join candidate data with requisition data if needed for more detailed report
            # For now, just list active requisitions and their candidate counts by status
            pipeline_by_req = {}
            active_reqs = req_df[req_df['status'] == JobRequisitionStatus.OPEN]
            for index, req in active_reqs.iterrows():
                req_id = req['requisition_id']
                req_cands = cand_df[cand_df['job_requisition_id'] == req_id]
                pipeline_by_req[req_id] = {
                    'job_title': req['job_title'],
                    'total_candidates_for_req': len(req_cands),
                    'status_counts': req_cands['status'].value_counts().to_dict() if not req_cands.empty else {}
                }
            report['pipeline_by_active_requisition'] = pipeline_by_req
            
    print("Generated candidate pipeline report.")
    return report

def calculate_time_to_hire(hired_candidates: List[Candidate]) -> Dict[str, Any]:
    """
    Calculates average, min, max time to hire for candidates who reached 'HIRED' status.
    Assumes 'applied_at' and 'offer.accepted_at' or a 'hired_at' field exists and is populated.
    (Simplified: uses applied_at and assumes updated_at for HIRED status is effectively hired_at)
    """
    if not hired_candidates:
        return {"message": "No hired candidate data for time-to-hire calculation.", "avg_time_to_hire_days": None}

    durations = []
    for cand in hired_candidates:
        if cand.status == CandidateStatus.HIRED and cand.applied_at:
            # More accurate would be a specific hired_date or offer.accepted_at
            # Using cand.updated_at as a proxy for hired_at if status is HIRED
            hired_at_proxy = cand.updated_at 
            if isinstance(cand.applied_at, datetime) and isinstance(hired_at_proxy, datetime):
                duration = hired_at_proxy - cand.applied_at
                durations.append(duration.days)
            elif isinstance(cand.applied_at, str) and isinstance(hired_at_proxy, str):
                try:
                    applied_dt = datetime.fromisoformat(cand.applied_at)
                    hired_dt = datetime.fromisoformat(hired_at_proxy)
                    duration = hired_dt - applied_dt
                    durations.append(duration.days)
                except ValueError:
                    print(f"Could not parse dates for TTH for candidate {cand.candidate_id}")

    if not durations:
        return {"message": "Not enough valid data to calculate time to hire.", "avg_time_to_hire_days": None}

    report = {
        "number_of_hires_in_calc": len(durations),
        "avg_time_to_hire_days": round(sum(durations) / len(durations), 2) if durations else None,
        "min_time_to_hire_days": min(durations) if durations else None,
        "max_time_to_hire_days": max(durations) if durations else None
    }
    print("Calculated time to hire report.")
    return report

def get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]:
    """Simulates fetching Talent quarterly metrics."""
    print(f"Fetching Talent quarterly metrics for Q{quarter} {year} (simulated).")
    return {
        "quarter": quarter,
        "year": year,
        "open_positions": 25, # Simulated
        "candidates_sourced": 200, # Simulated
        "avg_time_to_fill_days": 45, # Simulated
        "offer_acceptance_rate_percent": 75.0 # Simulated
    }

# More talent reports:
# - Offer acceptance rate
# - Source effectiveness (which sources yield most hires)
# - Interviewer load and feedback turnaround time 