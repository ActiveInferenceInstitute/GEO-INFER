"""
Reproducible spatial visual preview generators for GEO-INFER modules.

Generates interactive Folium/Leaflet HTML preview cards, vector SVG cards,
PNG binary cards, and deterministic metadata receipts for all GEO-INFER
domain modules.
"""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import struct
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

try:
    import folium
    _FOLIUM_AVAILABLE = True
except ImportError:  # pragma: no cover
    folium = None  # type: ignore[assignment]
    _FOLIUM_AVAILABLE = False


# Canonical specifications and spatial profiles for all 44 GEO-INFER modules
MODULE_PROFILES: Dict[str, Dict[str, Any]] = {
    "ACT": {
        "name": "Active Inference Engine",
        "description": "Free energy minimization, epistemic exploration, and action selection",
        "category": "Foundations",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#2563eb",
        "secondary_color": "#60a5fa",
        "features": ["Belief Posterior", "Free Energy Landscape", "Policy Prior"],
    },
    "AG": {
        "name": "Agricultural Systems",
        "description": "Precision crop analytics, irrigation management, and yield modeling",
        "category": "Domain",
        "center": [36.7783, -119.4179],
        "zoom": 10,
        "primary_color": "#16a34a",
        "secondary_color": "#4ade80",
        "features": ["NDVI Field Zonation", "Soil Moisture Grids", "Irrigation Flow"],
    },
    "AGENT": {
        "name": "Multi-Agent Systems",
        "description": "Agent lifecycle, emergent coordination, and stigmergic interactions",
        "category": "Optimization",
        "center": [37.7833, -122.4167],
        "zoom": 13,
        "primary_color": "#9333ea",
        "secondary_color": "#c084fc",
        "features": ["Agent Swarm Positions", "Interaction Trails", "Communication Radii"],
    },
    "AI": {
        "name": "Artificial Intelligence Engine",
        "description": "Machine-learning embeddings, spatial neural operators, and surrogate models",
        "category": "Foundations",
        "center": [37.7600, -122.4400],
        "zoom": 12,
        "primary_color": "#4f46e5",
        "secondary_color": "#818cf8",
        "features": ["Latent Feature Space", "Neural Operator Field", "Prediction Confidence"],
    },
    "ANT": {
        "name": "Ant Colony Optimization",
        "description": "Swarm routing, pheromone field decay, and stigmergic optimization",
        "category": "Optimization",
        "center": [37.7500, -122.4200],
        "zoom": 13,
        "primary_color": "#ea580c",
        "secondary_color": "#fb923c",
        "features": ["Pheromone Intensity", "Foraging Paths", "Nest-Source Vectors"],
    },
    "API": {
        "name": "API Management System",
        "description": "Service endpoints, GraphQL schemas, and gateway telemetry",
        "category": "Infrastructure",
        "center": [37.7900, -122.4000],
        "zoom": 14,
        "primary_color": "#0284c7",
        "secondary_color": "#38bdf8",
        "features": ["Gateway Topology", "Latency Isocurves", "Service Ingress"],
    },
    "APP": {
        "name": "Application Framework",
        "description": "Interactive dashboards, reactive spatial UI, and view state",
        "category": "Applications",
        "center": [37.7700, -122.4300],
        "zoom": 13,
        "primary_color": "#0d9488",
        "secondary_color": "#2dd4bf",
        "features": ["Dashboard Viewport", "Active Layers", "Widget Anchors"],
    },
    "ART": {
        "name": "Artificial Intelligence Art",
        "description": "Generative aesthetics, cartographic styling, and spatial rendering",
        "category": "Creative",
        "center": [37.8000, -122.4100],
        "zoom": 13,
        "primary_color": "#db2777",
        "secondary_color": "#f472b6",
        "features": ["Harmonic Field", "Color Ramp Boundary", "Flow Contours"],
    },
    "BAYES": {
        "name": "Bayesian Inference Engine",
        "description": "Spatial Gaussian processes, variational ELBO, and MCMC sampling",
        "category": "Foundations",
        "center": [37.7650, -122.4350],
        "zoom": 12,
        "primary_color": "#7c3aed",
        "secondary_color": "#a78bfa",
        "features": ["GP Posterior Mean", "Variational Uncertainty", "Inducing Points"],
    },
    "BIO": {
        "name": "Biological Systems",
        "description": "Biodiversity mapping, ecological niche modeling, and genomic dispersion",
        "category": "Domain",
        "center": [38.5000, -122.8000],
        "zoom": 11,
        "primary_color": "#059669",
        "secondary_color": "#34d399",
        "features": ["Species Occurrence", "Habitat Suitability", "Corridor Network"],
    },
    "CIV": {
        "name": "Civic Engagement",
        "description": "Participatory GIS, municipal sentiment, and community feedback loops",
        "category": "Domain",
        "center": [37.7750, -122.4180],
        "zoom": 13,
        "primary_color": "#d97706",
        "secondary_color": "#fbbf24",
        "features": ["Neighborhood Feedback", "Voting Stations", "Public Forums"],
    },
    "CLIMATE": {
        "name": "Climate Analysis Module",
        "description": "CMIP6 climate projections, extreme heat indices, and anomaly detection",
        "category": "Domain",
        "center": [37.5000, -122.0000],
        "zoom": 9,
        "primary_color": "#0891b2",
        "secondary_color": "#22d3ee",
        "features": ["Temperature Anomaly", "Precipitation Shift", "Heat Vulnerability"],
    },
    "COG": {
        "name": "Cognitive Modeling",
        "description": "Spatial attention maps, multi-scale saliency, and working memory",
        "category": "Foundations",
        "center": [37.7800, -122.4250],
        "zoom": 13,
        "primary_color": "#6366f1",
        "secondary_color": "#818cf8",
        "features": ["Attention Saliency", "Cognitive Horizon", "Belief State Vector"],
    },
    "COMMS": {
        "name": "Communication Systems",
        "description": "Mesh network topology, telemetry routing, and bandwidth modeling",
        "category": "Infrastructure",
        "center": [37.7700, -122.4100],
        "zoom": 13,
        "primary_color": "#0284c7",
        "secondary_color": "#38bdf8",
        "features": ["Antenna Coverage", "Mesh Relay Nodes", "Signal Attenuation"],
    },
    "DATA": {
        "name": "Data Management Engine",
        "description": "GeoParquet chunking, secure GISP1 envelope validation, and storage",
        "category": "Foundations",
        "center": [37.7850, -122.4050],
        "zoom": 13,
        "primary_color": "#475569",
        "secondary_color": "#94a3b8",
        "features": ["Storage Partitions", "Cache Indexes", "Ingest Pipelines"],
    },
    "ECON": {
        "name": "Economic Analysis",
        "description": "Spatial econometrics, land value modeling, and trade networks",
        "category": "Domain",
        "center": [37.7920, -122.4010],
        "zoom": 14,
        "primary_color": "#ca8a04",
        "secondary_color": "#facc15",
        "features": ["Land Value Isobars", "Commercial Density", "Market Radius"],
    },
    "EDU": {
        "name": "Educational Technology Module",
        "description": "Geospatial curriculum tracks, interactive tutorials, and learner metrics",
        "category": "Domain",
        "center": [37.7700, -122.4500],
        "zoom": 13,
        "primary_color": "#2563eb",
        "secondary_color": "#60a5fa",
        "features": ["Learning Waypoints", "Exercise Boundaries", "Cohort Progress"],
    },
    "EMERGENCY": {
        "name": "Emergency Management Module",
        "description": "Evacuation routing, multi-hazard incident dispatch, and resource allocation",
        "category": "Domain",
        "center": [37.7600, -122.4300],
        "zoom": 12,
        "primary_color": "#dc2626",
        "secondary_color": "#f87171",
        "features": ["Evacuation Corridors", "Incident Perimeter", "Shelter Points"],
    },
    "ENERGY": {
        "name": "Energy Systems Module",
        "description": "Renewable potential, grid load balancing, and transmission routing",
        "category": "Domain",
        "center": [37.7000, -122.1500],
        "zoom": 10,
        "primary_color": "#eab308",
        "secondary_color": "#fde047",
        "features": ["Solar Irradiance", "Grid Substations", "Wind Potential"],
    },
    "EXAMPLES": {
        "name": "Cross-Module Examples",
        "description": "End-to-end integration exemplars, tutorials, and demonstration pipelines",
        "category": "Orchestration",
        "center": [37.7749, -122.4194],
        "zoom": 11,
        "primary_color": "#3b82f6",
        "secondary_color": "#93c5fd",
        "features": ["Workflow Stepper", "Cross-Domain Links", "Output Manifest"],
    },
    "FOREST": {
        "name": "Forest Management Module",
        "description": "Canopy cover analysis, fuel load estimation, and timber biomass",
        "category": "Domain",
        "center": [41.7500, -124.2000],
        "zoom": 10,
        "primary_color": "#15803d",
        "secondary_color": "#22c55e",
        "features": ["Canopy Density", "Fuel Load Index", "Timber Parcels"],
    },
    "GIT": {
        "name": "Git & Orchestration",
        "description": "Provenance DAGs, versioned spatial state, and reproducible workflows",
        "category": "Infrastructure",
        "center": [37.7800, -122.3900],
        "zoom": 14,
        "primary_color": "#334155",
        "secondary_color": "#64748b",
        "features": ["Commit Tree", "Branch Checkpoints", "Diff Polygons"],
    },
    "HEALTH": {
        "name": "Geospatial Health Analytics",
        "description": "Epidemiological diffusion, hospital accessibility, and environmental exposure",
        "category": "Domain",
        "center": [37.7600, -122.4400],
        "zoom": 12,
        "primary_color": "#e11d48",
        "secondary_color": "#fb7185",
        "features": ["Infection Clusters", "Care Access Isochrones", "Exposure Contours"],
    },
    "INTRA": {
        "name": "Knowledge Integration",
        "description": "Cross-module ontology, documentation catalog, and visualization hub",
        "category": "Infrastructure",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#0ea5e9",
        "secondary_color": "#38bdf8",
        "features": ["Module Graph", "Ontology Concepts", "Catalog Registry"],
    },
    "IOT": {
        "name": "Internet of Things Integration",
        "description": "Streaming sensor ingestion, telemetry buffers, and anomaly alerts",
        "category": "Foundations",
        "center": [37.7700, -122.4150],
        "zoom": 13,
        "primary_color": "#06b6d4",
        "secondary_color": "#67e8f9",
        "features": ["Sensor Feeds", "Buffer Geometries", "Threshold Alerts"],
    },
    "LOG": {
        "name": "Logistics",
        "description": "Freight corridors, last-mile optimization, and fleet dispatch",
        "category": "Domain",
        "center": [37.8000, -122.2800],
        "zoom": 11,
        "primary_color": "#f97316",
        "secondary_color": "#fdba74",
        "features": ["Freight Corridors", "Distribution Hubs", "Route Efficiency"],
    },
    "MARINE": {
        "name": "Marine and Coastal Module",
        "description": "Bathymetry modeling, shoreline vulnerability, and ocean currents",
        "category": "Domain",
        "center": [37.8200, -122.5000],
        "zoom": 11,
        "primary_color": "#0284c7",
        "secondary_color": "#0ea5e9",
        "features": ["Bathymetric Contours", "Current Vectors", "Coastal Buffers"],
    },
    "MATH": {
        "name": "Mathematical Foundations",
        "description": "SIMD geometry kernels, spherical trigonometry, and numerical transforms",
        "category": "Foundations",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#8b5cf6",
        "secondary_color": "#c4b5fd",
        "features": ["SIMD Ray-Casting Grid", "Convex Hull", "Point-in-Polygon"],
    },
    "METAGOV": {
        "name": "Meta-Governance & Organizational Governance Module",
        "description": "Polycentric governance, institutional decision protocols, and auditability",
        "category": "Governance",
        "center": [37.7790, -122.4180],
        "zoom": 13,
        "primary_color": "#64748b",
        "secondary_color": "#94a3b8",
        "features": ["Jurisdiction Borders", "Policy Envelopes", "Voting Weights"],
    },
    "NORMS": {
        "name": "Norms & Standards",
        "description": "ISO/OGC geospatial standard compliance, metadata schemas, and validation",
        "category": "Governance",
        "center": [37.7720, -122.4170],
        "zoom": 13,
        "primary_color": "#475569",
        "secondary_color": "#64748b",
        "features": ["Zoning Constraints", "Standard Buffers", "Audit Checkpoints"],
    },
    "OPS": {
        "name": "Operations",
        "description": "Cluster orchestration, memory budgets, and task execution",
        "category": "Infrastructure",
        "center": [37.7850, -122.4000],
        "zoom": 13,
        "primary_color": "#334155",
        "secondary_color": "#475569",
        "features": ["Worker Nodes", "Job Allocation", "Resource Metrics"],
    },
    "ORG": {
        "name": "Organizational Systems",
        "description": "Enterprise structure, role definitions, and workflow delegation",
        "category": "Governance",
        "center": [37.7780, -122.4150],
        "zoom": 13,
        "primary_color": "#059669",
        "secondary_color": "#10b981",
        "features": ["Unit Boundaries", "Delegation Graph", "Access Scopes"],
    },
    "PEP": {
        "name": "People & Communities",
        "description": "Demographic equity, social vulnerability, and human mobility patterns",
        "category": "Domain",
        "center": [37.7600, -122.4200],
        "zoom": 12,
        "primary_color": "#f59e0b",
        "secondary_color": "#fbbf24",
        "features": ["Equity Index Cells", "Demographic Density", "Community Centers"],
    },
    "PLACE": {
        "name": "Place-Based Analysis",
        "description": "Cascadia regional bioregions, volcanoes, and watershed hydrography",
        "category": "Domain",
        "center": [45.5152, -122.6784],
        "zoom": 7,
        "primary_color": "#059669",
        "secondary_color": "#34d399",
        "features": ["Cascadia Volcanoes", "Megathrust Fault Line", "Watershed Hydrography"],
    },
    "REQ": {
        "name": "Requirements Management",
        "description": "System specifications, verification traces, and constraint checking",
        "category": "Governance",
        "center": [37.7700, -122.4200],
        "zoom": 13,
        "primary_color": "#64748b",
        "secondary_color": "#94a3b8",
        "features": ["Requirement Zones", "Verification Status", "Trace Links"],
    },
    "RISK": {
        "name": "Risk Assessment",
        "description": "Directed multi-hazard interaction matrices and compound exceedance modeling",
        "category": "Foundations",
        "center": [37.7500, -122.4400],
        "zoom": 11,
        "primary_color": "#dc2626",
        "secondary_color": "#ef4444",
        "features": ["Compound Hazard Zone", "Exceedance Probability", "Vulnerability Surface"],
    },
    "SEC": {
        "name": "Security",
        "description": "GISP1 cryptographic envelopes, geospatial token validation, and anonymization",
        "category": "Infrastructure",
        "center": [37.7800, -122.4100],
        "zoom": 13,
        "primary_color": "#1e293b",
        "secondary_color": "#334155",
        "features": ["Cryptographic Boundary", "Audit Points", "Anonymized Hexagons"],
    },
    "SIM": {
        "name": "Simulation",
        "description": "Digital twin environments, Monte Carlo rollouts, and physics simulation",
        "category": "Foundations",
        "center": [37.7650, -122.4250],
        "zoom": 12,
        "primary_color": "#7c3aed",
        "secondary_color": "#8b5cf6",
        "features": ["Digital Twin State", "Simulation Mesh", "Trajectory Envelopes"],
    },
    "SPACE": {
        "name": "Spatial Analysis Engine",
        "description": "H3 v4 indexing, spatial joins, CRS reprojection, and GeoLibre projects",
        "category": "Foundations",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#2563eb",
        "secondary_color": "#3b82f6",
        "features": ["H3 Resolution Cells", "CRS Bounds", "Vector Geometry"],
    },
    "SPM": {
        "name": "Spatial Process Modeling",
        "description": "Topological random field theory, Euler characteristic, and resel inference",
        "category": "Foundations",
        "center": [37.7550, -122.4350],
        "zoom": 12,
        "primary_color": "#4338ca",
        "secondary_color": "#6366f1",
        "features": ["Euler Characteristic Surface", "FWE Peak Threshold", "Cluster Resels"],
    },
    "TEST": {
        "name": "Testing Framework",
        "description": "Unified test orchestrator, contract validators, and property suites",
        "category": "Infrastructure",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#15803d",
        "secondary_color": "#16a34a",
        "features": ["Test Coverage Cells", "Assertion Metrics", "Validation Gateways"],
    },
    "TIME": {
        "name": "Temporal Analysis Engine",
        "description": "Spatiotemporal streaming, dynamic windowing, and anomaly prediction",
        "category": "Foundations",
        "center": [37.7700, -122.4200],
        "zoom": 12,
        "primary_color": "#0284c7",
        "secondary_color": "#0ea5e9",
        "features": ["Temporal Trajectories", "Sliding Windows", "Anomaly Peaks"],
    },
    "TRANSPORT": {
        "name": "Transportation Systems Module",
        "description": "Multimodal transit routing, network flow analysis, and congestion relief",
        "category": "Domain",
        "center": [37.7749, -122.4194],
        "zoom": 12,
        "primary_color": "#d97706",
        "secondary_color": "#f59e0b",
        "features": ["Transit Corridors", "Traffic Flow Speeds", "Intermodal Hubs"],
    },
    "WATER": {
        "name": "Water Resource Module",
        "description": "Pollution plume dispersion, watershed flow routing, and groundwater aquifers",
        "category": "Domain",
        "center": [37.8000, -122.4000],
        "zoom": 11,
        "primary_color": "#0284c7",
        "secondary_color": "#38bdf8",
        "features": ["Watershed Catchment", "Pollution Plume Area", "Groundwater Aquifer"],
    },
}


