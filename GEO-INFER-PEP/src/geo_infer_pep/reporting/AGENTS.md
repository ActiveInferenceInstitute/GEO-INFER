# Agent
: reporting

## Scope
 This directory contains reporting components for the module. It provides 0 classes and 10 functions.

## Classes
 and Functions

### generate_customer_segmentation_report
 `generate_customer_segmentation_report(customers: List[Customer]) -> Dict[str, Any]` Generates a report on customer segmentation.

### generate_lead_conversion_report
 `generate_lead_conversion_report(customers: List[Customer]) -> Dict[str, Any]` Generates a report on lead conversion rates.

### get_quarterly_metrics
 `get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]` Simulates fetching CRM quarterly metrics.

### create_quarterly_overview
 `create_quarterly_overview(hr_metrics: Dict, crm_metrics: Dict, talent_metrics: Dict) -> str` Simulates the creation of a quarterly overview report.

### generate_headcount_report
 `generate_headcount_report(employees: List[Employee], group_by: List[str]) -> Dict[str, Any]` Generates a headcount report, optionally grouped by specified fields (e.g., department, location).

### generate_diversity_report
 `generate_diversity_report(employees: List[Employee], diversity_fields: List[str]) -> Dict[str, Any]` Generates a diversity report based on specified fields (e.g., gender, nationality).

### get_quarterly_metrics
 `get_quarterly_metrics(quarter: str, year: int, employees: List[Employee]) -> Dict[str, Any]` Calculates real HR quarterly metrics from employee data.

### generate_candidate_pipeline_report
 `generate_candidate_pipeline_report(candidates: List[Candidate], requisitions: Optional[List[JobRequisition]]) -> Dict[str, Any]` Generates a report on the current candidate pipeline status.

### calculate_time_to_hire
 `calculate_time_to_hire(hired_candidates: List[Candidate]) -> Dict[str, Any]` Calculates average, min, max time to hire for candidates who reached 'HIRED' status.

### get_quarterly_metrics
 `get_quarterly_metrics(quarter: str, year: int) -> Dict[str, Any]` Simulates fetching Talent quarterly metrics.

## Capabilities

- **10 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PEP/src/geo_infer_pep/reporting`
- **Type**: Directory Node
