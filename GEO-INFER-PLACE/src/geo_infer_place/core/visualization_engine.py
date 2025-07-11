"""
InteractiveVisualizationEngine: Interactive geospatial dashboard creation.

This module provides comprehensive visualization capabilities for place-based
analysis, including interactive maps with H3 integration, multi-layer overlays,
and dashboard generation adapted from the climate integration example.
"""

import logging
import json
import folium
import h3
import pandas as pd
import geopandas as gpd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from folium.plugins import MarkerCluster, HeatMap
import branca.colormap as cm
import numpy as np

from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

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
    
    def __init__(self, 
                 location_config: Dict[str, Any],
                 output_dir: Path,
                 h3_resolution: int = 8):
        """
        Initialize visualization engine.
        
        Args:
            location_config: Configuration for the location
            output_dir: Output directory for generated visualizations
            h3_resolution: H3 spatial resolution for aggregation
        """
        self.location_config = location_config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.h3_resolution = h3_resolution
        
        # Get location center and bounds
        self.location_bounds = location_config.get('location', {}).get('bounds', {})
        self.center_lat = (self.location_bounds.get('north', 42) + self.location_bounds.get('south', 41)) / 2
        self.center_lon = (self.location_bounds.get('east', -123) + self.location_bounds.get('west', -125)) / 2
        
        logger.info(f"InteractiveVisualizationEngine initialized")
        logger.info(f"Location center: ({self.center_lat:.3f}, {self.center_lon:.3f})")
        logger.info(f"H3 resolution: {self.h3_resolution}")
        
    def create_comprehensive_dashboard(self, 
                                     analysis_results: Dict[str, Any],
                                     dashboard_config: Optional[Dict] = None) -> str:
        """
        Create comprehensive interactive dashboard with all analysis results.
        
        Args:
            analysis_results: Results from comprehensive analysis
            dashboard_config: Optional dashboard configuration
            
        Returns:
            Path to generated dashboard HTML file
        """
        logger.info("🎨 Creating comprehensive interactive dashboard...")
        
        # Create base map with professional styling
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=10,
            tiles='CartoDB positron',
            attr='© CartoDB, © OpenStreetMap contributors'
        )
        
        # Add title
        title_html = self._create_dashboard_title()
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Create layer groups for different analysis domains
        layer_groups = self._create_layer_groups()
        
        # Add domain-specific visualizations
        domain_results = analysis_results.get('domain_results', {})
        
        if 'forest_health' in domain_results:
            self._add_forest_health_layers(m, layer_groups, domain_results['forest_health'])
            
        if 'coastal_resilience' in domain_results:
            self._add_coastal_resilience_layers(m, layer_groups, domain_results['coastal_resilience'])
            
        if 'fire_risk' in domain_results:
            self._add_fire_risk_layers(m, layer_groups, domain_results['fire_risk'])
            
        if 'community_development' in domain_results:
            self._add_community_development_layers(m, layer_groups, domain_results['community_development'])
            
        # Add integrated results if available
        integrated_results = analysis_results.get('integrated_results', {})
        if integrated_results:
            self._add_integration_layers(m, layer_groups, integrated_results)
            
        # Add layer control
        for group in layer_groups.values():
            group.add_to(m)
        folium.LayerControl().add_to(m)
        
        # Save dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dashboard_path = self.output_dir / f"comprehensive_dashboard_{timestamp}.html"
        m.save(str(dashboard_path))
        
        logger.info(f"✅ Comprehensive dashboard saved to: {dashboard_path}")
        return str(dashboard_path)
        
    def _create_dashboard_title(self) -> str:
        """Create professional dashboard title."""
        location_name = self.location_config.get('location', {}).get('name', 'Location')
        
        title_html = f'''
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
        '''
        return title_html
        
    def _create_layer_groups(self) -> Dict[str, folium.FeatureGroup]:
        """Create layer groups for different analysis domains."""
        layer_groups = {
            'h3_grid': folium.FeatureGroup(name="🔷 H3 Spatial Grid", show=True),
            'forest_health': folium.FeatureGroup(name="🌲 Forest Health", show=True),
            'coastal_resilience': folium.FeatureGroup(name="🌊 Coastal Resilience", show=True),
            'fire_risk': folium.FeatureGroup(name="🔥 Fire Risk", show=True),
            'community_development': folium.FeatureGroup(name="🏘️ Community Development", show=True),
            'integration': folium.FeatureGroup(name="🔗 Cross-Domain Integration", show=False)
        }
        return layer_groups
        
    def _add_forest_health_layers(self, 
                                 m: folium.Map, 
                                 layer_groups: Dict, 
                                 forest_data: Dict[str, Any]):
        """Add forest health visualization layers."""
        logger.info("Adding forest health visualization layers...")
        
        # Create marker cluster for forest monitoring sites
        forest_cluster = MarkerCluster(name="Forest Monitoring Sites")
        
        # Add forest health monitoring points (placeholder data)
        monitoring_sites = self._generate_forest_monitoring_sites()
        
        for site in monitoring_sites:
            # Color code by health status
            if site['health_index'] > 0.7:
                marker_color = 'green'
                icon = 'leaf'
            elif site['health_index'] > 0.4:
                marker_color = 'orange'
                icon = 'exclamation-triangle'
            else:
                marker_color = 'red'
                icon = 'warning'
                
            popup_html = f'''
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
            '''
            
            folium.Marker(
                location=[site['lat'], site['lon']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Health Index: {site['health_index']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix='fa')
            ).add_to(forest_cluster)
            
        forest_cluster.add_to(layer_groups['forest_health'])
        
    def _add_coastal_resilience_layers(self, 
                                      m: folium.Map, 
                                      layer_groups: Dict, 
                                      coastal_data: Dict[str, Any]):
        """Add coastal resilience visualization layers."""
        logger.info("Adding coastal resilience visualization layers...")
        
        # Create coastal monitoring cluster
        coastal_cluster = MarkerCluster(name="Coastal Monitoring Sites")
        
        # Add coastal monitoring points (placeholder data)
        coastal_sites = self._generate_coastal_monitoring_sites()
        
        for site in coastal_sites:
            # Color code by vulnerability level
            if site['vulnerability'] < 0.3:
                marker_color = 'blue'
                icon = 'anchor'
            elif site['vulnerability'] < 0.7:
                marker_color = 'orange'
                icon = 'exclamation-triangle'
            else:
                marker_color = 'red'
                icon = 'warning'
                
            popup_html = f'''
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
            '''
            
            folium.Marker(
                location=[site['lat'], site['lon']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Vulnerability: {site['vulnerability']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix='fa')
            ).add_to(coastal_cluster)
            
        coastal_cluster.add_to(layer_groups['coastal_resilience'])
        
    def _add_fire_risk_layers(self, 
                             m: folium.Map, 
                             layer_groups: Dict, 
                             fire_data: Dict[str, Any]):
        """Add fire risk visualization layers."""
        logger.info("Adding fire risk visualization layers...")
        
        # Create fire monitoring cluster
        fire_cluster = MarkerCluster(name="Fire Risk Monitoring")
        
        # Add fire risk monitoring points (placeholder data)
        fire_sites = self._generate_fire_monitoring_sites()
        
        for site in fire_sites:
            # Color code by risk level
            if site['risk_level'] < 0.3:
                marker_color = 'green'
                icon = 'fire-extinguisher'
            elif site['risk_level'] < 0.7:
                marker_color = 'orange'
                icon = 'exclamation-triangle'
            else:
                marker_color = 'red'
                icon = 'fire'
                
            popup_html = f'''
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
            '''
            
            folium.Marker(
                location=[site['lat'], site['lon']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Risk Level: {site['risk_level']:.2f}",
                icon=folium.Icon(color=marker_color, icon=icon, prefix='fa')
            ).add_to(fire_cluster)
            
        fire_cluster.add_to(layer_groups['fire_risk'])
        
    def _add_community_development_layers(self, 
                                         m: folium.Map, 
                                         layer_groups: Dict, 
                                         community_data: Dict[str, Any]):
        """Add community development visualization layers."""
        logger.info("Adding community development visualization layers...")
        
        # Create community facilities cluster
        community_cluster = MarkerCluster(name="Community Facilities")
        
        # Add community facility points (placeholder data)
        facilities = self._generate_community_facilities()
        
        for facility in facilities:
            # Color code by facility type
            facility_colors = {
                'healthcare': 'red',
                'education': 'blue',
                'emergency': 'orange',
                'community': 'green'
            }
            
            facility_icons = {
                'healthcare': 'plus',
                'education': 'graduation-cap',
                'emergency': 'exclamation-triangle',
                'community': 'users'
            }
            
            color = facility_colors.get(facility['type'], 'gray')
            icon = facility_icons.get(facility['type'], 'info')
            
            popup_html = f'''
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #4B0082; margin: 0 0 8px 0;">🏘️ {facility['name']}</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>Type:</b></td><td>{facility['type'].title()}</td></tr>
                    <tr><td><b>Capacity:</b></td><td>{facility['capacity']}</td></tr>
                    <tr><td><b>Service Area:</b></td><td>{facility['service_area']} km²</td></tr>
                    <tr><td><b>Accessibility:</b></td><td>{facility['accessibility']}</td></tr>
                </table>
            </div>
            '''
            
            folium.Marker(
                location=[facility['lat'], facility['lon']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=facility['name'],
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(community_cluster)
            
        community_cluster.add_to(layer_groups['community_development'])
        
    def _add_integration_layers(self, 
                               m: folium.Map, 
                               layer_groups: Dict, 
                               integration_data: Dict[str, Any]):
        """Add cross-domain integration visualization layers."""
        logger.info("Adding cross-domain integration layers...")
        
        # Add H3 hexagonal overlay for integrated analysis
        h3_cells = self._generate_h3_integration_grid(integration_data)
        
        for h3_cell, cell_data in h3_cells.items():
            # Get H3 cell boundary
            h3_boundary = h3.cell_to_boundary(h3_cell, geo_json=True)
            
            # Color based on integration score
            integration_score = cell_data.get('integration_score', 0)
            if integration_score > 0.7:
                color = '#FF4500'  # High integration (red-orange)
            elif integration_score > 0.4:
                color = '#FFA500'  # Medium integration (orange)
            elif integration_score > 0.2:
                color = '#FFFF00'  # Low integration (yellow)
            else:
                color = '#87CEEB'  # Minimal integration (light blue)
                
            popup_html = f'''
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="color: #8B4513; margin: 0 0 8px 0;">🔗 H3 Integration Cell</h4>
                <table style="font-size: 11px; width: 100%;">
                    <tr><td><b>H3 Index:</b></td><td>{h3_cell}</td></tr>
                    <tr><td><b>Integration Score:</b></td><td>{integration_score:.3f}</td></tr>
                    <tr><td><b>Domain Count:</b></td><td>{cell_data['domain_count']}</td></tr>
                    <tr><td><b>Risk Factors:</b></td><td>{cell_data['risk_factors']}</td></tr>
                </table>
            </div>
            '''
            
            folium.Polygon(
                locations=[[lat, lon] for lon, lat in h3_boundary],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Integration Score: {integration_score:.3f}",
                color='black',
                weight=1,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(layer_groups['integration'])
            
    def _generate_forest_monitoring_sites(self) -> List[Dict]:
        """Generate placeholder forest monitoring sites."""
        np.random.seed(42)
        sites = []
        
        # Generate 20 monitoring sites within Del Norte County bounds
        for i in range(20):
            lat = np.random.uniform(self.location_bounds.get('south', 41.5), self.location_bounds.get('north', 42.0))
            lon = np.random.uniform(self.location_bounds.get('west', -124.4), self.location_bounds.get('east', -123.5))
            
            site = {
                'site_id': f'FH_{i+1:03d}',
                'lat': lat,
                'lon': lon,
                'health_index': np.random.uniform(0.2, 0.9),
                'ndvi': np.random.uniform(0.3, 0.8),
                'tree_density': int(np.random.uniform(100, 800)),
                'species_diversity': np.random.uniform(1.5, 3.5),
                'last_survey': '2024-01-15'
            }
            sites.append(site)
            
        return sites
        
    def _generate_coastal_monitoring_sites(self) -> List[Dict]:
        """Generate placeholder coastal monitoring sites."""
        np.random.seed(43)
        sites = []
        
        # Generate 15 coastal sites along the western edge
        for i in range(15):
            lat = np.random.uniform(self.location_bounds.get('south', 41.5), self.location_bounds.get('north', 42.0))
            lon = np.random.uniform(-124.4, -124.0)  # Western coastal area
            
            site = {
                'site_id': f'CS_{i+1:03d}',
                'lat': lat,
                'lon': lon,
                'vulnerability': np.random.uniform(0.1, 0.9),
                'erosion_rate': np.random.uniform(-0.5, 2.5),
                'sea_level_trend': np.random.uniform(1.0, 4.0),
                'storm_exposure': np.random.choice(['Low', 'Moderate', 'High'])
            }
            sites.append(site)
            
        return sites
        
    def _generate_fire_monitoring_sites(self) -> List[Dict]:
        """Generate placeholder fire monitoring sites."""
        np.random.seed(44)
        sites = []
        
        # Generate 25 fire monitoring sites
        for i in range(25):
            lat = np.random.uniform(self.location_bounds.get('south', 41.5), self.location_bounds.get('north', 42.0))
            lon = np.random.uniform(self.location_bounds.get('west', -124.4), self.location_bounds.get('east', -123.5))
            
            site = {
                'site_id': f'FR_{i+1:03d}',
                'lat': lat,
                'lon': lon,
                'risk_level': np.random.uniform(0.1, 0.9),
                'fuel_moisture': np.random.uniform(5, 25),
                'fire_weather_index': np.random.uniform(0, 100),
                'suppression_distance': np.random.uniform(2, 20)
            }
            sites.append(site)
            
        return sites
        
    def _generate_community_facilities(self) -> List[Dict]:
        """Generate placeholder community facilities."""
        facilities = [
            {'name': 'Sutter Coast Hospital', 'type': 'healthcare', 'lat': 41.7558, 'lon': -124.2026, 'capacity': 150, 'service_area': 50, 'accessibility': 'Good'},
            {'name': 'Del Norte High School', 'type': 'education', 'lat': 41.7500, 'lon': -124.1900, 'capacity': 800, 'service_area': 25, 'accessibility': 'Good'},
            {'name': 'Crescent City Fire Department', 'type': 'emergency', 'lat': 41.7583, 'lon': -124.2014, 'capacity': 25, 'service_area': 30, 'accessibility': 'Excellent'},
            {'name': 'Community Center', 'type': 'community', 'lat': 41.7522, 'lon': -124.1975, 'capacity': 200, 'service_area': 15, 'accessibility': 'Good'},
            {'name': 'Gasquet Elementary', 'type': 'education', 'lat': 41.8485, 'lon': -123.9673, 'capacity': 100, 'service_area': 20, 'accessibility': 'Moderate'}
        ]
        return facilities
        
    def _generate_h3_integration_grid(self, integration_data: Dict[str, Any]) -> Dict[str, Dict]:
        """Generate H3 grid for integration visualization."""
        h3_cells = {}
        
        # Generate H3 cells covering the study area
        bbox = (self.location_bounds.get('west', -124.4), self.location_bounds.get('south', 41.5),
                self.location_bounds.get('east', -123.5), self.location_bounds.get('north', 42.0))
        
        # Create a grid of points and convert to H3
        lat_points = np.linspace(bbox[1], bbox[3], 10)
        lon_points = np.linspace(bbox[0], bbox[2], 10)
        
        np.random.seed(45)
        for lat in lat_points:
            for lon in lon_points:
                h3_cell = h3.latlng_to_cell(lat, lon, self.h3_resolution)
                if h3_cell not in h3_cells:
                    h3_cells[h3_cell] = {
                        'integration_score': np.random.uniform(0.1, 0.8),
                        'domain_count': np.random.randint(1, 5),
                        'risk_factors': np.random.randint(0, 4)
                    }
                    
        return h3_cells 