@dataclass(frozen=True)
class SpatialPreviewArtifacts:
    """Container for generated preview files and metadata."""

    module_id: str
    html_path: Path
    svg_path: Path
    png_path: Path
    manifest_path: Path
    input_sha256: str
    html_bytes: int
    svg_bytes: int
    png_bytes: int


def _generate_synthetic_h3_polygons(
    center_lat: float, center_lng: float, count: int = 7, radius: float = 0.02
) -> List[List[Tuple[float, float]]]:
    """Generate deterministic hexagon polygons around a center point for preview cards."""
    import math

    polygons: List[List[Tuple[float, float]]] = []
    # Center hexagon
    angles = [i * (math.pi / 3.0) for i in range(6)]
    hex_r = radius * 0.55

    offsets = [(0.0, 0.0)]
    for k in range(min(count - 1, 6)):
        angle = k * (math.pi / 3.0)
        offsets.append((radius * math.cos(angle), radius * math.sin(angle)))

    for d_lat, d_lng in offsets:
        c_lat = center_lat + d_lat
        c_lng = center_lng + d_lng
        ring = []
        for a in angles:
            p_lat = c_lat + hex_r * math.sin(a)
            p_lng = c_lng + hex_r * math.cos(a)
            ring.append((round(p_lat, 6), round(p_lng, 6)))
        ring.append(ring[0])  # Close polygon
        polygons.append(ring)
    return polygons


