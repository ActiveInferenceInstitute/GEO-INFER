# GEO-INFER-PEP Source Code

This directory contains the core implementation of the GEO-INFER-PEP module, providing people, engagement, and performance management capabilities for the GEO-INFER framework.

## Directory Structure

```
src/
├── geo_infer_pep/
│   ├── __init__.py                    # Package initialization
│   ├── api/                          # API interfaces and endpoints
│   │   ├── __init__.py
│   │   ├── crm_endpoints.py          # CRM API endpoints
│   │   ├── hr_endpoints.py           # HR API endpoints
│   │   └── talent_endpoints.py       # Talent management endpoints
│   ├── core/                         # Core business logic
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Workflow orchestration
│   │   ├── pep_engine.py             # Main PEP engine
│   │   └── validator.py               # Data validation
│   ├── crm/                          # Customer relationship management
│   │   ├── __init__.py
│   │   ├── importer.py               # CRM data import
│   │   └── transformer.py            # CRM data transformation
│   ├── hr/                           # Human resources management
│   │   ├── __init__.py
│   │   ├── importer.py               # HR data import
│   │   └── transformer.py            # HR data transformation
│   ├── models/                       # Data models and schemas
│   │   ├── __init__.py
│   │   ├── crm_models.py             # CRM data models
│   │   ├── hr_models.py              # HR data models
│   │   └── talent_models.py          # Talent data models
│   ├── reporting/                    # Reporting and analytics
│   │   ├── __init__.py
│   │   ├── crm_reports.py            # CRM reporting
│   │   ├── hr_reports.py             # HR reporting
│   │   └── talent_reports.py         # Talent reporting
│   ├── talent/                       # Talent acquisition and management
│   │   ├── __init__.py
│   │   ├── importer.py               # Talent data import
│   │   └── transformer.py            # Talent data transformation
│   ├── utils/                        # Utility functions
│   │   └── __init__.py
│   └── visualizations/               # Data visualization components
│       ├── __init__.py
│       ├── crm_visuals.py            # CRM visualizations
│       ├── hr_visuals.py             # HR visualizations
│       └── talent_visuals.py         # Talent visualizations
```

## Core Components

### PEP Engine

**Location**: `core/pep_engine.py`

The main People, Engagement, and Performance engine:

```python
from geo_infer_pep.core.pep_engine import PEPEngine

# Initialize PEP engine
pep_engine = PEPEngine()

# Import organizational data
pep_engine.import_hr_data('hr_data.csv')
pep_engine.import_crm_data('crm_data.csv')

# Generate comprehensive dashboards
dashboards = pep_engine.generate_all_dashboards()

# Process onboarding workflows
onboarding_result = pep_engine.process_onboarding_workflow(candidate_data)
```

### Workflow Orchestrator

**Location**: `core/orchestrator.py`

Manages complex business workflows:

```python
from geo_infer_pep.core.orchestrator import PEPOrchestrator

# Create workflow orchestrator
orchestrator = PEPOrchestrator(pep_engine)

# Create employee onboarding workflow
workflow_id = orchestrator.create_employee_onboarding_workflow(candidate_id)

# Execute workflow
result = orchestrator.execute_workflow(workflow_id)

# Monitor workflow status
status = orchestrator.get_workflow_status(workflow_id)
```

### Data Validators

**Location**: `core/validator.py`

Comprehensive data validation for all PEP data types:

```python
from geo_infer_pep.core.validator import PEPValidator

# Initialize validator
validator = PEPValidator()

# Validate employee data
employee_result = validator.validate_employee(employee_data, strict=True)

# Validate customer data
customer_result = validator.validate_customer(customer_data)

# Validate candidate data
candidate_result = validator.validate_candidate(candidate_data)
```

## API Layer

### CRM Endpoints

**Location**: `api/crm_endpoints.py`

Customer relationship management API:

```python
from geo_infer_pep.api.crm_endpoints import router as crm_router

# Upload customer data
@app.post("/crm/upload/csv")
async def upload_crm_data(file: UploadFile):
    return await import_crm_csv(file)

# Get customer reports
@app.get("/crm/reports/segmentation")
async def get_customer_segmentation():
    return generate_customer_segmentation_report()
```

### HR Endpoints

**Location**: `api/hr_endpoints.py`

Human resources management API:

```python
from geo_infer_pep.api.hr_endpoints import router as hr_router

# Get employee information
@app.get("/hr/employees")
async def get_employees():
    return get_all_employees()

# Generate HR reports
@app.get("/hr/reports/headcount")
async def get_headcount_report():
    return generate_headcount_report()
```

### Talent Endpoints

**Location**: `api/talent_endpoints.py`

Talent acquisition and management API:

```python
from geo_infer_pep.api.talent_endpoints import router as talent_router

# Get candidate pipeline
@app.get("/talent/candidates")
async def get_candidates():
    return get_all_candidates()

# Generate talent reports
@app.get("/talent/reports/pipeline")
async def get_pipeline_report():
    return generate_candidate_pipeline_report()
```

## Data Models

### CRM Models

**Location**: `models/crm_models.py`

Customer relationship management data structures:

```python
from geo_infer_pep.models.crm_models import Customer, InteractionLog

# Create customer
customer = Customer(
    customer_id="CUST_001",
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    company="Example Corp"
)

# Log customer interaction
interaction = InteractionLog(
    channel="email",
    summary="Product inquiry",
    agent_id="agent_001"
)
```

