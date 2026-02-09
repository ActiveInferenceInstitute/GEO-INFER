# Agent
: visualizations

## Scope
 This directory contains visualizations components for the module. It provides 0 classes and 6 functions.

## Classes
 and Functions

### plot_customer_distribution_by_status
 `plot_customer_distribution_by_status(customers: List[Customer], output_dir: Path) -> Optional[str]` Generates a bar chart of customer distribution by status.

### plot_customer_distribution_by_source
 `plot_customer_distribution_by_source(customers: List[Customer], output_dir: Path) -> Optional[str]` Generates a bar chart of customer distribution by source.

### plot_headcount_by_department
 `plot_headcount_by_department(employees: List[Employee], output_dir: Path) -> Optional[str]` Generates a bar chart of active employee headcount by department.

### plot_gender_distribution
 `plot_gender_distribution(employees: List[Employee], output_dir: Path) -> Optional[str]` Generates a pie chart for gender distribution of active employees.

### plot_candidate_pipeline_by_status
 `plot_candidate_pipeline_by_status(candidates: List[Candidate], output_dir: Path) -> Optional[str]` Generates a bar chart of candidates by their current status in the pipeline.

### plot_time_to_hire_distribution
 `plot_time_to_hire_distribution(hired_candidates_with_tth_days: List[int], output_dir: Path) -> Optional[str]` Generates a histogram for Time to Hire distribution.

## Capabilities

- **6 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PEP/src/geo_infer_pep/visualizations`
- **Type**: Directory Node