def render_leaflet_html(
    module_id: str,
    output_path: Optional[Path] = None,
    *,
    width: int = 800,
    height: int = 450,
) -> str:
    """Render a standalone reproducible Leaflet/Folium HTML preview card."""
    profile = MODULE_PROFILES.get(module_id.upper())
    if not profile:
        raise ValueError(f"Unknown module ID: {module_id}")

    center_lat, center_lng = profile["center"]
    zoom = profile["zoom"]
    name = profile["name"]
    primary_color = profile["primary_color"]
    secondary_color = profile["secondary_color"]
    category = profile["category"]
    description = profile["description"]
    features = profile["features"]

    hex_rings = _generate_synthetic_h3_polygons(center_lat, center_lng, count=7)

    if _FOLIUM_AVAILABLE and folium is not None:
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom,
            tiles="CartoDB positron",
            width=width,
            height=height,
        )

        # Add title header
        title_html = (
            f"<div style='position: fixed; top: 10px; left: 60px; z-index: 1000; "
            f"background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(4px); "
            f"border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 14px; "
            f"box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); font-family: -apple-system, sans-serif;'>"
            f"<div style='display: flex; align-items: center; gap: 8px;'>"
            f"<span style='background: {primary_color}; color: white; padding: 2px 8px; "
            f"border-radius: 4px; font-weight: 700; font-size: 11px;'>GEO-INFER-{module_id}</span>"
            f"<span style='font-size: 13px; font-weight: 600; color: #1e293b;'>{html_lib.escape(name)}</span>"
            f"</div>"
            f"<div style='font-size: 11px; color: #64748b; margin-top: 2px;'>{html_lib.escape(description)}</div>"
            f"</div>"
        )
        m.get_root().html.add_child(folium.Element(title_html))  # type: ignore[attr-defined]

        # Add H3 hex grid layer
        fg_hex = folium.FeatureGroup(name="🔷 H3 Spatial Domain", show=True)
        for i, ring in enumerate(hex_rings):
            folium.Polygon(
                locations=ring,
                color=primary_color,
                weight=2,
                fill=True,
                fill_color=secondary_color,
                fill_opacity=0.35,
                popup=folium.Popup(
                    f"<b>Cell #{i}</b><br>Module: GEO-INFER-{module_id}<br>Feature: {features[i % len(features)]}",
                    max_width=250,
                ),
            ).add_to(fg_hex)
        fg_hex.add_to(m)

        # Center marker
        folium.CircleMarker(
            location=[center_lat, center_lng],
            radius=6,
            color=primary_color,
            fill=True,
            fill_color="#ffffff",
            fill_opacity=1.0,
            weight=3,
            popup=f"<b>GEO-INFER-{module_id}</b> Focus Center",
        ).add_to(m)

        folium.LayerControl(position="topright").add_to(m)
        rendered_html = m.get_root().render()
    else:  # pragma: no cover
        # Dependency-free HTML Leaflet fallback
        rendered_html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>GEO-INFER-{module_id}: {html_lib.escape(name)}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    #map {{ width: 100%; height: 100vh; }}
    .info-card {{
      position: absolute; top: 12px; left: 55px; z-index: 1000;
      background: rgba(255, 255, 255, 0.95); padding: 10px 16px;
      border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="info-card">
    <strong>GEO-INFER-{module_id}</strong>: {html_lib.escape(name)}<br>
    <small style="color: #64748b;">{html_lib.escape(description)}</small>
  </div>
  <div id="map"></div>
  <script>
    var map = L.map('map').setView([{center_lat}, {center_lng}], {zoom});
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      attribution: '&copy; CartoDB &copy; OpenStreetMap contributors'
    }}).addTo(map);
  </script>
