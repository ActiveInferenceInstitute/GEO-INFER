"""HR Data Importers."""
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from ..models.hr_models import Employee, EmploymentStatus, Gender # Adjusted import path

class BaseHRImporter(ABC):
    """Abstract base class for HR data importers."""

    @abstractmethod
    def connect(self, **kwargs) -> None:
        """Connect to the HR data source."""
        pass

    @abstractmethod
    def fetch_employees(self, last_sync_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch raw employee data from the HR source."""
        pass

    @abstractmethod
    def transform_employees(self, raw_data: List[Dict[str, Any]]) -> List[Employee]:
        """Transform raw employee data into Employee Pydantic models."""
        pass

    def import_employees(self, last_sync_date: Optional[datetime] = None, **kwargs) -> List[Employee]:
        """Orchestrates the import process: connect, fetch, transform for employees."""
        self.connect(**kwargs)
        raw_data = self.fetch_employees(last_sync_date=last_sync_date)
        transformed_data = self.transform_employees(raw_data)
        print(f"Successfully imported and transformed {len(transformed_data)} employee records.")
        return transformed_data

# Example: CSVHRImporter (Now functional for basic fields)
class CSVHRImporter(BaseHRImporter):
    """Imports HR data from a CSV file."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.connection = None
        print(f"CSV HR Importer initialized for file: {self.file_path}")

    def connect(self, **kwargs) -> None:
        try:
            # Check accessibility
            with open(self.file_path, 'r', encoding='utf-8') as f:
                pass 
            self.connection = "connected"
            print(f"Successfully connected to HR CSV file: {self.file_path}")
        except FileNotFoundError:
            print(f"Error: HR CSV file not found at {self.file_path}")
            raise
        except Exception as e:
            print(f"Error connecting to HR CSV file {self.file_path}: {e}")
            raise

    def fetch_employees(self, last_sync_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        if not self.connection:
            raise ConnectionError("Not connected to HR CSV file. Call connect() first.")
        
        records: List[Dict[str, Any]] = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Add date filtering if last_sync_date and relevant date column in CSV
                    records.append(dict(row))
            print(f"Fetched {len(records)} employee records from {self.file_path}")
            return records
        except Exception as e:
            print(f"Error fetching employee data from CSV {self.file_path}: {e}")
            return []

    def transform_employees(self, raw_data: List[Dict[str, Any]]) -> List[Employee]:
        employees: List[Employee] = []
        for record in raw_data:
            try:
                # Basic date parsing, assuming YYYY-MM-DD format
                hire_dt = None
                if record.get('hire_date'):
                    try:
                        hire_dt = datetime.strptime(record['hire_date'], '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Warning: Could not parse hire_date for record: {record.get('employee_id')}")

                employee_data = {
                    'employee_id': record.get('employee_id'),
                    'first_name': record.get('first_name'),
                    'last_name': record.get('last_name'),
                    'email': record.get('email'),
                    'hire_date': hire_dt,
                    'employment_status': EmploymentStatus(record['status'].strip().lower()) if record.get('status') and record.get('status').strip() else EmploymentStatus.ACTIVE,
                    'job_title': record.get('job_title'),
                    'department': record.get('department'),
                    'gender': Gender(record['gender'].strip().lower()) if record.get('gender') and record.get('gender').strip() else None,
                    # Add other fields as necessary from your CSV
                }
                # Filter out None values for fields that are optional and not provided
                employee_data_cleaned = {k: v for k, v in employee_data.items() if v is not None or k in ['hire_date']}


                # Pydantic will validate
                employees.append(Employee(**employee_data_cleaned))
            except Exception as e:
                print(f"Error transforming HR record: {record.get('employee_id', 'Unknown ID')}. Error: {e}")
        print(f"Transformed {len(employees)} employee records.")
        return employees

# Future importers could include:
# - BambooHRImporter
# - WorkdayImporter
# - OtherHRISImporter 