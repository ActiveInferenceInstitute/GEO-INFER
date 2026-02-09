# Agent
: api

## Scope
 This directory contains api components for the module. It provides 0 classes and 23 functions.

## Classes
 and Functions

### create_cog_api_app
 `create_cog_api_app(config: Optional[Dict[str, Any]]) -> Optional[Flask]` Create and configure the GEO-INFER-COG REST API application.

### register_api_routes
 `register_api_routes(app: Flask) -> None` Register all API routes for the COG module.

### register_error_handlers
 `register_error_handlers(app: Flask) -> None` Register error handlers for the API.

### run_api_server
 `run_api_server(host: str, port: int, debug: bool) -> None` Run the COG API server.

### health_check
 `health_check()` Health check endpoint.

### analyze_text
 `analyze_text()` Analyze text for spatial content.

### extract_entities
 `extract_entities()` Extract spatial entities from text.

### analyze_sentiment
 `analyze_sentiment()` Analyze sentiment in spatial text.

### perform_inference
 `perform_inference()` Perform cognitive inference on spatial data.

### extract_knowledge
 `extract_knowledge()` Extract structured knowledge from data.

### analyze_decision
 `analyze_decision()` Analyze decision scenario.

### create_visualization
 `create_visualization()` Create cognitively optimized visualization.

### process_cognitive
 `process_cognitive()` Process spatial data through cognitive pipeline.

### get_user_profile
 `get_user_profile(user_id)` Get user cognitive profile.

### create_user_profile
 `create_user_profile(user_id)` Create or update user cognitive profile.

### get_system_status
 `get_system_status()` Get system status and component health.

### get_system_metrics
 `get_system_metrics()` Get system performance metrics.

### bad_request
 `bad_request(error)`

### not_found
 `not_found(error)`

### method_not_allowed
 `method_not_allowed(error)`

### payload_too_large
 `payload_too_large(error)`

### internal_server_error
 `internal_server_error(error)`

### handle_exception
 `handle_exception(error)`

## Capabilities

- **23 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-COG/src/geo_infer_cog/api`
- **Type**: Directory Node