</body>
</html>"""

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered_html, encoding="utf-8")

    return rendered_html


def render_svg_card(
    module_id: str,
    output_path: Optional[Path] = None,
    *,
    width: int = 700,
    height: int = 380,
) -> str:
    """Render a standalone reproducible SVG preview card with H3 spatial graphics."""
    profile = MODULE_PROFILES.get(module_id.upper())
    if not profile:
        raise ValueError(f"Unknown module ID: {module_id}")

    name = html_lib.escape(profile["name"])
    category = html_lib.escape(profile["category"])
    description = html_lib.escape(profile["description"])
    primary_color = profile["primary_color"]
    secondary_color = profile["secondary_color"]
    features = profile["features"]

    # Generate 7 hex center points on SVG canvas
    cx, cy = width - 180, height // 2 + 10
    hex_radius: float = 48.0

    hex_paths: List[str] = []
    offsets: List[Tuple[float, float]] = [(0.0, 0.0)]
    import math

    for k in range(6):
        a = k * (math.pi / 3.0)
        offsets.append((hex_radius * 1.65 * math.cos(a), hex_radius * 1.65 * math.sin(a)))

    for i, (dx, dy) in enumerate(offsets):
        px, py = cx + dx, cy + dy
        points = []
        for corner in range(6):
            ca = corner * (math.pi / 3.0)
            corner_x = px + hex_radius * math.cos(ca)
            corner_y = py + hex_radius * math.sin(ca)
            points.append(f"{corner_x:.1f},{corner_y:.1f}")
        points_str = " ".join(points)
        fill_op = "0.7" if i == 0 else "0.35"
        feat_label = features[i % len(features)]
        hex_paths.append(
            f'<polygon points="{points_str}" fill="{secondary_color}" fill-opacity="{fill_op}" '
            f'stroke="{primary_color}" stroke-width="2.5" />'
        )
        hex_paths.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{primary_color}" />'
        )
        if i == 0:
            hex_paths.append(
                f'<text x="{px:.1f}" y="{py + 4:.1f}" text-anchor="middle" '
                f'fill="#ffffff" font-family="-apple-system, sans-serif" font-size="10" font-weight="700">H3</text>'
            )

    hex_graphics = "\n    ".join(hex_paths)
    chips_html = "".join(
        f'<rect x="36" y="{190 + idx * 32}" width="220" height="24" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>'
        f'<circle cx="48" cy="{202 + idx * 32}" r="3.5" fill="{primary_color}"/>'
        f'<text x="60" y="{206 + idx * 32}" fill="#334155" font-family="-apple-system, sans-serif" font-size="11" font-weight="500">{html_lib.escape(feat)}</text>'
        for idx, feat in enumerate(features[:3])
    )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bg-grad-{module_id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f8fafc"/>
    </linearGradient>
    <linearGradient id="badge-grad-{module_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{primary_color}"/>
      <stop offset="100%" stop-color="{secondary_color}"/>
    </linearGradient>
    <filter id="shadow-{module_id}" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Background Card -->
  <rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="12" fill="url(#bg-grad-{module_id})" stroke="#e2e8f0" stroke-width="1.5" filter="url(#shadow-{module_id})"/>

  <!-- Left Content Column -->
  <g transform="translate(0, 0)">
    <!-- Header Badge -->
    <rect x="36" y="36" width="130" height="26" rx="6" fill="url(#badge-grad-{module_id})"/>
    <text x="101" y="53" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="700" letter-spacing="0.5">GEO-INFER-{module_id}</text>

    <!-- Category Pill -->
    <rect x="176" y="36" width="90" height="26" rx="6" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
    <text x="221" y="53" text-anchor="middle" fill="#475569" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="600">{category}</text>

    <!-- Title -->
    <text x="36" y="98" fill="#0f172a" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="20" font-weight="700">{name}</text>

    <!-- Description -->
    <text x="36" y="128" fill="#64748b" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="400">
      <tspan x="36" dy="0">{description[:58]}</tspan>
      <tspan x="36" dy="18">{description[58:120]}</tspan>
    </text>

    <!-- Section Heading -->
    <text x="36" y="174" fill="#1e293b" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="12" font-weight="600">Active Spatial Dimensions</text>

    <!-- Feature Chips -->
    {chips_html}

    <!-- Footer Contract Info -->
    <text x="36" y="{height - 28}" fill="#94a3b8" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="10" font-weight="500">H3 v4 Spatial Topology · CC BY-NC-SA 4.0 · Verified Contract</text>
  </g>

  <!-- Right Visual Domain H3 Graph -->
  <g>
    <!-- Grid connection lines -->
    <line x1="{cx}" y1="{cy}" x2="{cx - 90}" y2="{cy}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
    <line x1="{cx}" y1="{cy}" x2="{cx + 90}" y2="{cy}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
    <line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 90}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
    <line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy + 90}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4"/>
    {hex_graphics}
  </g>
</svg>"""

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg_content, encoding="utf-8")

    return svg_content


