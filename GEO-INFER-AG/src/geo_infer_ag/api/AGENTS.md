# Agent
: api

## Scope
 This directory contains api components for the module. It provides 2 classes and 2 functions.

## Classes
 and Functions

### AgriculturalConfig
 Configuration for agricultural API.

### AgriculturalAPI
 API client for agricultural data and analysis.

**Methods**:
- `get_crop_data(crop_type: str, region: Optional[str], year: Optional[int]) -> Dict[str, Any]`: Get agricultural data for a specific crop.
- `get_soil_data(location: Dict[str, float], depth: Optional[float]) -> Dict[str, Any]`: Get soil data for a specific location.
- `get_weather_forecast(location: Dict[str, float], days: int) -> List[Dict[str, Any]]`: Get weather forecast for agricultural planning.
- `analyze_crop_yield(crop_type: str, location: Dict[str, float], soil_data: Dict[str, Any], weather_data: List[Dict[str, Any]]) -> Dict[str, Any]`: Analyze potential crop yield based on conditions.
- `get_precision_agriculture_data(field_id: str, sensor_type: Optional[str]) -> Dict[str, Any]`: Get precision agriculture sensor data.
- `optimize_irrigation(field_data: Dict[str, Any], weather_forecast: List[Dict[str, Any]]) -> Dict[str, Any]`: Optimize irrigation schedule based on field and weather data.

### create_agricultural_api
 `create_agricultural_api(config: Optional[AgriculturalConfig]) -> AgriculturalAPI` Create a AgriculturalAPI instance.

### get_crop_recommendations
 `get_crop_recommendations(location: Dict[str, float], soil_data: Dict[str, Any]) -> List[str]` Get crop recommendations for a location.

## Capabilities

- **2 classes** for core functionality
- **2 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-AG/src/geo_infer_ag/api`
- **Type**: Directory Node
