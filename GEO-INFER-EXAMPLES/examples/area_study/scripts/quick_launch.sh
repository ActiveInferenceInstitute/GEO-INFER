#!/bin/bash

# Quick Launch Script for Area Study Dashboard
# This script directly runs streamlit without Python subprocess complexity

echo "🏛️ GEO-INFER Area Study Dashboard"
echo "================================================================"
echo "🚀 Starting dashboard with simple streamlit command..."
echo "🌐 Dashboard will be at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo "================================================================"
echo

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_SCRIPT="$SCRIPT_DIR/dashboard_app.py"

echo "📁 Script location: $DASHBOARD_SCRIPT"
echo "📋 Command: streamlit run $DASHBOARD_SCRIPT --server.port 8501 --server.address 0.0.0.0"
echo

# Run streamlit directly
streamlit run "$DASHBOARD_SCRIPT" \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --theme.base light \
    --browser.serverAddress localhost \
    --browser.serverPort 8501
