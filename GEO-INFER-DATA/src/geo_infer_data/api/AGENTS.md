# Agent
: api ## Scope
 This agent handles REST API and service interfaces for GEO-INFER-DATA providing programmatic access to data management operations. ## Implementation
 Status ### Currentl
y
 Implemented - ✅ **DataAPI**: REST API server with FastAPI for data access and management - ✅ **DatasetAPI**: Dataset-specific API endpoints - ✅ **DataService**: Core data service for dataset management and operations ## Agent
 Capabilities ### 1
. REST API Server ```python from geo_infer_data.api import DataAPI # Initialize and start API server api = DataAPI( config_path='config/local.yaml', host='0.0.0.0', port=8001, enable_cors=True ) # Start server api.start() # API endpoints available: # GET /datasets - List datasets # POST /datasets - Create dataset # GET /datasets/{id}/data - Get dataset data # POST /data/ingest/multi-source - Multi-source ingestion # POST /data/etl/execute - Execute ETL pipeline # GET /health - Health check ``` ### 2
. Data Service ```python from geo_infer_data.api import DataService # Initialize data service service = DataService( storage_service=storage, quality_service=quality_manager ) # List datasets datasets = await service.list_datasets( filters={'type': 'vector'}, limit=50, offset=0 ) # Get dataset data data = await service.get_dataset_data( dataset_id='dataset_123', bbox=[-122.5, 37.7, -122.3, 37.9] ) # Create dataset dataset_id = await service.create_dataset( metadata=dataset_metadata, data=geodataframe ) ``` ### 3
. Dataset API Operations ```python from geo_infer_data.api import DatasetAPI # Initialize dataset API dataset_api = DatasetAPI(data_service=service) # Get dataset metadata metadata = await dataset_api.get_metadata('dataset_123') # Update dataset updated = await dataset_api.update_dataset( dataset_id='dataset_123', updates={'description': 'Updated description'} ) # Delete dataset await dataset_api.delete_dataset('dataset_123') ``` ## Function
 Signatures ### DataAP
I
 - `__init__(config_path: Optional[Path] = None, host: str = "0.0.0.0", port: int = 8001, enable_cors: bool = True)` - `start(reload: bool = False) -> None`: Start the API server - `stop() -> None`: Stop the API server - `_setup_routes() -> None`: Setup API routes ### DataServic
e
 - `__init__(storage_service: Optional[AdaptiveDataStorage] = None, quality_service: Optional[DataQualityManager] = None)` - `list_datasets(filters: Optional[Dict] = None, limit: int = 50, offset: int = 0) -> List[Dataset]` - `get_dataset_data(dataset_id: str, bbox: Optional[List[float]] = None) -> Any` - `create_dataset(metadata: DatasetMetadata, data: Any) -> str` - `get_access_patterns(dataset_id: Optional[str] = None) -> Dict[str, Any]` - `get_storage_stats() -> Dict[str, Any]` - `optimize_performance() -> Dict[str, Any]` ### DatasetAP
I
 - `get_metadata(dataset_id: str) -> DatasetMetadata` - `update_dataset(dataset_id: str, updates: Dict[str, Any]) -> Dataset` - `delete_dataset(dataset_id: str) -> None` ## API
 Endpoints ### Dataset
s
 - `GET /api/v1/datasets` - List datasets with filtering and pagination - `POST /api/v1/datasets` - Create dataset - `GET /api/v1/datasets/{id}` - Get dataset metadata - `PUT /api/v1/datasets/{id}` - Update dataset - `DELETE /api/v1/datasets/{id}` - Delete dataset - `GET /api/v1/datasets/{id}/data` - Get dataset data ### Dat
a
 Operations - `POST /api/v1/data/ingest/multi-source` - Multi-source data ingestion - `POST /api/v1/data/etl/execute` - Execute ETL pipeline - `GET /api/v1/data/quality/{dataset_id}` - Get quality report ### Syste
m
 - `GET /api/v1/health` - Health check - `GET /api/v1/stats` - Storage statistics ## Integration
 - **Location**: `GEO-INFER-DATA/src/geo_infer_data/api` - **Dependencies**: `fastapi`, `uvicorn`, `geo_infer_data.core`, `geo_infer_data.models` - **Used By**: External applications, web interfaces, other GEO-INFER modules - **Provides**: REST API interface for data management operations --- This AGENTS.md documents REST API and service interfaces for GEO-INFER-DATA. 