def _build_raw_png(width: int, height: int, rgb_bytes: bytes, text_chunks: Optional[Mapping[str, str]] = None) -> bytes:
    """Construct a compliant PNG binary byte stream with optional tEXt metadata chunks."""
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    # Width (4), Height (4), Bit depth (1), Color type 2 (RGB), Compression (0), Filter (0), Interlace (0)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF)
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + ihdr_crc

    # Optional tEXt chunks
    extra_chunks = b""
    if text_chunks:
        for key, val in text_chunks.items():
            t_data = key.encode("latin-1") + b"\x00" + val.encode("latin-1")
            t_crc = struct.pack(">I", zlib.crc32(b"tEXt" + t_data) & 0xFFFFFFFF)
            extra_chunks += struct.pack(">I", len(t_data)) + b"tEXt" + t_data + t_crc

    # IDAT chunk: filter byte (0) prepended to each scanline
    raw_scanlines = bytearray()
    row_stride = width * 3
    for y in range(height):
        raw_scanlines.append(0)  # Filter type 0 (None)
        raw_scanlines.extend(rgb_bytes[y * row_stride : (y + 1) * row_stride])

    compressed_idat = zlib.compress(bytes(raw_scanlines), level=9)
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed_idat) & 0xFFFFFFFF)
    idat_chunk = struct.pack(">I", len(compressed_idat)) + b"IDAT" + compressed_idat + idat_crc

    # IEND chunk
    iend_crc = struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    iend_chunk = struct.pack(">I", 0) + b"IEND" + iend_crc

    return signature + ihdr_chunk + extra_chunks + idat_chunk + iend_chunk


