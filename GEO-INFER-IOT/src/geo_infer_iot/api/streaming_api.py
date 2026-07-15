"""
Streaming API Module

This module provides WebSocket and streaming API endpoints for real-time
sensor data streaming and live monitoring capabilities.
"""

import logging
import asyncio
import json
from typing import Dict, Optional, Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Optional imports for enhanced functionality
try:
    from geo_infer_iot.core.ingestion import IoTDataIngestion

    HAS_INGESTION = True
except ImportError:
    HAS_INGESTION = False

logger = logging.getLogger(__name__)


class StreamingAPI:
    """
    WebSocket and streaming API for real-time sensor data.

    Provides real-time data streaming capabilities including:
    - Live sensor data feeds via WebSocket
    - Real-time spatial inference updates
    - Live anomaly detection alerts
    - Streaming data export capabilities
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.app = FastAPI(title="GEO-INFER-IOT Streaming API", version="1.0.0")

        # WebSocket connection management
        self.active_connections: Set[WebSocket] = set()
        self.sensor_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.spatial_subscriptions: Dict[str, Set[WebSocket]] = {}

        # Initialize ingestion if available
        if HAS_INGESTION:
            self.ingestion = IoTDataIngestion(None, config)
        else:
            self.ingestion = None

        # Setup API routes
        self._setup_routes()

        logger.info("StreamingAPI initialized")

    def _setup_routes(self):
        """Setup API routes and WebSocket endpoints."""

        @self.app.get("/")
        async def root():
            """API root endpoint."""
            return {
                "service": "GEO-INFER-IOT Streaming API",
                "version": "1.0.0",
                "status": "operational",
                "websocket_endpoint": "/ws/sensor-stream",
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.websocket("/ws/sensor-stream")
        async def sensor_stream_websocket(websocket: WebSocket):
            """WebSocket endpoint for real-time sensor data streaming."""
            await websocket.accept()

            # Add to active connections
            self.active_connections.add(websocket)

            try:
                # Wait for subscription message
                subscription_data = await websocket.receive_text()
                subscription = json.loads(subscription_data)

                sensor_ids = subscription.get("sensor_ids", [])
                h3_indices = subscription.get("h3_indices", [])

                # Register subscriptions
                for sensor_id in sensor_ids:
                    if sensor_id not in self.sensor_subscriptions:
                        self.sensor_subscriptions[sensor_id] = set()
                    self.sensor_subscriptions[sensor_id].add(websocket)

                for h3_index in h3_indices:
                    if h3_index not in self.spatial_subscriptions:
                        self.spatial_subscriptions[h3_index] = set()
                    self.spatial_subscriptions[h3_index].add(websocket)

                # Send confirmation
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "subscription_confirmed",
                            "sensor_ids": sensor_ids,
                            "h3_indices": h3_indices,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

                # Keep connection alive and forward data
                while True:
                    # In a real implementation, this would listen for new measurements
                    # and forward them to subscribed clients
                    await asyncio.sleep(1)

                    # Example: Send periodic heartbeat
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "heartbeat",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    )

            except WebSocketDisconnect:
                # Remove from all subscriptions
                for sensor_connections in self.sensor_subscriptions.values():
                    sensor_connections.discard(websocket)

                for spatial_connections in self.spatial_subscriptions.values():
                    spatial_connections.discard(websocket)

                self.active_connections.discard(websocket)

            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.active_connections.discard(websocket)

        @self.app.get("/streams")
        async def list_streams():
            """List available data streams."""
            streams = {
                "sensor_data_stream": {
                    "type": "sensor_measurements",
                    "format": "json",
                    "real_time": True,
                    "websocket_endpoint": "/ws/sensor-stream",
                    "description": "Real-time sensor measurement stream",
                },
                "spatial_inference_stream": {
                    "type": "spatial_predictions",
                    "format": "json",
                    "real_time": True,
                    "websocket_endpoint": "/ws/spatial-stream",
                    "description": "Real-time spatial inference results",
                },
                "anomaly_alert_stream": {
                    "type": "anomaly_alerts",
                    "format": "json",
                    "real_time": True,
                    "websocket_endpoint": "/ws/anomaly-stream",
                    "description": "Real-time anomaly detection alerts",
                },
            }

            return {
                "streams": streams,
                "total_streams": len(streams),
                "active_connections": len(self.active_connections),
            }

        @self.app.get("/subscriptions")
        async def get_subscriptions():
            """Get current subscription status."""
            return {
                "active_connections": len(self.active_connections),
                "sensor_subscriptions": {
                    sensor_id: len(connections)
                    for sensor_id, connections in self.sensor_subscriptions.items()
                },
                "spatial_subscriptions": {
                    h3_index: len(connections)
                    for h3_index, connections in self.spatial_subscriptions.items()
                },
                "timestamp": datetime.now().isoformat(),
            }

    def broadcast_measurement(self, measurement: Dict):
        """Broadcast a new measurement to subscribed clients."""
        # This would be called when new measurements are ingested
        sensor_id = measurement.get("sensor_id")
        h3_index = measurement.get("h3_index")

        # Send to sensor-specific subscribers
        if sensor_id in self.sensor_subscriptions:
            message = {
                "type": "sensor_measurement",
                "data": measurement,
                "timestamp": datetime.now().isoformat(),
            }

            # Send to all subscribers for this sensor
            for websocket in list(self.sensor_subscriptions[sensor_id]):
                try:
                    asyncio.create_task(websocket.send_text(json.dumps(message)))
                except Exception:
                    # Remove disconnected clients
                    self.sensor_subscriptions[sensor_id].discard(websocket)

        # Send to spatial subscribers
        if h3_index in self.spatial_subscriptions:
            message = {
                "type": "spatial_measurement",
                "data": measurement,
                "h3_index": h3_index,
                "timestamp": datetime.now().isoformat(),
            }

            for websocket in list(self.spatial_subscriptions[h3_index]):
                try:
                    asyncio.create_task(websocket.send_text(json.dumps(message)))
                except Exception:
                    # Remove disconnected clients
                    self.spatial_subscriptions[h3_index].discard(websocket)

    def broadcast_spatial_inference(self, inference_result: Dict):
        """Broadcast spatial inference results to subscribed clients."""
        message = {
            "type": "spatial_inference",
            "data": inference_result,
            "timestamp": datetime.now().isoformat(),
        }

        # Send to all active connections
        disconnected = set()
        for websocket in self.active_connections:
            try:
                asyncio.create_task(websocket.send_text(json.dumps(message)))
            except Exception:
                disconnected.add(websocket)

        # Remove disconnected clients
        for websocket in disconnected:
            self.active_connections.discard(websocket)

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app
