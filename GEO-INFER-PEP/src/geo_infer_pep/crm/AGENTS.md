# Agent
: crm

## Scope
 This directory contains crm components for the module. It provides 2 classes and 3 functions.

## Classes
 and Functions

### BaseCRMImporter
 Abstract base class for CRM importers.

**Methods**:
- `connect(**kwargs) -> None`: Connect to the CRM data source.
- `fetch_data(last_sync_date: Optional[datetime]) -> List[Dict[str, Any]]`: Fetch raw data from the CRM.
- `transform_data(raw_data: List[Dict[str, Any]]) -> List[Customer]`: Transform raw data into Customer Pydantic models.
- `import_customers(last_sync_date: Optional[datetime], **kwargs) -> List[Customer]`: Orchestrates the import process: connect, fetch, transform.

### CSVCRMImporter
 Imports CRM data from a CSV file.

**Methods**:
- `connect(**kwargs) -> None`: Simulates opening the CSV file.
- `fetch_data(last_sync_date: Optional[datetime]) -> List[Dict[str, Any]]`: Reads data from the CSV file.
- `transform_data(raw_data: List[Dict[str, Any]]) -> List[Customer]`: Transforms CSV rows into Customer Pydantic models.

### clean_customer_data
 `clean_customer_data(customers: List[Customer]) -> List[Customer]` Performs cleaning operations on a list of Customer objects.

### enrich_customer_data
 `enrich_customer_data(customers: List[Customer], external_data_sources: dict) -> List[Customer]` Enriches customer data with calculated fields and organizational context.

### convert_customers_to_dataframe
 `convert_customers_to_dataframe(customers: List[Customer]) -> pd.DataFrame` Converts a list of Customer Pydantic models to a Pandas DataFrame

## Capabilities

- **2 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PEP/src/geo_infer_pep/crm`
- **Type**: Directory Node
