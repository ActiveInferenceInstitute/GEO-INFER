# Agent
: talent

## Scope
 This directory contains talent components for the module. It provides 2 classes and 4 functions.

## Classes
 and Functions

### BaseTalentImporter
 Abstract base class for Talent data importers.

**Methods**:
- `connect(**kwargs) -> None`: Connect to the Talent data source (e.g., ATS API).
- `fetch_candidates(last_sync_date: Optional[datetime], requisition_id: Optional[str]) -> List[Dict[str, Any]]`: Fetch raw candidate data.
- `transform_candidates(raw_data: List[Dict[str, Any]]) -> List[Candidate]`: Transform raw data into Candidate Pydantic models.
- `fetch_requisitions(last_sync_date: Optional[datetime], status: Optional[str]) -> List[Dict[str, Any]]`: Fetch raw job requisition data.
- `transform_requisitions(raw_data: List[Dict[str, Any]]) -> List[JobRequisition]`: Transform raw data into JobRequisition Pydantic models.
- `import_candidates(last_sync_date: Optional[datetime], requisition_id: Optional[str], **kwargs) -> List[Candidate]`:
- `import_requisitions(last_sync_date: Optional[datetime], status: Optional[str], **kwargs) -> List[JobRequisition]`:

### CSVTalentImporter
 Imports Talent data from CSV files.

**Methods**:
- `connect(**kwargs) -> None`:
- `fetch_candidates(last_sync_date: Optional[datetime], requisition_id: Optional[str]) -> List[Dict[str, Any]]`:
- `transform_candidates(raw_data: List[Dict[str, Any]]) -> List[Candidate]`:
- `fetch_requisitions(last_sync_date: Optional[datetime], status: Optional[str]) -> List[Dict[str, Any]]`:
- `transform_requisitions(raw_data: List[Dict[str, Any]]) -> List[JobRequisition]`:

### clean_candidate_data
 `clean_candidate_data(candidates: List[Candidate]) -> List[Candidate]` Performs cleaning operations on a list of Candidate objects.

### enrich_candidate_data
 `enrich_candidate_data(candidates: List[Candidate], requisitions: List[JobRequisition]) -> List[Candidate]` Enriches candidate data with calculated fields and requisition context.

### convert_candidates_to_dataframe
 `convert_candidates_to_dataframe(candidates: List[Candidate]) -> pd.DataFrame` Converts a list of Candidate Pydantic models to a Pandas DataFrame.

### convert_requisitions_to_dataframe
 `convert_requisitions_to_dataframe(requisitions: List[JobRequisition]) -> pd.DataFrame` Converts a list of JobRequisition Pydantic models to a Pandas DataFrame.

## Capabilities

- **2 classes** for core functionality
- **4 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PEP/src/geo_infer_pep/talent`
- **Type**: Directory Node
