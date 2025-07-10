#!/usr/bin/env python3
"""
Unified H3 Backend for Cascadian Agricultural Land Analysis

This module provides a unified interface for integrating multiple data sources
through H3 spatial indexing, enabling cross-border analysis between California
and Oregon agricultural areas.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import folium
from folium.plugins import HeatMap
# import h3  # REMOVE direct h3 import

# Import shared H3 utility
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill

# Import all the specialized modules (will be created)
from zoning import geo_infer_zoning
from current_use import geo_infer_current_use
from ownership import geo_infer_ownership
from mortgage_debt import geo_infer_mortgage_debt
from improvements import geo_infer_improvements
from surface_water import geo_infer_surface_water
from ground_water import geo_infer_ground_water
from power_source import geo_infer_power_source

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, np.bool8)):
            return bool(obj)
        return super().default(obj)


class CascadianAgriculturalH3Backend:
    """
    Unified H3-indexed backend for comprehensive agricultural land analysis
    across the Cascadian bioregion (Northern California + Oregon).
    """
    
    def __init__(self, resolution: int = 8, bioregion: str = 'Cascadia'):
        """
        Initialize the unified backend with H3 spatial indexing.
        
        Args:
            resolution: H3 resolution level (default: 8)
            bioregion: Bioregion identifier (default: 'Cascadia')
        """
        self.resolution = resolution
        self.bioregion = bioregion
        self.target_hexagons = self._define_target_region()
        
        # Initialize all data modules
        self.modules = {
            'zoning': geo_infer_zoning.GeoInferZoning(resolution),
            'current_use': geo_infer_current_use.GeoInferCurrentUse(resolution),
            'ownership': geo_infer_ownership.GeoInferOwnership(resolution),
            'mortgage_debt': geo_infer_mortgage_debt.GeoInferMortgageDebt(resolution),
            'improvements': geo_infer_improvements.GeoInferImprovements(resolution),
            'surface_water': geo_infer_surface_water.GeoInferSurfaceWater(resolution),
            'ground_water': geo_infer_ground_water.GeoInferGroundWater(resolution),
            'power_source': geo_infer_power_source.GeoInferPowerSource(resolution)
        }
        
        # Initialize unified data storage
        self.unified_data = {}
        
        logger.info(f"CascadiaAgriculturalH3Backend initialized with {len(self.modules)} modules at H3 resolution {resolution}")
    
    def _define_target_region(self) -> List[str]:
        """
        Define the target region using H3 hexagons for bioregional analysis.
        
        Returns:
            List of H3 hexagon identifiers covering the target region
        """
        target_hexagons = []
        
        # Define bioregion boundaries
        bioregion_configs = {
            'Cascadia': {
                'lat_range': (39.0, 46.0),
                'lon_range': (-124.5, -116.0),
                'description': 'Northern California counties and all of Oregon'
            },
            'Columbia': {
                'lat_range': (44.0, 49.0),
                'lon_range': (-124.0, -116.0),
                'description': 'Columbia River Basin region'
            }
        }
        
        config = bioregion_configs.get(self.bioregion, bioregion_configs['Cascadia'])
        
        # Generate sample points across the region
        lat_min, lat_max = config['lat_range']
        lon_min, lon_max = config['lon_range']
        
        # Create grid of sample points
        lat_steps = 12
        lon_steps = 17
        
        for i in range(lat_steps):
            for j in range(lon_steps):
                lat = lat_min + (lat_max - lat_min) * i / (lat_steps - 1)
                lon = lon_min + (lon_max - lon_min) * j / (lon_steps - 1)
                
                try:
                    # Use correct H3 API function
                    try:
                        h3_index = geo_to_h3(lat, lon, self.resolution)
                    except AttributeError:
                        h3_index = h3_to_geo(lat, lon, self.resolution)
                    target_hexagons.append(h3_index)
                except Exception as e:
                    logger.warning(f"Could not generate H3 hexagon for {lat}, {lon}: {e}")
        
        # Remove duplicates and sort
        unique_hexagons = sorted(list(set(target_hexagons)))
        
        logger.info(f"Defined {len(unique_hexagons)} hexagons for {self.bioregion} bioregion")
        return unique_hexagons
    
    def run_comprehensive_analysis(self) -> Dict[str, Dict]:
        """
        Execute all 8 modules and create unified H3-indexed dataset
        
        Returns:
            Comprehensive H3-indexed agricultural data
        """
        results = {}
        
        # Execute each module
        for module_name, module_instance in self.modules.items():
            logger.info(f"Processing {module_name} module...")
            try:
                if module_name == 'zoning':
                    results[module_name] = module_instance.integrate_h3_indexing(
                        module_instance.fetch_comprehensive_zoning_data(), self.resolution
                    )
                elif module_name == 'current_use':
                    results[module_name] = module_instance.process_current_use_h3(
                        year=2024, resolution=self.resolution
                    )
                elif module_name == 'ownership':
                    results[module_name] = module_instance.analyze_ownership_concentration_h3(
                        resolution=self.resolution
                    )
                elif module_name == 'mortgage_debt':
                    results[module_name] = module_instance.estimate_debt_levels_h3(
                        resolution=self.resolution
                    )
                elif module_name == 'improvements':
                    results[module_name] = module_instance.analyze_agricultural_improvements_h3(
                        resolution=self.resolution
                    )
                elif module_name == 'surface_water':
                    results[module_name] = module_instance.analyze_surface_water_rights_h3(
                        resolution=self.resolution
                    )
                elif module_name == 'ground_water':
                    results[module_name] = module_instance.analyze_groundwater_h3(
                        resolution=self.resolution
                    )
                elif module_name == 'power_source':
                    results[module_name] = module_instance.analyze_power_sources_h3(
                        resolution=self.resolution
                    )
            except Exception as e:
                logger.warning(f"Error processing {module_name}: {str(e)}. Skipping.")
                results[module_name] = {}
        
        self.unified_data = self._aggregate_module_results(results)
        return self.unified_data

    def _aggregate_module_results(self, results: Dict[str, Dict]) -> Dict[str, Dict]:
        aggregated = {}
        for hexagon in self.target_hexagons:
            hex_data = {}
            for module, module_data in results.items():
                hex_data[module] = module_data.get(hexagon, {})
            # Ensure lat_lng is always present
            hex_data['lat_lng'] = self._h3_to_latlng(hexagon)
            aggregated[hexagon] = hex_data
        return aggregated
    
    def _h3_to_latlng(self, h3_index: str) -> Tuple[float, float]:
        """
        Convert H3 index to latitude/longitude coordinates.
        
        Args:
            h3_index: H3 hexagon index
            
        Returns:
            Tuple of (latitude, longitude)
        """
        try:
            # Use correct H3 API function
            try:
                return h3_to_geo(h3_index)
            except AttributeError:
                return h3_to_geo(h3_index)
        except Exception as e:
            logger.warning(f"Could not convert H3 index {h3_index} to lat/lng: {e}")
            return (0.0, 0.0)
    
    def calculate_agricultural_redevelopment_potential(self) -> Dict[str, Any]:
        """
        Calculate agricultural redevelopment potential scores for each H3 hexagon
        
        Returns:
            Dictionary of redevelopment scores and factors for each hexagon
        """
        if not self.unified_data:
            logger.warning("No unified data available. Running comprehensive analysis...")
            self.run_comprehensive_analysis()
        
        scores = {}
        for hexagon in self.target_hexagons:
            hex_data = self.unified_data.get(hexagon, {})
            
            # Calculate individual scores with defaults
            zoning_score = self._calculate_zoning_score(hex_data.get('zoning', {})) if 'zoning' in hex_data else 0.5
            use_score = self._calculate_use_score(hex_data.get('current_use', {})) if 'current_use' in hex_data else 0.5
            water_score = self._calculate_water_score(
                hex_data.get('surface_water', {}), 
                hex_data.get('ground_water', {})
            ) if all(k in hex_data for k in ['surface_water', 'ground_water']) else 0.5
            infra_score = self._calculate_infrastructure_score(
                hex_data.get('improvements', {}), 
                hex_data.get('power_source', {})
            ) if all(k in hex_data for k in ['improvements', 'power_source']) else 0.5
            ownership_score = hex_data.get('ownership', {}).get('concentration_score', 0.5) if 'ownership' in hex_data else 0.5
            debt_score = hex_data.get('mortgage_debt', {}).get('debt_level_score', 0.5) if 'mortgage_debt' in hex_data else 0.5
            
            # Weighted average
            total_score = (
                zoning_score * 0.2 + 
                use_score * 0.2 + 
                water_score * 0.2 + 
                infra_score * 0.15 + 
                ownership_score * 0.15 + 
                debt_score * 0.1
            )
            
            scores[hexagon] = {
                'total_score': total_score,
                'factors': {
                    'zoning': zoning_score,
                    'current_use': use_score,
                    'water': water_score,
                    'infrastructure': infra_score,
                    'ownership': ownership_score,
                    'debt': debt_score
                }
            }
        
        return scores
    
    def _calculate_zoning_score(self, zoning_data: Dict) -> float:
        """Calculate zoning favorability score (0-1)"""
        if not zoning_data or zoning_data.get('status') == 'error':
            return 0.0
        
        # Simple scoring based on agricultural zoning presence
        agricultural_zones = ['agricultural', 'farm', 'exclusive_farm_use', 'ag', 'prime_farmland']
        
        zone_type = zoning_data.get('zone_type', '').lower()
        if any(ag_zone in zone_type for ag_zone in agricultural_zones):
            return 0.8
        elif 'rural' in zone_type:
            return 0.6
        elif 'residential' in zone_type:
            return 0.3
        else:
            return 0.1
    
    def _calculate_use_score(self, current_use_data: Dict) -> float:
        """Calculate current use compatibility score (0-1)"""
        if not current_use_data or current_use_data.get('status') == 'error':
            return 0.0
        
        # Score based on current agricultural use
        current_use = current_use_data.get('primary_use', '').lower()
        if 'crop' in current_use or 'farm' in current_use:
            return 0.9
        elif 'pasture' in current_use or 'grazing' in current_use:
            return 0.7
        elif 'fallow' in current_use:
            return 0.8
        elif 'forest' in current_use:
            return 0.4
        else:
            return 0.2
    
    def _calculate_water_score(self, surface_water_data: Dict, ground_water_data: Dict) -> float:
        """Calculate water access score (0-1)"""
        surface_score = 0.0
        ground_score = 0.0
        
        if surface_water_data and surface_water_data.get('status') != 'error':
            if surface_water_data.get('has_surface_rights', False):
                surface_score = 0.8
            elif surface_water_data.get('nearby_water_bodies', False):
                surface_score = 0.4
        
        if ground_water_data and ground_water_data.get('status') != 'error':
            if ground_water_data.get('has_well_access', False):
                ground_score = 0.6
            elif ground_water_data.get('aquifer_access', False):
                ground_score = 0.4
        
        return max(surface_score, ground_score)
    
    def _calculate_infrastructure_score(self, improvements_data: Dict, power_data: Dict) -> float:
        """Calculate infrastructure availability score (0-1)"""
        improvements_score = 0.0
        power_score = 0.0
        
        if improvements_data and improvements_data.get('status') != 'error':
            if improvements_data.get('has_buildings', False):
                improvements_score += 0.3
            if improvements_data.get('has_irrigation', False):
                improvements_score += 0.4
            if improvements_data.get('has_roads', False):
                improvements_score += 0.2
        
        if power_data and power_data.get('status') != 'error':
            if power_data.get('has_grid_power', False):
                power_score = 0.8
            elif power_data.get('has_renewable_power', False):
                power_score = 0.6
        
        return min(1.0, improvements_score + power_score * 0.5)
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary of the analysis.
        
        Returns:
            Dictionary containing analysis summary
        """
        if not self.unified_data:
            return {
                'error': 'No unified data available',
                'total_hexagons': len(self.target_hexagons),
                'modules_analyzed': 0
            }
        
        summary = {
            'total_hexagons': len(self.target_hexagons),
            'h3_resolution': self.resolution,
            'bioregion': self.bioregion,
            'analysis_timestamp': datetime.now().isoformat(),
            'modules_analyzed': len(self.modules),
            'module_summaries': {}
        }
        
        # Analyze each module's results
        for module_name in self.modules.keys():
            module_results = []
            errors = 0
            
            for hexagon_data in self.unified_data.values():
                module_data = hexagon_data.get(module_name, {})
                if module_data.get('status') == 'error':
                    errors += 1
                else:
                    module_results.append(module_data)
            
            summary['module_summaries'][module_name] = {
                'total_hexagons': len(self.target_hexagons),
                'successful_hexagons': len(module_results),
                'error_count': errors,
                'success_rate': len(module_results) / len(self.target_hexagons) if self.target_hexagons else 0
            }
        
        return summary
    
    def export_unified_data(self, output_path: str, export_format: str = 'geojson') -> None:
        """
        Export unified data to specified format.
        
        Args:
            output_path: Output file path
            export_format: Export format (geojson, csv, json)
        """
        if not self.unified_data:
            raise ValueError("No unified data available to export")
        
        if export_format.lower() == 'geojson':
            self._export_geojson(output_path)
        elif export_format.lower() == 'csv':
            self._export_csv(output_path)
        elif export_format.lower() == 'json':
            self._export_json(output_path)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_geojson(self, output_path: str) -> None:
        """Export data as GeoJSON"""
        features = []
        
        for hexagon, data in self.unified_data.items():
            # Get hexagon boundary
            try:
                try:
                    boundary = h3_to_geo_boundary(hexagon)
                except AttributeError:
                    boundary = h3_to_geo_boundary(hexagon)
                coordinates = [[[point[1], point[0]] for point in boundary]]
                
                lat, lng = self._h3_to_latlng(hexagon)
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": coordinates
                    },
                    "properties": {
                        "h3_index": hexagon,
                        "resolution": self.resolution,
                        "lat": lat,
                        "lng": lng,
                        **data
                    }
                }
                features.append(feature)
            except Exception as e:
                logger.warning(f"Could not export hexagon {hexagon}: {e}")
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        
        with open(output_path, 'w') as f:
            json.dump(geojson_data, f, indent=2, cls=NumpyEncoder)
    
    def _export_csv(self, output_path: str) -> None:
        """Export data as CSV"""
        rows = []
        
        for hexagon, data in self.unified_data.items():
            row = {
                'h3_index': hexagon,
                'lat': data['lat_lng'][0],
                'lng': data['lat_lng'][1],
                'resolution': self.resolution
            }
            
            # Flatten module data
            for module_name, module_data in data['modules'].items():
                if isinstance(module_data, dict):
                    for key, value in module_data.items():
                        row[f"{module_name}_{key}"] = value
                else:
                    row[module_name] = module_data
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
    
    def _export_json(self, output_path: str) -> None:
        """Export data as JSON"""
        with open(output_path, 'w') as f:
            json.dump(self.unified_data, f, indent=2, cls=NumpyEncoder)
    
    def generate_interactive_dashboard(self, output_path: str) -> None:
        """
        Generate an interactive HTML dashboard with layer toggles.
        
        Args:
            output_path: Output path for the HTML dashboard
        """
        if not self.unified_data:
            logger.warning("No unified data available for dashboard generation")
            return
        
        # Calculate center of the region
        lats = [data['lat_lng'][0] for data in self.unified_data.values()]
        lngs = [data['lat_lng'][1] for data in self.unified_data.values()]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add alternative tile layers
        folium.TileLayer('Stamen Terrain', attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
        folium.TileLayer('CartoDB positron', attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
        
        # Create feature groups for different data layers
        feature_groups = {}
        
        for module_name in self.modules.keys():
            feature_groups[module_name] = folium.FeatureGroup(
                name=f"{module_name.replace('_', ' ').title()} Data"
            )
        
        # Add hexagon data to appropriate layers
        for hexagon, data in self.unified_data.items():
            lat, lng = data['lat_lng']
            
            # Skip invalid coordinates
            if lat == 0.0 and lng == 0.0:
                continue
            
            # Get hexagon boundary for polygon overlay
            try:
                boundary = h3_to_geo_boundary(hexagon)
                boundary_coords = [[point[0], point[1]] for point in boundary]
                
                # Create popup content
                popup_content = f"""
                <div style="width: 300px;">
                    <h4>H3 Index: {hexagon}</h4>
                    <p><b>Coordinates:</b> {lat:.4f}, {lng:.4f}</p>
                    <p><b>Resolution:</b> {self.resolution}</p>
                    <hr>
                """
                
                # Add module data to popup
                for module_name, module_data in data['modules'].items():
                    status = module_data.get('status', 'unknown')
                    popup_content += f"<p><b>{module_name.replace('_', ' ').title()}:</b> {status}</p>"
                
                popup_content += "</div>"
                
                # Add polygon to each relevant feature group
                for module_name, module_data in data['modules'].items():
                    if module_data.get('status') != 'error':
                        # Color based on module type
                        colors = {
                            'zoning': 'blue',
                            'current_use': 'green',
                            'ownership': 'purple',
                            'surface_water': 'cyan',
                            'ground_water': 'navy',
                            'improvements': 'orange',
                            'power_source': 'red',
                            'mortgage_debt': 'brown'
                        }
                        
                        color = colors.get(module_name, 'gray')
                        
                        folium.Polygon(
                            locations=boundary_coords,
                            color=color,
                            weight=2,
                            fillOpacity=0.3,
                            popup=folium.Popup(popup_content, max_width=300)
                        ).add_to(feature_groups[module_name])
                
            except Exception as e:
                logger.warning(f"Could not add hexagon {hexagon} to map: {e}")
        
        # Add feature groups to map
        for fg in feature_groups.values():
            fg.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add a title
        title_html = f'''
        <h3 align="center" style="font-size:20px"><b>{self.bioregion} Agricultural Land Analysis Dashboard</b></h3>
        <p align="center">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p align="center">H3 Resolution: {self.resolution} | Total Hexagons: {len(self.unified_data)}</p>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save the map
        m.save(output_path)
        logger.info(f"Interactive dashboard saved to {output_path}") 