### HR Models

**Location**: `models/hr_models.py`

Human resources data structures:

```python
from geo_infer_pep.models.hr_models import Employee, EmploymentStatus

# Create employee
employee = Employee(
    employee_id="EMP_001",
    first_name="Jane",
    last_name="Smith",
    email="jane.smith@company.com",
    employment_status=EmploymentStatus.ACTIVE
)
```

### Talent Models

**Location**: `models/talent_models.py`

Talent acquisition and management data structures:

```python
from geo_infer_pep.models.talent_models import Candidate, JobRequisition

# Create candidate
candidate = Candidate(
    candidate_id="CAND_001",
    first_name="Alice",
    last_name="Johnson",
    email="alice.johnson@email.com",
    skills=["Python", "Machine Learning", "Geospatial"]
)

# Create job requisition
requisition = JobRequisition(
    requisition_id="REQ_001",
    job_title="Senior Data Scientist",
    department="Data Science"
)
```

## Data Import/Export

### CRM Data Import

**Location**: `crm/importer.py`

```python
from geo_infer_pep.crm.importer import CSVCRMImporter

# Import CRM data from CSV
importer = CSVCRMImporter('customers.csv')
customers = importer.import_customers()
```

### HR Data Import

**Location**: `hr/importer.py`

```python
from geo_infer_pep.hr.importer import CSVHRImporter

# Import HR data from CSV
importer = CSVHRImporter('employees.csv')
employees = importer.import_employees()
```

### Talent Data Import

**Location**: `talent/importer.py`

```python
from geo_infer_pep.talent.importer import CSVTalentImporter

# Import talent data from CSV files
importer = CSVTalentImporter('candidates.csv', 'requisitions.csv')
candidates = importer.import_candidates()
requisitions = importer.import_requisitions()
```

## Reporting and Analytics

### CRM Reporting

**Location**: `reporting/crm_reports.py`

```python
from geo_infer_pep.reporting.crm_reports import generate_customer_segmentation_report

# Generate customer segmentation report
report = generate_customer_segmentation_report(customers)
```

### HR Reporting

**Location**: `reporting/hr_reports.py`

```python
from geo_infer_pep.reporting.hr_reports import generate_headcount_report

# Generate headcount report
report = generate_headcount_report(employees)
```

### Talent Reporting

**Location**: `reporting/talent_reports.py`

```python
from geo_infer_pep.reporting.talent_reports import generate_candidate_pipeline_report

# Generate candidate pipeline report
report = generate_candidate_pipeline_report(candidates)
```

## Visualization Components

### CRM Visualizations

**Location**: `visualizations/crm_visuals.py`

```python
from geo_infer_pep.visualizations.crm_visuals import plot_customer_distribution_by_status

# Create customer status distribution chart
chart_path = plot_customer_distribution_by_status(customers)
```

### HR Visualizations

**Location**: `visualizations/hr_visuals.py`

```python
from geo_infer_pep.visualizations.hr_visuals import plot_headcount_by_department

# Create headcount by department chart
chart_path = plot_headcount_by_department(employees)
```

### Talent Visualizations

**Location**: `visualizations/talent_visuals.py`

```python
from geo_infer_pep.visualizations.talent_visuals import plot_candidate_pipeline_by_status

# Create candidate pipeline status chart
chart_path = plot_candidate_pipeline_by_status(candidates)
```

## Integration Points

The PEP module integrates with other GEO-INFER modules:

- **GEO-INFER-SPACE**: Spatial analysis for workforce distribution and customer location analysis
- **GEO-INFER-TIME**: Temporal analysis for employee lifecycle and performance trends
- **GEO-INFER-DATA**: Data management for HR, CRM, and talent datasets
- **GEO-INFER-API**: RESTful interfaces for external integration
- **GEO-INFER-APP**: User interfaces for HR, CRM, and talent management
- **GEO-INFER-ORG**: Organizational structure and governance integration

## Development Guidelines

### Adding New Features

1. Define data models in appropriate `models/` subdirectory
2. Implement business logic in `core/` modules
3. Add API endpoints in `api/` directory
4. Create comprehensive tests
5. Update documentation

### Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings
- Write unit tests for all new functionality
- Follow established patterns from existing modules

### Testing

Run the PEP test suite:
```bash
python -m pytest tests/
```

Run specific component tests:
```bash
python -m pytest tests/core/test_pep_engine.py
```

## Dependencies

Core dependencies managed through main GEO-INFER framework:

- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `pydantic`: Data validation and serialization
- `fastapi`: API framework
- `sqlalchemy`: Database ORM (optional)
- `matplotlib`: Visualization (optional)

## Configuration

Configure PEP module in `config/pep_config.yaml`:

```yaml
pep:
  data_sources:
    hr_file: "data/hr_data.csv"
    crm_file: "data/crm_data.csv"
    talent_file: "data/talent_data.csv"

  api:
    host: "0.0.0.0"
    port: 8002

  workflows:
    onboarding_enabled: true
    performance_review_enabled: true
    learning_management_enabled: true
```

## Performance Considerations

- Use efficient data structures for large datasets
- Implement caching for frequently accessed data
- Optimize database queries when using persistent storage
- Consider pagination for large result sets
- Monitor memory usage with large HR/CRM datasets

