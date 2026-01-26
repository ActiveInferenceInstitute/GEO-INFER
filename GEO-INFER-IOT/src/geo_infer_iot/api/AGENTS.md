# Agent
: api ## Scope
 This directory contains api components for the module. It provides 3 classes and 0 functions. ## Classes
 and Functions ### BayesianInferenceAP
I
 API for Bayesian spatial inference operations. **Methods**: - `get_app() -> FastAPI`: Get the FastAPI application instance. ### SensorAP
I
 REST API for sensor management and data access. **Methods**: - `get_app() -> FastAPI`: Get the FastAPI application instance. - `run(host: str, port: int, **kwargs)`: Run the API server. ### StreamingAP
I
 WebSocket and streaming API for real-time sensor data. **Methods**: - `broadcast_measurement(measurement: Dict)`: Broadcast a measurement to subscribed clients. - `broadcast_spatial_inference(inference_result: Dict)`: Broadcast spatial inference results to subscribed clients. - `get_app() -> FastAPI`: Get the FastAPI application instance. ## Capabilities
 - **3 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-IOT/src/geo_infer_iot/api` - **Type**: Directory Node 