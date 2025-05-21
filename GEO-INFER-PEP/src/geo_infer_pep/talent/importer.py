"""Talent Data Importers (e.g., from ATS)."""
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from ..models.talent_models import Candidate, JobRequisition, CandidateStatus, JobRequisitionStatus

class BaseTalentImporter(ABC):
    """Abstract base class for Talent data importers."""

    @abstractmethod
    def connect(self, **kwargs) -> None:
        """Connect to the Talent data source (e.g., ATS API)."""
        pass

    @abstractmethod
    def fetch_candidates(self, last_sync_date: Optional[datetime] = None, requisition_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch raw candidate data."""
        pass

    @abstractmethod
    def transform_candidates(self, raw_data: List[Dict[str, Any]]) -> List[Candidate]:
        """Transform raw data into Candidate Pydantic models."""
        pass

    @abstractmethod
    def fetch_requisitions(self, last_sync_date: Optional[datetime] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch raw job requisition data."""
        pass

    @abstractmethod
    def transform_requisitions(self, raw_data: List[Dict[str, Any]]) -> List[JobRequisition]:
        """Transform raw data into JobRequisition Pydantic models."""
        pass

    def import_candidates(self, last_sync_date: Optional[datetime] = None, requisition_id: Optional[str] = None, **kwargs) -> List[Candidate]:
        self.connect(**kwargs)
        raw_data = self.fetch_candidates(last_sync_date=last_sync_date, requisition_id=requisition_id)
        transformed_data = self.transform_candidates(raw_data)
        print(f"Imported and transformed {len(transformed_data)} candidate records.")
        return transformed_data

    def import_requisitions(self, last_sync_date: Optional[datetime] = None, status: Optional[str] = None, **kwargs) -> List[JobRequisition]:
        self.connect(**kwargs)
        raw_data = self.fetch_requisitions(last_sync_date=last_sync_date, status=status)
        transformed_data = self.transform_requisitions(raw_data)
        print(f"Imported and transformed {len(transformed_data)} job requisition records.")
        return transformed_data

# Example: CSVTalentImporter (Now more functional)
class CSVTalentImporter(BaseTalentImporter):
    """Imports Talent data from CSV files."""
    def __init__(self, candidate_file_path: Optional[str] = None, requisition_file_path: Optional[str] = None):
        self.candidate_file_path = candidate_file_path
        self.requisition_file_path = requisition_file_path
        self.connection = None # Simplified connection status
        print("CSVTalentImporter initialized.")

    def connect(self, **kwargs) -> None:
        # In a real scenario, might check file existence or prepare readers
        # For now, connection is established if at least one file path is provided.
        if self.candidate_file_path or self.requisition_file_path:
            self.connection = "connected"
            print("CSVTalentImporter connected (simulated for CSV files).")
        else:
            print("CSVTalentImporter not connected: No file paths provided.")
            # Optionally raise an error if connection is strictly required for any operation
            # raise ValueError("Cannot connect: No candidate or requisition file path provided.")

    def _read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        if not self.connection:
            # Attempt to connect if not already. This is a soft connect.
            self.connect()
            if not self.connection: # If still not connected (e.g. no paths)
                 raise ConnectionError("Not connected. Call connect() or provide file paths.")
        
        if not file_path:
            return []

        records: List[Dict[str, Any]] = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    records.append(dict(row))
            print(f"Fetched {len(records)} records from {file_path}")
            return records
        except FileNotFoundError:
            print(f"Error: CSV file not found at {file_path}")
            raise # Re-raise to be caught by tests or higher level logic
        except Exception as e:
            print(f"Error fetching data from CSV file {file_path}: {e}")
            return []

    def fetch_candidates(self, last_sync_date: Optional[datetime] = None, requisition_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.candidate_file_path:
            print("Warning: Candidate file path not provided for fetch_candidates.")
            return []
        # Basic filtering could be added here post-fetch if needed, e.g., by date or req_id
        return self._read_csv_file(self.candidate_file_path)

    def transform_candidates(self, raw_data: List[Dict[str, Any]]) -> List[Candidate]:
        candidates: List[Candidate] = []
        for record in raw_data:
            try:
                applied_at_dt = None
                if record.get('applied_at'):
                    try: applied_at_dt = datetime.fromisoformat(record['applied_at'])
                    except ValueError: print(f"Warn: Bad applied_at for cand {record.get('candidate_id')}")
                
                updated_at_dt = None
                if record.get('updated_at'):
                    try: updated_at_dt = datetime.fromisoformat(record['updated_at'])
                    except ValueError: print(f"Warn: Bad updated_at for cand {record.get('candidate_id')}")

                candidate_data = {
                    'candidate_id': record.get('candidate_id'),
                    'first_name': record.get('first_name'),
                    'last_name': record.get('last_name'),
                    'email': record.get('email'),
                    'phone_number': record.get('phone_number'),
                    'status': CandidateStatus(record['status'].strip().lower()) if record.get('status') and record.get('status').strip() else CandidateStatus.APPLIED,
                    'job_requisition_id': record.get('job_requisition_id'),
                    'source': record.get('source'),
                    'applied_at': applied_at_dt or datetime.now(), # Default if missing/bad
                    'updated_at': updated_at_dt or datetime.now(), # Default if missing/bad
                    'skills': [s.strip() for s in record.get('skills', '').split(',') if s.strip()] if record.get('skills') is not None else [],
                    # Add other fields like linkedin_profile, resume_url etc.
                }
                candidate_data_cleaned = {k:v for k,v in candidate_data.items() if v is not None or k in ['applied_at', 'updated_at']}
                candidates.append(Candidate(**candidate_data_cleaned))
            except Exception as e:
                print(f"Error transforming candidate record: {record.get('candidate_id', 'Unknown ID')}. Error: {e}")
        print(f"Transformed {len(candidates)} candidate records.")
        return candidates

    def fetch_requisitions(self, last_sync_date: Optional[datetime] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.requisition_file_path:
            print("Warning: Requisition file path not provided for fetch_requisitions.")
            return []
        # Basic filtering could be added here post-fetch if needed
        return self._read_csv_file(self.requisition_file_path)

    def transform_requisitions(self, raw_data: List[Dict[str, Any]]) -> List[JobRequisition]:
        requisitions: List[JobRequisition] = []
        for record in raw_data:
            try:
                opened_at_date = None
                if record.get('opened_at'):
                    try: opened_at_date = datetime.strptime(record['opened_at'], '%Y-%m-%d').date()
                    except ValueError: print(f"Warn: Bad opened_at for req {record.get('requisition_id')}")

                closed_at_date = None
                if record.get('closed_at'):
                    try: closed_at_date = datetime.strptime(record['closed_at'], '%Y-%m-%d').date()
                    except ValueError: print(f"Warn: Bad closed_at for req {record.get('requisition_id')}")

                req_data = {
                    'requisition_id': record.get('requisition_id'),
                    'job_title': record.get('job_title'),
                    'department': record.get('department'),
                    'status': JobRequisitionStatus(record['status'].strip().lower()) if record.get('status') and record.get('status').strip() else JobRequisitionStatus.OPEN,
                    'opened_at': opened_at_date or date.today(), # Default if missing/bad
                    'closed_at': closed_at_date,
                    'hiring_manager_id': record.get('hiring_manager_id')
                    # Add other fields like location, description, etc.
                }
                req_data_cleaned = {k:v for k,v in req_data.items() if v is not None or k == 'closed_at'}
                requisitions.append(JobRequisition(**req_data_cleaned))
            except Exception as e:
                print(f"Error transforming requisition record: {record.get('requisition_id', 'Unknown ID')}. Error: {e}")
        print(f"Transformed {len(requisitions)} job requisition records.")
        return requisitions

# Future importers: GreenhouseImporter, LeverImporter, WorkableImporter 