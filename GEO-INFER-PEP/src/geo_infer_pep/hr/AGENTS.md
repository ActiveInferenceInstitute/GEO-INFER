# Agent
: hr

## Scope
 This directory contains hr components for the module. It provides 2 classes and 3 functions.

## Classes
 and Functions

### BaseHRImporter
 Abstract base class for HR data importers.

**Methods**:
- `connect(**kwargs) -> None`: Connect to the HR data source.
- `fetch_employees(last_sync_date: Optional[datetime]) -> List[Dict[str, Any]]`: Fetch raw employee data from the HR source.
- `transform_employees(raw_data: List[Dict[str, Any]]) -> List[Employee]`: Transform raw employee data into Employee Pydantic models.
- `import_employees(last_sync_date: Optional[datetime], **kwargs) -> List[Employee]`: Orchestrates the import process: connect, fetch, transform for employees.

### CSVHRImporter
 Imports HR data from a CSV file.

**Methods**:
- `connect(**kwargs) -> None`:
- `fetch_employees(last_sync_date: Optional[datetime]) -> List[Dict[str, Any]]`:
- `transform_employees(raw_data: List[Dict[str, Any]]) -> List[Employee]`:

### clean_employee_data
 `clean_employee_data(employees: List[Employee]) -> List[Employee]` Performs cleaning operations on a list of Employee objects.

### enrich_employee_data
 `enrich_employee_data(employees: List[Employee], org_data: dict) -> List[Employee]` Enriches employee data with calculated fields and organizational context.

### convert_employees_to_dataframe
 `convert_employees_to_dataframe(employees: List[Employee]) -> pd.DataFrame` Converts a list of Employee Pydantic models to a Pandas DataFrame.

## Capabilities

- **2 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PEP/src/geo_infer_pep/hr`
- **Type**: Directory Node
