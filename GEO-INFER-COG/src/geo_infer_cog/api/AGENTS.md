# Agent
: api ## Scope
 This directory contains api components for the module. It provides 0 classes and 23 functions. ## Classes
 and Functions ### create_cog_api_ap
p
 `create_cog_api_app(config: Optional[Dict[str, Any]]) -> Optional[Flask]` Create and configure the GEO-INFER-COG REST API application. ### register_api_route
s
 `register_api_routes(app: Flask) -> None` Register all API routes for the COG module. ### register_error_handler
s
 `register_error_handlers(app: Flask) -> None` Register error handlers for the API. ### run_api_serve
r
 `run_api_server(host: str, port: int, debug: bool) -> None` Run the COG API server. ### health_chec
k
 `health_check()` Health check endpoint. ### analyze_tex
t
 `analyze_text()` Analyze text for spatial content. ### extract_entitie
s
 `extract_entities()` Extract spatial entities from text. ### analyze_sentimen
t
 `analyze_sentiment()` Analyze sentiment in spatial text. ### perform_inferenc
e
 `perform_inference()` Perform cognitive inference on spatial data. ### extract_knowledg
e
 `extract_knowledge()` Extract structured knowledge from data. ### analyze_decisio
n
 `analyze_decision()` Analyze decision scenario. ### create_visualizatio
n
 `create_visualization()` Create cognitively optimized visualization. ### process_cognitiv
e
 `process_cognitive()` Process spatial data through cognitive pipeline. ### get_user_profil
e
 `get_user_profile(user_id)` Get user cognitive profile. ### create_user_profil
e
 `create_user_profile(user_id)` Create or update user cognitive profile. ### get_system_statu
s
 `get_system_status()` Get system status and component health. ### get_system_metric
s
 `get_system_metrics()` Get system performance metrics. ### bad_reques
t
 `bad_request(error)` ### not_foun
d
 `not_found(error)` ### method_not_allowe
d
 `method_not_allowed(error)` ### payload_too_larg
e
 `payload_too_large(error)` ### internal_server_erro
r
 `internal_server_error(error)` ### handle_exceptio
n
 `handle_exception(error)` ## Capabilities
 - **23 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-COG/src/geo_infer_cog/api` - **Type**: Directory Node 