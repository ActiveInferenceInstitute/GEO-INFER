"""Talent Data Transformers."""
from typing import List
import pandas as pd
from ..models.talent_models import Candidate, JobRequisition

def clean_candidate_data(candidates: List[Candidate]) -> List[Candidate]:
    """
    Performs basic cleaning on a list of Candidate objects.
    """
    cleaned_candidates = []
    for cand in candidates:
        # Example: Standardize skills to lowercase
        if cand.skills:
            cand.skills = [skill.lower() for skill in cand.skills]
        cleaned_candidates.append(cand)
    print(f"Performed cleaning on {len(cleaned_candidates)} candidate records (simulated).")
    return cleaned_candidates

def enrich_candidate_data(candidates: List[Candidate], requisitions: List[JobRequisition] = None) -> List[Candidate]:
    """
    Enriches candidate data, e.g., linking to job requisition details.
    """
    # Potentially create a lookup for requisitions by ID if provided
    req_lookup = {req.requisition_id: req for req in requisitions} if requisitions else {}
    
    enriched_candidates = []
    for cand in candidates:
        # Example: if cand.job_requisition_id in req_lookup:
        #    cand.job_title_applied_for = req_lookup[cand.job_requisition_id].job_title
        enriched_candidates.append(cand)
    print(f"Performed enrichment on {len(enriched_candidates)} candidate records (simulated).")
    return enriched_candidates

def convert_candidates_to_dataframe(candidates: List[Candidate]) -> pd.DataFrame:
    """
    Converts a list of Candidate Pydantic models to a Pandas DataFrame.
    """
    if not candidates:
        return pd.DataFrame()
    candidate_dicts = [cand.model_dump() for cand in candidates]
    df = pd.DataFrame(candidate_dicts)
    print(f"Converted {len(df)} candidate records to DataFrame.")
    return df

def convert_requisitions_to_dataframe(requisitions: List[JobRequisition]) -> pd.DataFrame:
    """
    Converts a list of JobRequisition Pydantic models to a Pandas DataFrame.
    """
    if not requisitions:
        return pd.DataFrame()
    req_dicts = [req.model_dump() for req in requisitions]
    df = pd.DataFrame(req_dicts)
    print(f"Converted {len(df)} job requisition records to DataFrame.")
    return df 