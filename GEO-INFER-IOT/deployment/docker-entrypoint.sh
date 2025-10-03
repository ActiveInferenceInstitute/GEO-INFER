#!/bin/bash
set -e

# GEO-INFER-IOT Docker Entry Point Script
# This script handles initialization and startup of the IoT service

echo "Starting GEO-INFER-IOT service..."

# Function to handle graceful shutdown
cleanup() {
    echo "Received shutdown signal, stopping services..."
    # Stop background processes
    kill 0
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create necessary directories if they don't exist
mkdir -p /app/logs /app/data

# Set default configuration path if not provided
CONFIG_PATH=${CONFIG_PATH:-/app/config/iot_config.yaml}

# Check if configuration file exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Configuration file not found at $CONFIG_PATH, using defaults"
    # Create default configuration if needed
    cat > "$CONFIG_PATH" << EOF
# Default IoT Configuration
project:
  name: "GEO-INFER-IOT Docker Deployment"
  version: "1.0.0"

# MQTT Configuration
protocols:
  mqtt:
    enabled: true
    broker_host: "localhost"
    broker_port: 1883

# API Configuration
api:
  rest:
    enabled: true
    host: "0.0.0.0"
    port: 8000
    workers: 4

  websocket:
    enabled: true
    port: 8001

# Logging Configuration
logging:
  level: "INFO"
  format: "json"
  handlers:
    - type: "console"
    - type: "file"
      filename: "/app/logs/application.log"

# Performance Configuration
performance:
  system_metrics_interval_seconds: 10
  iot_metrics_interval_seconds: 5
  cpu_threshold: 80.0
  memory_threshold: 85.0
EOF
fi

# Set Python path
export PYTHONPATH=/app/src:$PYTHONPATH

# Initialize the IoT system if needed
echo "Initializing IoT system..."

# Check if database services are available (for production deployments)
if [ -n "$POSTGRES_HOST" ] || [ -n "$INFLUXDB_HOST" ]; then
    echo "Waiting for database services..."
    # Add database connection checks here
fi

# Start performance monitoring
echo "Starting performance monitoring..."
python -c "
from geo_infer_iot.performance import start_performance_monitoring
import sys
sys.path.insert(0, '/app/src')
start_performance_monitoring()
print('Performance monitoring started')
"

# Execute the main command
echo "Starting main application: $@"
exec "$@" &

# Wait for the main process
wait $!
