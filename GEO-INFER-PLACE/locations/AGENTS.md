# Agent: locations

## Scope

This agent manages the `locations` directory, which contains place-based geospatial
analysis configurations and implementations for specific geographic regions.

## Capabilities

- **Location Registry**: Maintains the index of all supported geographic locations
- **Configuration Management**: Location-specific analysis configs, data schemas, and requirements
- **Code Implementations**: Production-ready analysis pipelines (Cascadia, Del Norte County)
- **Documentation Standards**: README formatting, requirements accuracy, and data source cataloguing

## Supported Locations

| Location | Type | Agent Sub-Scope |
|----------|------|-----------------|
| `australia/` | Documentation | Continental climate, biodiversity, drought |
| `cascadia/` | Production Code | Agricultural H3 analysis, data fusion |
| `del_norte_county/` | Production Code | Forest health, coastal, fire risk |
| `del_norte_county_synthetic/` | Configuration | Synthetic data variant |
| `houston/` | Documentation | Open civic data, urban analytics |
| `siberia/` | Documentation | Permafrost, Arctic climate, carbon |

## Integration

- **Location**: `GEO-INFER-PLACE/locations`
- **Type**: Directory Node
- **Parent**: `GEO-INFER-PLACE`
- **Dependencies**: `geo_infer_place.core`, `geo_infer_place.utils`
