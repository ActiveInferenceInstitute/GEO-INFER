#!/bin/bash
# Run Cascadia Analysis using uv for environment management

# Ensure dependencies are installed
echo "📦 Syncing dependencies with uv..."
uv sync --extra viz

# Run analysis
echo "🚀 Starting Cascadia Analysis..."
uv run python cascadia_main.py \
    --modules zoning,ownership,improvements,ground_water,surface_water,water_rights,power_source,mortgage_debt \
    --skip-cache \
    --generate-dashboard \
    --spatial-analysis \
    "$@"

# --- Bioregion mode (ecological overview, H3 res 7, ecology module, HTTP server) ---
# Uncomment to run bioregion analysis:
# uv run python cascadia_main.py \
#     --bioregion \
#     --modules ecology,zoning,ground_water,surface_water \
#     --output-dir output/ \
#     --generate-dashboard \
#     --serve \
#     --server-port 8765
