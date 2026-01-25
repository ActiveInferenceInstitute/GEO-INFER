#!/bin/bash
# Run Cascadia Analysis using uv for environment management

# Ensure dependencies are installed
echo "📦 Syncing dependencies with uv..."
uv sync --extra viz

# Clean synthetic cache to force real data usage (workaround for flag issue)
echo "🧹 Cleaning synthetic data cache..."
find output -name "synthetic_*.geojson" -delete 2>/dev/null

# Run analysis
echo "🚀 Starting Cascadia Analysis..."
uv run python cascadia_main.py \
    --modules zoning,ownership,improvements,ground_water,surface_water,water_rights,power_source,mortgage_debt \
    --skip-cache \
    --generate-dashboard \
    --spatial-analysis \
    "$@"
