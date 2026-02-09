# Locations

## Overview

Place-based geospatial analysis configurations for specific geographic regions.
Each sub-directory contains location-specific documentation, data schemas,
analysis configurations, and (where implemented) runnable code.

## Location Index

| Location | Region | Status | Code | Key Focus Areas |
|----------|--------|--------|------|-----------------|
| [australia](australia/) | Continental | 📄 Documentation | — | Climate monitoring, biodiversity, drought, wildfire |
| [cascadia](cascadia/) | Pacific NW | ✅ Production | `cascadia_main.py` + `src/` | Agricultural land analysis, H3 fusion |
| [del_norte_county](del_norte_county/) | NW California | ✅ Production | `run_analysis.py` + dashboard | Forest health, coastal resilience, fire risk |
| [del_norte_county_synthetic](del_norte_county_synthetic/) | NW California | 📄 Documentation | Dashboard configs | Synthetic data variant of Del Norte |
| [houston](houston/) | Gulf Coast TX | 📄 Documentation | — | Open civic data, urban analytics |
| [siberia](siberia/) | Arctic Russia | 📄 Documentation | — | Permafrost, carbon cycle, Arctic climate |

## Adding a New Location

1. Create a sub-directory named with the location slug (e.g., `new_region/`)
2. Add a `README.md` describing the geographic context and research focus
3. Add a `requirements.txt` listing **only real, pip-installable** dependencies
4. Add an `AGENTS.md` describing the agent scope and capabilities
5. If implementing analysis code, follow the patterns in `del_norte_county/` or `cascadia/`