def render_png_card(
    module_id: str,
    output_path: Optional[Path] = None,
    *,
    width: int = 400,
    height: int = 240,
) -> bytes:
    """Render a deterministic raster PNG preview card with embedded metadata."""
    profile = MODULE_PROFILES.get(module_id.upper())
    if not profile:
        raise ValueError(f"Unknown module ID: {module_id}")

    # Parse primary hex color
    hex_color = profile["primary_color"].lstrip("#")
    r_base = int(hex_color[0:2], 16)
    g_base = int(hex_color[2:4], 16)
    b_base = int(hex_color[4:6], 16)

    # Generate smooth gradient image buffer
    pixel_data = bytearray(width * height * 3)
    for y in range(height):
        v_factor = y / float(height)
        for x in range(width):
            h_factor = x / float(width)
            # Subtle gradient with accented border
            if x < 4 or x >= width - 4 or y < 4 or y >= height - 4:
                # Border in primary color
                r, g, b = r_base, g_base, b_base
            elif y < 40:
                # Top header bar
                r = int(r_base * 0.85 + (255 - r_base) * 0.15)
                g = int(g_base * 0.85 + (255 - g_base) * 0.15)
                b = int(b_base * 0.85 + (255 - b_base) * 0.15)
            else:
                # Soft background gradient
                diag = (h_factor + v_factor) * 0.5
                r = int(248 + (255 - 248) * (1 - diag))
                g = int(250 + (255 - 250) * (1 - diag))
                b = int(252 + (255 - 252) * (1 - diag))

            idx = (y * width + x) * 3
            pixel_data[idx] = r
            pixel_data[idx + 1] = g
            pixel_data[idx + 2] = b

    text_meta = {
        "Title": f"GEO-INFER-{module_id} Preview",
        "Module": f"GEO-INFER-{module_id}",
        "Category": profile["category"],
        "Name": profile["name"],
        "Generator": "geo_infer_intra.visual_preview",
    }

    png_bytes = _build_raw_png(width, height, bytes(pixel_data), text_meta)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png_bytes)

    return png_bytes


