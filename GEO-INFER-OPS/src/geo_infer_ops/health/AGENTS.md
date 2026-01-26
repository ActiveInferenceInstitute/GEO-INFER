# Agent
: health ## Scope
 This directory contains health components for the module. It provides 3 classes and 0 functions. ## Classes
 and Functions ### HealthStatu
s
 Health status levels. ### HealthChec
k
 Represents a health check result. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert health check to dictionary. ### HealthChecke
r
 Health checker for GEO-INFER modules and services. **Methods**: - `register_check(name: str, check_func: Callable, async_check: bool) -> None`: Register a custom health check. - `get_health_status() -> Dict[str, Any]`: Get current health status (synchronous wrapper). - `get_health_history(limit: int, since: Optional[datetime]) -> List[Dict[str, Any]]`: Get health check history. ## Capabilities
 - **3 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-OPS/src/geo_infer_ops/health` - **Type**: Directory Node 