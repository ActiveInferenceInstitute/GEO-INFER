# GEO-INFER-APP: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-APP** module provides application development capabilities for agents, enabling web interfaces, dashboards, and interactive mapping applications.

## Agent Capabilities

### 1. Dashboard Builder

```python
from geo_infer_app import DashboardBuilder

# Create agent-powered dashboard
dashboard = DashboardBuilder()

# Add map widget
dashboard.add_widget(
    type="map",
    data_source=agent.get_spatial_data,
    layers=["parcels", "zones", "points"],
    interactive=True)

# Add chart widget
dashboard.add_widget(
    type="chart",
    chart_type="time_series",
    data_source=agent.get_metrics)

# Deploy dashboard
dashboard.deploy(port=3000)```

### 2. Interactive Maps

```python
from geo_infer_app import MapApplication

# Create interactive map application
app = MapApplication()

# Configure map
app.set_basemap("satellite")
app.set_center(lat=37.77, lon=-122.41, zoom=12)

# Add agent-driven layers
app.add_layer(
    name="real_time_sensors",
    source=sensor_agent.stream,
    style={"type": "heatmap"})

# Add interactivity
@app.on_click
def handle_click(event):
    info = agent.query_location(event.latlng)
    app.show_popup(info)```

### 3. Report Generator

```python
from geo_infer_app import ReportGenerator

# Generate reports from agent analysis
generator = ReportGenerator()

report = generator.create(
    template="spatial_analysis",
    data=agent.get_analysis_results(),
    include_maps=True,
    format="pdf")

print(f"Report generated: {report.path}")```

### 4. Mobile App Support

```python
from geo_infer_app import MobileApp

# Create mobile-friendly interface
mobile = MobileApp()

# Configure for field data collection
mobile.enable_features([
    "offline_maps",
    "gps_tracking",
    "photo_capture",
    "form_builder"])

# Sync with agent
mobile.set_sync_agent(field_agent)```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Dashboards** | ✅ Ready | Interactive dashboards |
| **Maps** | ✅ Ready | Web mapping |
| **Reports** | ✅ Ready | PDF, HTML reports |
| **Mobile** | ✅ Ready | Field apps |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **UIAgent** | 🔮 High | Adaptive interfaces |
| **VoiceAgent** | 🔮 Medium | Voice commands |

## Use Cases

### Operations Dashboard

```python
from geo_infer_app import OperationsDashboard

ops = OperationsDashboard(title="City Operations")

# Real-time monitoring
ops.add_map(agent.get_live_data)
ops.add_alerts(agent.get_alerts)
ops.add_metrics(agent.get_kpis)

ops.launch()```

---

This AGENTS.md documents how GEO-INFER-APP provides application capabilities for agents.

**Last Updated**: 2026-01-26