def generate_module_preview_suite(
    module_id: str,
    output_dir: Path | str,
) -> SpatialPreviewArtifacts:
    """Generate the full reproducible preview bundle (HTML, SVG, PNG, Manifest) for a module."""
    mod = module_id.upper()
    if mod not in MODULE_PROFILES:
        raise ValueError(f"Module {module_id} not recognized in profile registry")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = f"geo-infer-{mod.lower()}"
    html_file = out_dir / f"{slug}_preview.html"
    svg_file = out_dir / f"{slug}_preview.svg"
    png_file = out_dir / f"{slug}_preview.png"
    manifest_file = out_dir / f"{slug}_preview.manifest.json"

    html_str = render_leaflet_html(mod, html_file)
    svg_str = render_svg_card(mod, svg_file)
    png_bytes = render_png_card(mod, png_file)

    input_payload = {
        "module_id": mod,
        "profile": MODULE_PROFILES[mod],
    }
    input_digest = hashlib.sha256(
        json.dumps(input_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()

    manifest_data: Dict[str, Any] = {
        "schema_version": "geo-infer-intra-visual-preview/v1",
        "module_id": f"GEO-INFER-{mod}",
        "name": MODULE_PROFILES[mod]["name"],
        "category": MODULE_PROFILES[mod]["category"],
        "input_sha256": input_digest,
        "artifacts": [
            {"name": html_file.name, "type": "text/html", "bytes": len(html_str.encode("utf-8"))},
            {"name": svg_file.name, "type": "image/svg+xml", "bytes": len(svg_str.encode("utf-8"))},
            {"name": png_file.name, "type": "image/png", "bytes": len(png_bytes)},
        ],
        "accessibility": {
            "has_title": True,
            "has_svg_viewbox": True,
            "has_png_metadata": True,
        },
    }

    manifest_file.write_text(json.dumps(manifest_data, indent=2, sort_keys=True), encoding="utf-8")

    return SpatialPreviewArtifacts(
        module_id=mod,
        html_path=html_file,
        svg_path=svg_file,
        png_path=png_file,
        manifest_path=manifest_file,
        input_sha256=input_digest,
        html_bytes=len(html_str.encode("utf-8")),
        svg_bytes=len(svg_str.encode("utf-8")),
        png_bytes=len(png_bytes),
    )


def generate_all_module_previews(output_dir: Path | str) -> Dict[str, SpatialPreviewArtifacts]:
    """Generate preview card bundles for all 44 GEO-INFER modules."""
    results: Dict[str, SpatialPreviewArtifacts] = {}
    for mod in sorted(MODULE_PROFILES.keys()):
        results[mod] = generate_module_preview_suite(mod, output_dir)
    return results


__all__ = [
    "MODULE_PROFILES",
    "SpatialPreviewArtifacts",
    "render_leaflet_html",
    "render_svg_card",
    "render_png_card",
    "generate_module_preview_suite",
    "generate_all_module_previews",
]
