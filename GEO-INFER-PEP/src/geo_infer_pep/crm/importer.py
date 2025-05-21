"""CRM Data Importers."""
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.crm_models import Customer, Address, InteractionLog # Adjusted import path

class BaseCRMImporter(ABC):
    """Abstract base class for CRM importers."""

    @abstractmethod
    def connect(self, **kwargs) -> None:
        """Connect to the CRM data source."""
        pass

    @abstractmethod
    def fetch_data(self, last_sync_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch raw data from the CRM."""
        pass

    @abstractmethod
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Customer]:
        """Transform raw data into Customer Pydantic models."""
        pass

    def import_customers(self, last_sync_date: Optional[datetime] = None, **kwargs) -> List[Customer]:
        """Orchestrates the import process: connect, fetch, transform."""
        self.connect(**kwargs)
        raw_data = self.fetch_data(last_sync_date=last_sync_date)
        transformed_data = self.transform_data(raw_data)
        print(f"Successfully imported and transformed {len(transformed_data)} customer records.")
        return transformed_data

class CSVCRMImporter(BaseCRMImporter):
    """Imports CRM data from a CSV file."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.connection = None
        print(f"CSV CRM Importer initialized for file: {self.file_path}")

    def connect(self, **kwargs) -> None:
        """Simulates opening the CSV file."""
        try:
            # In a real scenario, you might keep the file open or check its existence.
            with open(self.file_path, 'r', encoding='utf-8') as f:
                pass # Just to check if file is accessible
            self.connection = "connected"
            print(f"Successfully connected to CSV file: {self.file_path}")
        except FileNotFoundError:
            print(f"Error: CSV file not found at {self.file_path}")
            raise
        except Exception as e:
            print(f"Error connecting to CSV file {self.file_path}: {e}")
            raise

    def fetch_data(self, last_sync_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Reads data from the CSV file."""
        if not self.connection:
            raise ConnectionError("Not connected to CSV file. Call connect() first.")
        
        records: List[Dict[str, Any]] = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Basic filtering by date if applicable
                    # This assumes a 'updated_at' or similar column in the CSV
                    if last_sync_date and 'updated_at' in row:
                        try:
                            record_date = datetime.fromisoformat(row['updated_at'])
                            if record_date <= last_sync_date:
                                continue
                        except ValueError:
                            # Handle cases where date format is incorrect or missing
                            print(f"Warning: Could not parse date for row: {row}")
                            pass # Or skip if strict
                    records.append(dict(row))
            print(f"Fetched {len(records)} records from {self.file_path}")
            return records
        except Exception as e:
            print(f"Error fetching data from CSV file {self.file_path}: {e}")
            return []

    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Customer]:
        """Transforms CSV rows into Customer Pydantic models."""
        customers: List[Customer] = []
        for record in raw_data:
            try:
                address = Address(
                    street=record.get('address_street'),
                    city=record.get('address_city'),
                    state=record.get('address_state'),
                    postal_code=record.get('address_postal_code'),
                    country=record.get('address_country')
                )
                
                # Example: simple interaction log from a notes field (highly simplified)
                interactions = []
                if record.get('notes'):
                    interactions.append(InteractionLog(summary=record['notes'], channel="csv_import"))

                customer_data = {
                    'customer_id': record.get('id', record.get('customer_id', f"csv-{hash(str(record))}")),
                    'first_name': record.get('first_name'),
                    'last_name': record.get('last_name', 'N/A'), # last_name is mandatory in model
                    'email': record.get('email'),
                    'phone_number': record.get('phone'),
                    'company': record.get('company_name'),
                    'job_title': record.get('title'),
                    'address': address,
                    'created_at': datetime.fromisoformat(record['created_at']) if record.get('created_at') else datetime.now(),
                    'updated_at': datetime.fromisoformat(record['updated_at']) if record.get('updated_at') else datetime.now(),
                    'source': record.get('lead_source', 'CSV Import'),
                    'status': record.get('status', 'active'),
                    'tags': record.get('tags', '').split(',') if record.get('tags') else [],
                    'interaction_history': interactions,
                    'notes': record.get('notes_detail')
                }
                # Pydantic will validate the data
                customers.append(Customer(**customer_data))
            except Exception as e:
                # Log the error and problematic record, then continue if possible
                print(f"Error transforming record: {record}. Error: {e}")
                # Optionally, add to an error list or re-raise if critical
        return customers

# Example of how to use the CSV Importer:
# if __name__ == '__main__':
#     # Create a dummy CSV for testing
#     dummy_csv_path = 'dummy_crm_data.csv'
#     with open(dummy_csv_path, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(['id', 'first_name', 'last_name', 'email', 'phone', 'company_name', 'title', 
#                          'address_street', 'address_city', 'address_state', 'address_postal_code', 'address_country',
#                          'created_at', 'updated_at', 'lead_source', 'status', 'tags', 'notes', 'notes_detail'])
#         writer.writerow(['1', 'John', 'Doe', 'john.doe@example.com', '555-1234', 'Acme Corp', 'Developer',
#                          '123 Main St', 'Anytown', 'CA', '90210', 'USA',
#                          datetime.now().isoformat(), datetime.now().isoformat(), 'Website', 'active', 'vip,developer', 'Initial contact', 'Met at conference'])
#         writer.writerow(['2', 'Jane', 'Smith', 'jane.smith@example.com', '555-5678', 'Beta Inc', 'Manager',
#                          '456 Oak Ave', 'Otherville', 'NY', '10001', 'USA',
#                          datetime(2023,1,15).isoformat(), datetime.now().isoformat(), 'Referral', 'lead', 'manager,high-priority', 'Followed up', 'Interested in Product X'])

#     importer = CSVCRMImporter(file_path=dummy_csv_path)
#     try:
#         imported_customers = importer.import_customers()
#         for cust in imported_customers:
#             print(cust.model_dump_json(indent=2))
#     except Exception as e:
#         print(f"An error occurred during import: {e}")

#     # Clean up dummy file
#     import os
#     os.remove(dummy_csv_path) 