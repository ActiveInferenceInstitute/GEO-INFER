# Agent: cascadia/src

## Scope

Core source code for the Cascadia agricultural analysis pipeline.

## Modules

### `core/`

- `enhanced_data_manager.py` — Cached data management with intelligent TTL
- `enhanced_h3_fusion.py` — H3 v4 geospatial data fusion engine
- `enhanced_logging.py` — Structured logging configuration
- `real_data_acquisition.py` — Multi-source API data fetching
- `data_processor.py` — Data transformation and export
- `visualization/comprehensive_visualization.py` — Dashboard generation

### `config/`

- Analysis configuration and schema definitions

### `data_modules/`

- Location-specific data module definitions

## Integration

- **Location**: `GEO-INFER-PLACE/locations/cascadia/src`
- **Type**: Source Code Directory
- **Entry Point**: `cascadia_main.py` (parent directory)
