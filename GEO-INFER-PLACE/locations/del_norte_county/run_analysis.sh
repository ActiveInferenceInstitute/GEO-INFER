#!/bin/bash
set -e

# Change directory to the script location's parent (GEO-INFER-PLACE root or similar context)
# Assuming this script is in locations/del_norte_county/ and we run from project root or relative
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../../.."

echo "🚀 Starting Del Norte County Analysis Pipeline..."
echo "📂 Project Root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Ensure dependencies are installed (optional if using uv)
# uv sync

echo "📊 Running analysis..."
uv run \
  --with-editable ./GEO-INFER-SPACE \
  --with-editable ./GEO-INFER-PLACE \
  --with-requirements GEO-INFER-PLACE/locations/del_norte_county/requirements.txt \
  python3 GEO-INFER-PLACE/locations/del_norte_county/run_analysis.py

echo "✅ Analysis complete! Dashboard generated."
echo "🌐 View at: file://$PROJECT_ROOT/GEO-INFER-PLACE/locations/del_norte_county/del_norte_dashboard/"
