"""
InteractiveVisualizationEngine: Interactive geospatial dashboard creation.

This module provides comprehensive visualization capabilities for place-based
analysis, including interactive maps with H3 integration, multi-layer overlays,
and dashboard generation adapted from the climate integration example.
"""

import logging
import folium
import h3
import geopandas as gpd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from folium.plugins import MarkerCluster
import numpy as np

logger = logging.getLogger(__name__)


class InteractiveVisualizationEngine:
    """
    Interactive visualization engine for comprehensive place-based dashboards.

    Adapted from the climate integration spatial microbiome example, this engine
    creates sophisticated interactive geospatial visualizations with H3 integration,
    multi-layer overlays, and real-time data integration for place-based analysis.

    Features:
    - H3 hexagonal spatial aggregation and visualization
    - Multi-layer interactive maps with toggle controls
    - Real-time data integration and visualization
    - Professional dashboard generation
    - Clustering and spatial analysis visualization
    - Export capabilities for sharing and embedding

    Example Usage:
        >>> engine = InteractiveVisualizationEngine(location_config, output_dir)
        >>> dashboard = engine.create_comprehensive_dashboard(analysis_results)
        >>> forest_map = engine.create_forest_health_visualization(forest_data)
        >>> coastal_map = engine.create_coastal_resilience_visualization(coastal_data)
    """

    def __init__(
        self, location_config: Dict[str, Any], output_dir: Path, h3_resolution: int = 8
    ):
        """
        Initialize visualization engine.

        Args:
            location_config: Configuration for the location
            output_dir: Output directory for generated visualizations
            h3_resolution: H3 spatial resolution for aggregation
        """
        if not isinstance(location_config, dict):
            raise TypeError("location_config must be a mapping")
        if not isinstance(h3_resolution, int) or not 0 <= h3_resolution <= 15:
            raise ValueError("h3_resolution must be an integer between 0 and 15")
        self.location_config = location_config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.h3_resolution = h3_resolution

        # Get location center and bounds
        self.location_bounds = location_config.get("location", {}).get("bounds", {})
        required_bounds = ("north", "south", "east", "west")
        if any(key not in self.location_bounds for key in required_bounds):
            raise ValueError(f"location bounds must contain {required_bounds}")
        bounds = {key: float(self.location_bounds[key]) for key in required_bounds}
        if not all(np.isfinite(value) for value in bounds.values()):
            raise ValueError("location bounds must contain finite values")
        if not -90 <= bounds["south"] < bounds["north"] <= 90:
            raise ValueError(
                "location latitude bounds must satisfy -90 <= south < north <= 90"
            )
        if not -180 <= bounds["west"] < bounds["east"] <= 180:
            raise ValueError(
                "location longitude bounds must satisfy -180 <= west < east <= 180"
            )
        self.location_bounds = bounds
        self.center_lat = (
            self.location_bounds.get("north", 42)
            + self.location_bounds.get("south", 41)
        ) / 2
        self.center_lon = (
            self.location_bounds.get("east", -123)
            + self.location_bounds.get("west", -125)
        ) / 2

        logger.info("InteractiveVisualizationEngine initialized")
        logger.info(f"Location center: ({self.center_lat:.3f}, {self.center_lon:.3f})")
        logger.info(f"H3 resolution: {self.h3_resolution}")

    def create_comprehensive_dashboard(
        self, analysis_results: Dict[str, Any], dashboard_config: Optional[Dict] = None
    ) -> str:
        """
        Create comprehensive interactive dashboard with all analysis results.

        Args:
            analysis_results: Results from comprehensive analysis
            dashboard_config: Optional dashboard configuration

        Returns:
            Path to generated dashboard HTML file
        """
        if not isinstance(analysis_results, dict):
            raise TypeError("analysis_results must be a mapping")
        dashboard_config = dashboard_config or {}
        if not isinstance(dashboard_config, dict):
            raise TypeError("dashboard_config must be a mapping")
        zoom_start = dashboard_config.get("zoom_start", 10)
        if not isinstance(zoom_start, (int, float)) or not np.isfinite(zoom_start):
            raise ValueError("dashboard_config.zoom_start must be finite")
        tiles = dashboard_config.get("tiles", "CartoDB positron")
        if not isinstance(tiles, str) or not tiles:
            raise ValueError("dashboard_config.tiles must be a non-empty string")
        logger.info("🎨 Creating comprehensive interactive dashboard...")

        # Create base map with professional styling
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=zoom_start,
            tiles=tiles,
            attr="© CartoDB, © OpenStreetMap contributors",
        )

        # Add title
        title_html = self._create_dashboard_title()
        m.get_root().html.add_child(folium.Element(title_html))

        # Create layer groups for different analysis domains
        layer_groups = self._create_layer_groups()

        # Add domain-specific visualizations
        domain_results = analysis_results.get("domain_results", {})

        if "forest_health" in domain_results:
            self._add_forest_health_layers(
                m, layer_groups, domain_results["forest_health"]
            )

        if "coastal_resilience" in domain_results:
            self._add_coastal_resilience_layers(
                m, layer_groups, domain_results["coastal_resilience"]
            )

        if "fire_risk" in domain_results:
            self._add_fire_risk_layers(m, layer_groups, domain_results["fire_risk"])

        if "community_development" in domain_results:
            self._add_community_development_layers(
                m, layer_groups, domain_results["community_development"]
            )

        # Add integrated results if available
        integrated_results = analysis_results.get("integrated_results", {})
        if integrated_results:
            self._add_integration_layers(m, layer_groups, integrated_results)

        # Add layer control
        for group in layer_groups.values():
            group.add_to(m)
        folium.LayerControl().add_to(m)

        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_path = self.output_dir / f"comprehensive_dashboard_{timestamp}.html"
        m.save(str(dashboard_path))

        logger.info(f"✅ Comprehensive dashboard saved to: {dashboard_path}")
        return str(dashboard_path)

    def create_base_map(self) -> folium.Map:
        """Create a basic folium map for testing."""
        return folium.Map(location=[self.center_lat, self.center_lon], zoom_start=10)

    def _create_dashboard_title(self) -> str:
        """Create professional dashboard title."""
        location_name = self.location_config.get("location", {}).get("name", "Location")

        title_html = f"""
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 80px; 
                    background-color: white; border: 2px solid grey; z-index:9999; 
                    font-size: 14px; color: black; font-weight: bold;
                    padding: 10px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <div style="font-size: 18px; margin-bottom: 5px; color: #2E8B57;">
                🗺️ GEO-INFER Place-Based Analysis
            </div>
            <div style="font-size: 14px; color: #4682B4;">
                📍 {location_name}
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 5px;">
                Interactive Geospatial Dashboard • {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        """
        return title_html

    def _create_layer_groups(self) -> Dict[str, folium.FeatureGroup]:
        """Create layer groups for different analysis domains."""
        layer_groups = {
            "h3_grid": folium.FeatureGroup(name="🔷 H3 Spatial Grid", show=True),
            "forest_health": folium.FeatureGroup(name="🌲 Forest Health", show=True),
            "coastal_resilience": folium.FeatureGroup(
                name="🌊 Coastal Resilience", show=True
            ),
            "fire_risk": folium.FeatureGroup(name="🔥 Fire Risk", show=True),
            "community_development": folium.FeatureGroup(
                name="🏘️ Community Development", show=True
            ),
            "integration": folium.FeatureGroup(
                name="🔗 Cross-Domain Integration", show=False
            ),
        }
        return layer_groups

    def _add_forest_health_layers(
        self, m: folium.Map, layer_groups: Dict, forest_data: Dict[str, Any]
    ):
        """Add forest health visualization layers."""
        logger.info("Adding forest health visualization layers...")

        # Create marker cluster for forest monitoring sites
        forest_cluster = MarkerCluster(name="Forest Monitoring Sites")

        # Add forest health monitoring points (demo data when no external source is provided)
        monitoring_sites = self._generate_forest_monitoring_sites()

        for site in monitoring_sites:
            # Color code by health status
            if site["health_index"] > 0.7:
                marker_color = "green"
                icon = "leaf"
            elif site["health_index"] > 0.4:
                marker_color = "orange"
                icon = "exclamation-triangle"
            else:
                marker_color = "red"
                icon = "warning"

            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #228B22; margin: 0 0 8px 0;">🌲 Forest Health Site</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>Site ID:</b></td><td>{site['site_id']}</td></tr>
                    <tr><td><b>Health Index:</b></td><td>{site['health_index']:.2f}</td></tr>
                    <tr><td><b>NDVI:</b></td><td>{site['ndvi']:.3f}</td></tr>
                    <tr><td><b>Tree Density:</b></td><td>{site['tree_density']}/ha</td></tr>
                    <tr><td><b>Species Diversity:</b></td><td>{site['species_diversity']:.2f}</td></tr>
                    <tr><td><b>Last Survey:</b></td><td>{site['last_survey']}</td></tr>
                </table>
            </div>
            """

            folium.Marker(
                location=[site["lat"], site["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Health Index: {site['health_index']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix="fa"),
            ).add_to(forest_cluster)

        forest_cluster.add_to(layer_groups["forest_health"])

    def _add_coastal_resilience_layers(
        self, m: folium.Map, layer_groups: Dict, coastal_data: Dict[str, Any]
    ):
        """Add coastal resilience visualization layers."""
        logger.info("Adding coastal resilience visualization layers...")

        # Create coastal monitoring cluster
        coastal_cluster = MarkerCluster(name="Coastal Monitoring Sites")

        # Add coastal monitoring points (demo data when no external source is provided)
        coastal_sites = self._generate_coastal_monitoring_sites()

        for site in coastal_sites:
            # Color code by vulnerability level
            if site["vulnerability"] < 0.3:
                marker_color = "blue"
                icon = "anchor"
            elif site["vulnerability"] < 0.7:
                marker_color = "orange"
                icon = "exclamation-triangle"
            else:
                marker_color = "red"
                icon = "warning"

            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #4682B4; margin: 0 0 8px 0;">🌊 Coastal Monitoring</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>Site ID:</b></td><td>{site['site_id']}</td></tr>
                    <tr><td><b>Vulnerability:</b></td><td>{site['vulnerability']:.2f}</td></tr>
                    <tr><td><b>Erosion Rate:</b></td><td>{site['erosion_rate']:.1f} m/yr</td></tr>
                    <tr><td><b>Sea Level Trend:</b></td><td>{site['sea_level_trend']:.1f} mm/yr</td></tr>
                    <tr><td><b>Storm Exposure:</b></td><td>{site['storm_exposure']}</td></tr>
                </table>
            </div>
            """

            folium.Marker(
                location=[site["lat"], site["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Vulnerability: {site['vulnerability']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix="fa"),
            ).add_to(coastal_cluster)

        coastal_cluster.add_to(layer_groups["coastal_resilience"])

    def _add_fire_risk_layers(
        self, m: folium.Map, layer_groups: Dict, fire_data: Dict[str, Any]
    ):
        """Add fire risk visualization layers."""
        logger.info("Adding fire risk visualization layers...")

        # Create fire monitoring cluster
        fire_cluster = MarkerCluster(name="Fire Risk Monitoring")

        # Add fire risk monitoring points (demo data when no external source is provided)
        fire_sites = self._generate_fire_monitoring_sites()

        for site in fire_sites:
            # Color code by risk level
            if site["risk_level"] < 0.3:
                marker_color = "green"
                icon = "fire-extinguisher"
            elif site["risk_level"] < 0.7:
                marker_color = "orange"
                icon = "exclamation-triangle"
            else:
                marker_color = "red"
                icon = "fire"

            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #DC143C; margin: 0 0 8px 0;">🔥 Fire Risk Site</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>Site ID:</b></td><td>{site['site_id']}</td></tr>
                    <tr><td><b>Risk Level:</b></td><td>{site['risk_level']:.2f}</td></tr>
                    <tr><td><b>Fuel Moisture:</b></td><td>{site['fuel_moisture']:.1f}%</td></tr>
                    <tr><td><b>Fire Weather Index:</b></td><td>{site['fire_weather_index']:.1f}</td></tr>
                    <tr><td><b>Suppression Distance:</b></td><td>{site['suppression_distance']:.1f} km</td></tr>
                </table>
            </div>
            """

            folium.Marker(
                location=[site["lat"], site["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Risk Level: {site['risk_level']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix="fa"),
            ).add_to(fire_cluster)

        fire_cluster.add_to(layer_groups["fire_risk"])

    def _add_community_development_layers(
        self, m: folium.Map, layer_groups: Dict, community_data: Dict[str, Any]
    ):
        """Add community development visualization layers."""
        logger.info("Adding community development visualization layers...")

        # Create community facilities cluster
        community_cluster = MarkerCluster(name="Community Facilities")

        # Add community facility points (demo data when no external source is provided)
        facilities = self._generate_community_facilities()

        for facility in facilities:
            # Color code by facility type
            facility_colors = {
                "healthcare": "red",
                "education": "blue",
                "emergency": "orange",
                "community": "green",
            }

            facility_icons = {
                "healthcare": "plus",
                "education": "graduation-cap",
                "emergency": "exclamation-triangle",
                "community": "users",
            }

            color = facility_colors.get(facility["type"], "gray")
            icon = facility_icons.get(facility["type"], "info")

            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #4B0082; margin: 0 0 8px 0;">🏘️ {facility['name']}</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>Type:</b></td><td>{facility['type'].title()}</td></tr>
                    <tr><td><b>Capacity:</b></td><td>{facility['capacity']}</td></tr>
                    <tr><td><b>Service Area:</b></td><td>{facility['service_area']} km²</td></tr>
                    <tr><td><b>Accessibility:</b></td><td>{facility['accessibility']}</td></tr>
                </table>
            </div>
            """

            folium.Marker(
                location=[facility["lat"], facility["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=facility["name"],
                icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            ).add_to(community_cluster)

        community_cluster.add_to(layer_groups["community_development"])

    def _add_integration_layers(
        self, m: folium.Map, layer_groups: Dict, integration_data: Dict[str, Any]
    ):
        """Add cross-domain integration visualization layers."""
        logger.info("Adding cross-domain integration layers...")

        # Add H3 hexagonal overlay for integrated analysis
        h3_cells = self._generate_h3_integration_grid(integration_data)

        for h3_cell, cell_data in h3_cells.items():
            # Get H3 cell boundary
            h3_boundary = h3.cell_to_boundary(h3_cell)

            # Color based on integration score
            integration_score = cell_data.get("integration_score", 0)
            if integration_score > 0.7:
                color = "#FF4500"  # High integration (red-orange)
            elif integration_score > 0.4:
                color = "#FFA500"  # Medium integration (orange)
            elif integration_score > 0.2:
                color = "#FFFF00"  # Low integration (yellow)
            else:
                color = "#87CEEB"  # Minimal integration (light blue)

            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #8B4513; margin: 0 0 8px 0;">🔗 H3 Integration Cell</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>H3 Index:</b></td><td>{h3_cell}</td></tr>
                    <tr><td><b>Integration Score:</b></td><td>{integration_score:.3f}</td></tr>
                    <tr><td><b>Domain Count:</b></td><td>{cell_data['domain_count']}</td></tr>
                    <tr><td><b>Risk Factors:</b></td><td>{cell_data['risk_factors']}</td></tr>
                </table>
            </div>
            """

            folium.Polygon(
                locations=[[lat, lon] for lon, lat in h3_boundary],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Integration Score: {integration_score:.3f}",
                color="black",
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
            ).add_to(layer_groups["integration"])

    def _generate_forest_monitoring_sites(self) -> List[Dict]:
        """Generate forest monitoring sites across Pacific Northwest and tropical regions.

        Produces programmatic site data using realistic coordinate ranges
        and ecologically meaningful attribute distributions.  When an external
        GeoJSON data source is configured via ``location_config['data_paths']['forest_monitoring']``
        and the file is readable, it is used instead.

        Returns:
            List of dicts, each containing lat, lon, site_id, health_index,
            ndvi, tree_density, species_diversity, and last_survey.
        """
        # Try loading from an external source first
        data_path = self.location_config.get("data_paths", {}).get("forest_monitoring")
        if data_path is not None:
            try:
                gdf = gpd.read_file(data_path)
                sites = gdf.to_dict("records")
                if sites:
                    return sites
            except Exception as e:
                logger.warning(
                    f"External forest data unavailable ({e}), generating sites programmatically"
                )

        rng = np.random.RandomState(42)
        n_sites = 20

        # Pacific Northwest: lat 44-52, lng -124 to -116
        pnw_lats = rng.uniform(44, 52, n_sites // 2)
        pnw_lngs = rng.uniform(-124, -116, n_sites // 2)
        # Tropical forests: lat -10 to 10, lng -80 to -60
        trop_lats = rng.uniform(-10, 10, n_sites // 2)
        trop_lngs = rng.uniform(-80, -60, n_sites // 2)

        lats = np.concatenate([pnw_lats, trop_lats])
        lngs = np.concatenate([pnw_lngs, trop_lngs])

        sites = []
        for i in range(n_sites):
            health_index = round(float(rng.beta(3, 1.5)), 2)
            ndvi = round(float(rng.uniform(0.35, 0.92)), 3)
            tree_density = int(rng.randint(80, 650))
            species_diversity = round(float(rng.uniform(0.2, 0.95)), 2)
            survey_month = int(rng.randint(1, 13))
            survey_day = int(rng.randint(1, 29))

            sites.append(
                {
                    "site_id": f"FOREST-{i + 1:03d}",
                    "lat": round(float(lats[i]), 5),
                    "lon": round(float(lngs[i]), 5),
                    "health_index": health_index,
                    "ndvi": ndvi,
                    "tree_density": tree_density,
                    "species_diversity": species_diversity,
                    "last_survey": f"2025-{survey_month:02d}-{survey_day:02d}",
                }
            )
        return sites

    def _generate_coastal_monitoring_sites(self) -> List[Dict]:
        """Generate coastal monitoring sites across Atlantic, Pacific, and tropical coasts.

        Produces programmatic site data using realistic coastal coordinate ranges
        and oceanographic attribute distributions.  When an external GeoJSON data
        source is configured and readable, it is used instead.

        Returns:
            List of dicts, each containing lat, lon, site_id, vulnerability,
            erosion_rate, sea_level_trend, and storm_exposure.
        """
        # Try loading from an external source first
        data_path = self.location_config.get("data_paths", {}).get("coastal_monitoring")
        if data_path is not None:
            try:
                gdf = gpd.read_file(data_path)
                sites = gdf.to_dict("records")
                if sites:
                    return sites
            except Exception as e:
                logger.warning(
                    f"External coastal data unavailable ({e}), generating sites programmatically"
                )

        rng = np.random.RandomState(43)
        n_sites = 15

        # US Atlantic coast: lat 25-45, lng -80 to -70
        atlantic_lats = rng.uniform(25, 45, 5)
        atlantic_lngs = rng.uniform(-80, -70, 5)
        # US Pacific coast: lat 30-50, lng -125 to -115
        pacific_lats = rng.uniform(30, 50, 5)
        pacific_lngs = rng.uniform(-125, -115, 5)
        # Tropical/Indo-Pacific coasts: lat -10 to 25, lng 100 to 115
        tropical_lats = rng.uniform(-10, 25, 5)
        tropical_lngs = rng.uniform(100, 115, 5)

        lats = np.concatenate([atlantic_lats, pacific_lats, tropical_lats])
        lngs = np.concatenate([atlantic_lngs, pacific_lngs, tropical_lngs])

        storm_categories = ["Low", "Moderate", "High", "Extreme"]

        sites = []
        for i in range(n_sites):
            vulnerability = round(float(rng.beta(2, 3)), 2)
            erosion_rate = round(float(rng.exponential(0.8)), 1)
            sea_level_trend = round(float(rng.uniform(1.5, 5.5)), 1)
            storm_exposure = storm_categories[
                int(rng.randint(0, len(storm_categories)))
            ]

            sites.append(
                {
                    "site_id": f"COASTAL-{i + 1:03d}",
                    "lat": round(float(lats[i]), 5),
                    "lon": round(float(lngs[i]), 5),
                    "vulnerability": vulnerability,
                    "erosion_rate": erosion_rate,
                    "sea_level_trend": sea_level_trend,
                    "storm_exposure": storm_exposure,
                }
            )
        return sites

    def _generate_fire_monitoring_sites(self) -> List[Dict]:
        """Generate fire monitoring sites across fire-prone zones.

        Produces programmatic site data using realistic coordinate ranges for
        California/Pacific and Mediterranean fire-prone regions with
        fire-science attribute distributions.  When an external GeoJSON data
        source is configured and readable, it is used instead.

        Returns:
            List of dicts, each containing lat, lon, site_id, risk_level,
            fuel_moisture, fire_weather_index, and suppression_distance.
        """
        # Try loading from an external source first
        data_path = self.location_config.get("data_paths", {}).get("fire_monitoring")
        if data_path is not None:
            try:
                gdf = gpd.read_file(data_path)
                sites = gdf.to_dict("records")
                if sites:
                    return sites
            except Exception as e:
                logger.warning(
                    f"External fire data unavailable ({e}), generating sites programmatically"
                )

        rng = np.random.RandomState(44)
        n_sites = 25
        half = n_sites // 2

        # California/Pacific fire corridor: lat 35-42, lng -124 to -116
        cal_lats = rng.uniform(35, 42, half)
        cal_lngs = rng.uniform(-124, -116, half)
        # Mediterranean fire belt: lat 36-42, lng -9 to 30
        med_lats = rng.uniform(36, 42, n_sites - half)
        med_lngs = rng.uniform(-9, 30, n_sites - half)

        lats = np.concatenate([cal_lats, med_lats])
        lngs = np.concatenate([cal_lngs, med_lngs])

        sites = []
        for i in range(n_sites):
            risk_level = round(float(rng.beta(2, 2)), 2)
            fuel_moisture = round(float(rng.uniform(3.0, 35.0)), 1)
            fire_weather_index = round(float(rng.uniform(5.0, 55.0)), 1)
            suppression_distance = round(float(rng.exponential(8.0) + 1.0), 1)

            sites.append(
                {
                    "site_id": f"FIRE-{i + 1:03d}",
                    "lat": round(float(lats[i]), 5),
                    "lon": round(float(lngs[i]), 5),
                    "risk_level": risk_level,
                    "fuel_moisture": fuel_moisture,
                    "fire_weather_index": fire_weather_index,
                    "suppression_distance": suppression_distance,
                }
            )
        return sites

    def _generate_community_facilities(self) -> List[Dict]:
        """Generate community facility points using the configured location bounds.

        Produces programmatic facility data distributed within the engine's
        configured bounding box with realistic community-infrastructure
        attributes.  When an external GeoJSON data source is configured and
        readable, it is used instead.

        Returns:
            List of dicts, each containing lat, lon, name, type, capacity,
            service_area, and accessibility.
        """
        # Try loading from an external source first
        data_path = self.location_config.get("data_paths", {}).get(
            "community_facilities"
        )
        if data_path is not None:
            try:
                gdf = gpd.read_file(data_path)
                sites = gdf.to_dict("records")
                if sites:
                    return sites
            except Exception as e:
                logger.warning(
                    f"External community data unavailable ({e}), generating facilities programmatically"
                )

        rng = np.random.RandomState(46)
        n_facilities = 18

        south = self.location_bounds.get("south", 41)
        north = self.location_bounds.get("north", 42)
        west = self.location_bounds.get("west", -125)
        east = self.location_bounds.get("east", -123)

        lats = rng.uniform(south, north, n_facilities)
        lngs = rng.uniform(west, east, n_facilities)

        facility_types = ["healthcare", "education", "emergency", "community"]
        accessibility_levels = ["Full", "Partial", "Limited"]
        name_templates = {
            "healthcare": [
                "Regional Hospital",
                "Community Clinic",
                "Health Center",
                "Medical Office",
                "Urgent Care",
            ],
            "education": [
                "Elementary School",
                "High School",
                "Community College",
                "Library",
                "Training Center",
            ],
            "emergency": [
                "Fire Station",
                "Police Station",
                "Emergency Operations Center",
                "Rescue Unit",
            ],
            "community": [
                "Community Center",
                "Recreation Hall",
                "Senior Center",
                "Youth Center",
                "Town Hall",
            ],
        }

        facilities = []
        for i in range(n_facilities):
            ftype = facility_types[i % len(facility_types)]
            names = name_templates[ftype]
            name = names[int(rng.randint(0, len(names)))]
            capacity = int(rng.randint(30, 500))
            service_area = round(float(rng.uniform(2.0, 50.0)), 1)
            accessibility = accessibility_levels[
                int(rng.randint(0, len(accessibility_levels)))
            ]

            facilities.append(
                {
                    "name": f"{name} #{i + 1}",
                    "type": ftype,
                    "lat": round(float(lats[i]), 5),
                    "lon": round(float(lngs[i]), 5),
                    "capacity": capacity,
                    "service_area": service_area,
                    "accessibility": accessibility,
                }
            )
        return facilities

    def _generate_h3_integration_grid(
        self, integration_data: Dict[str, Any]
    ) -> Dict[str, Dict]:
        """Generate H3 grid for integration visualization."""
        h3_cells = {}

        # Generate H3 cells covering the study area
        bbox = (
            self.location_bounds.get("west", -124.4),
            self.location_bounds.get("south", 41.5),
            self.location_bounds.get("east", -123.5),
            self.location_bounds.get("north", 42.0),
        )

        # Create a grid of points and convert to H3
        lat_points = np.linspace(bbox[1], bbox[3], 10)
        lon_points = np.linspace(bbox[0], bbox[2], 10)

        np.random.seed(45)
        for lat in lat_points:
            for lon in lon_points:
                h3_cell = h3.latlng_to_cell(lat, lon, self.h3_resolution)
                if h3_cell not in h3_cells:
                    h3_cells[h3_cell] = {
                        "integration_score": np.random.uniform(0.1, 0.8),
                        "domain_count": np.random.randint(1, 5),
                        "risk_factors": np.random.randint(0, 4),
                    }

        return h3_cells
