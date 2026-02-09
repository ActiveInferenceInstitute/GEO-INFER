# Agent: del_norte_county_synthetic

## Scope

Synthetic data variant of the Del Norte County analysis framework. Provides configuration
and dashboard infrastructure for testing and demonstration without live API dependencies.

## Capabilities

- **Dashboard Generation**: Interactive HTML dashboards from synthetic datasets
- **Configuration Management**: Analysis configs mirroring production del_norte_county
- **Demonstration Mode**: Realistic synthetic data for forest health, coastal, and fire risk

## Relationship to del_norte_county

This location mirrors the production `del_norte_county` implementation but uses synthetic
data generators instead of live CAL FIRE and NOAA API calls. Useful for:

- CI/CD pipelines with no external API access
- Development and testing of new analysis features
- Demonstrations and training materials

## Status

📄 Configuration and dashboards — references production code from `del_norte_county`.

## Integration

- **Location**: `GEO-INFER-PLACE/locations/del_norte_county_synthetic`
- **Type**: Location Node (synthetic variant)
- **Parent Implementation**: `del_norte_county`
