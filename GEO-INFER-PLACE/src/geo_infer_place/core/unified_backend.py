#!/usr/bin/env python3
"""
Unified H3 Backend for Cascadian Agricultural Land Analysis

This module provides a unified interface for integrating multiple data sources
through H3 spatial indexing, enabling cross-border analysis between California
and Oregon agricultural areas.
"""
import sys
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import logging
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, mapping
import folium
from folium.plugins import HeatMap, MarkerCluster

# --- H3 and OSC Integration ---
import h3
from geo_infer_space.osc_geo import create_h3_data_loader, H3DataLoader

# --- Local Core Imports ---
# Base class for type hinting
from .base_module import BaseAnalysisModule
from geo_infer_space.core.unified_backend import UnifiedH3Backend, NumpyEncoder

logger = logging.getLogger(__name__)


class CascadianAgriculturalH3Backend(UnifiedH3Backend):
    """
    Unified H3-indexed backend for comprehensive agricultural land analysis
    across the Cascadian bioregion (Northern California + Oregon).
    """
    
    def __init__(self,
                 modules: Dict[str, 'BaseAnalysisModule'],
                 resolution: int = 8,
                 bioregion: str = 'Cascadia',
                 target_counties: Optional[Dict[str, List[str]]] = None,
                 base_data_dir: Optional[Path] = None,
                 osc_repo_dir: Optional[str] = None):
        """
        Initialize the unified backend with H3 spatial indexing.
        
        Args:
            modules: A dictionary of initialized analysis module instances.
            resolution: H3 resolution level (default: 8)
            bioregion: Bioregion identifier (default: 'Cascadia')
            target_counties: A dict specifying counties to run, e.g., {'CA': ['all']}.
            base_data_dir: The root directory for data caching.
            osc_repo_dir: The root directory of the cloned OS-Climate repositories.
        """
        super().__init__(modules, resolution, bioregion, target_counties, base_data_dir, osc_repo_dir)
        # Add Cascadia-specific initialization here
        self.target_hexagons_by_state, self.target_hexagons = self._define_target_region(target_counties)
        
        logger.info(f"CascadianAgriculturalH3Backend initialized for '{self.bioregion}' with {len(self.modules)} active modules at H3 resolution {self.resolution}")
        logger.info(f"Active modules: {list(self.modules.keys())}")
        logger.info(f"Defined {len(self.target_hexagons)} total target hexagons across {len(self.target_hexagons_by_state)} states.")

    def _define_target_region(self, target_counties: Optional[Dict[str, List[str]]] = None) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Define the target region using H3 hexagons, categorized by state and filtered by county.
        
        This method loads county geometries from a GeoJSON file and generates H3 hexagons
        that cover the specified counties.

        Args:
            target_counties: A dictionary specifying counties to run, e.g., 
                             {'CA': ['Lassen', 'Plumas'], 'OR': ['all']}.
                             If None, defaults to the entire bioregion.

        Returns:
            A tuple containing:
            - A dictionary of H3 hexagon identifiers, keyed by state ('CA', 'OR', 'WA').
            - A list of all unique H3 hexagon identifiers across all filtered areas.
        """
        county_geoms = self._get_county_geometries(target_counties)

        if not county_geoms:
            logger.error("No county geometries could be loaded or defined. Cannot define a target region.")
            return {}, []

        hexagons_by_state: Dict[str, set] = {state: set() for state in county_geoms.keys()}
        
        for state, counties in county_geoms.items():
            for county_name, geom in counties.items():
                logger.info(f"Generating hexagons for {county_name}, {state}...")
                try:
                    # For MultiPolygons, polyfill each part
                    if isinstance(geom, (Polygon, MultiPolygon)):
                         hexagons_in_county = h3.polyfill_geojson(mapping(geom), self.resolution)
                         hexagons_by_state[state].update(hexagons_in_county)
                    else:
                        logger.warning(f"Skipping invalid geometry for {county_name}, {state}")
                except Exception as e:
                    logger.error(f"H3 polyfill failed for {county_name}, {state}: {e}")

        final_hex_by_state = {k: sorted(list(v)) for k, v in hexagons_by_state.items() if v}
        final_all_hexagons = sorted(list(set.union(*hexagons_by_state.values())))
            
        if not final_all_hexagons:
            logger.error(f"Failed to generate any H3 hexagons for bioregion '{self.bioregion}' with filters {target_counties}")
            return {}, []
            
        return final_hex_by_state, final_all_hexagons

    def _get_county_geometries(self, target_counties: Optional[Dict[str, List[str]]]) -> Dict[str, Dict[str, Any]]:
        """
        Loads county geometries for the specified states and counties from a GeoJSON file.
        Falls back to placeholder bounding boxes if the file is not found.
        """
        if not target_counties:
            return {}

        # The data file is in the GEO-INFER-PLACE/data directory
        package_root = Path(__file__).resolve().parents[2] # .../GEO-INFER-PLACE
        geometries_path = package_root / 'data' / 'us_counties_simple.geojson'
        
        output_geoms = {}
        
        try:
            if not geometries_path.exists():
                raise FileNotFoundError(f"US County geometry file not found at {geometries_path}")

            logger.info(f"Loading county geometries from {geometries_path}")
            counties_gdf = gpd.read_file(geometries_path)
            
            for state, counties in target_counties.items():
                output_geoms[state] = {}
                state_gdf = counties_gdf[counties_gdf['STATE_ABBR'] == state]
                
                if not state_gdf.empty:
                    if 'all' in counties:
                        for _, row in state_gdf.iterrows():
                            output_geoms[state][row['NAME']] = row['geometry']
                    else:
                        for county_name in counties:
                            county_geom = state_gdf[state_gdf['NAME'] == county_name]
                            if not county_geom.empty:
                                output_geoms[state][county_name] = county_geom.iloc[0]['geometry']
                            else:
                                logger.warning(f"Could not find geometry for county '{county_name}' in state '{state}'")

        except Exception as e:
            logger.warning(f"Could not load county geometries from file ({e}). Falling back to placeholder bounding boxes.")
            # Placeholder geometries (broad bounding boxes)
            placeholder_geoms = {
                'CA': {'all': Polygon.from_bounds(-124.5, 32.5, -114.0, 42.0)},
                'OR': {'all': Polygon.from_bounds(-124.6, 42.0, -116.4, 46.3)},
                'WA': {'all': Polygon.from_bounds(-124.8, 45.5, -116.9, 49.0)}
            }
            for state, counties in target_counties.items():
                if state in placeholder_geoms:
                    output_geoms[state] = {'all': placeholder_geoms[state]['all']}

        return output_geoms

    def run_comprehensive_analysis(self) -> None:
        """
        Execute the full analysis pipeline for all active modules.
        This follows the standardized workflow:
        1.  Check for cached H3 data.
        2.  If not cached, acquire raw data.
        3.  Process raw data to H3 using the OSC loader.
        4.  Run the module's final analysis on the H3 data.
        5.  Aggregate results.
        """
        logger.info("Starting comprehensive analysis...")
        module_results = {}

        for name, module in self.modules.items():
            logger.info(f"--- Processing Module: {name.upper()} ---")
            try:
                # Each module instance now has a reference to the backend and its methods.
                # The module's run_analysis method is responsible for orchestrating
                # its specific logic for acquisition, processing, and analysis.
                result = module.run_analysis()
                module_results[name] = result
                logger.info(f"Successfully processed module: {name.upper()}")
            except Exception as e:
                logger.error(f"Failed to process module {name.upper()}: {e}", exc_info=True)
                module_results[name] = {}
        
        self._aggregate_module_results(module_results)
        logger.info("Comprehensive analysis complete. All module data has been aggregated.")
    
    def _aggregate_module_results(self, results: Dict[str, Dict]):
        """Combine all module results into a unified H3-indexed dataset."""
        logger.info("Aggregating results from all modules...")
        
        for hexagon in self.target_hexagons:
            hex_data = {'hex_id': hexagon}
            
            # Add geometry and metadata
            try:
                hex_data['centroid'] = h3.h3_to_geo_boundary(hexagon, geo_json=True)
                hex_data['boundary'] = h3.h3_to_geo_boundary(hexagon, geo_json=True)
            except Exception as e:
                logger.warning(f"Could not process geometry for {hexagon}: {e}")
                hex_data['centroid'] = None
                hex_data['boundary'] = None

            # Add module data
            for module_name, module_data in results.items():
                hex_data[module_name] = module_data.get(hexagon, {})
            
            self.unified_data[hexagon] = hex_data
            
        logger.info(f"Aggregated data for {len(self.target_hexagons)} hexagons from {len(results)} modules.")

    def calculate_agricultural_redevelopment_potential(self) -> Dict[str, Dict]:
        """
        Calculate redevelopment scores based on the unified dataset.
        
        Returns:
            Dictionary of redevelopment scores for each hexagon.
        """
        logger.info("Calculating agricultural redevelopment potential scores...")
        if not self.unified_data:
            logger.warning("Unified data is not available. Cannot calculate redevelopment scores.")
            return {}

        for h3_index, hex_data in self.unified_data.items():
            scores = {
                'zoning': self._score_zoning(hex_data.get('zoning', {})),
                'current_use': self._score_current_use(hex_data.get('current_use', {})),
                'water': self._score_water(hex_data.get('surface_water', {}), hex_data.get('ground_water', {})),
                'water_rights': self._score_water_rights(hex_data.get('water_rights', {})),
                'infrastructure': self._score_infrastructure(hex_data.get('improvements', {}), hex_data.get('power_source', {})),
                'ownership': self._score_ownership(hex_data.get('ownership', {})),
                'debt': self._score_mortgage_debt(hex_data.get('mortgage_debt', {}))
            }

            # Weighted composite score
            # Weights based on research document priorities, adjusted for new data
            composite_score = (
                scores['zoning'] * 0.20 +
                scores['water'] * 0.20 +
                scores['water_rights'] * 0.10 +
                scores['infrastructure'] * 0.20 +
                scores['ownership'] * 0.15 +
                scores['debt'] * 0.15
            ) / 1.0  # Normalizing factor

            self.redevelopment_scores[h3_index] = {
                'composite_score': composite_score,
                'factors': scores
            }
            
        logger.info(f"Calculated redevelopment scores for {len(self.redevelopment_scores)} hexagons.")
        return self.redevelopment_scores

    # Scoring helper methods
    def _score_zoning(self, data: Dict) -> float:
        # Score based on flexibility and agricultural designation.
        if not data: return 0.1
        score = 0.5
        if data.get('is_ag_zone'): score += 0.4
        if data.get('allows_redevelopment'): score += 0.4
        return min(1.0, score)

    def _score_current_use(self, data: Dict) -> float:
        # Score based on lower intensity use being easier to redevelop.
        # More detailed logic to be added
        return 0.5

    def _score_water(self, surface: Dict, ground: Dict) -> float:
        # Score based on water security.
        # More detailed logic to be added
        return 0.5

    def _score_water_rights(self, data: Dict) -> float:
        """
        Scores water rights based on priority and allocation.
        A higher score indicates more secure and abundant water rights.
        """
        # Placeholder - needs real logic based on harmonized data model
        # e.g., total_allocation, senior_rights_ratio
        return data.get('water_security_score', 0.5)

    def _score_infrastructure(self, improvements: Dict, power: Dict) -> float:
        # Score based on existing infrastructure quality.
        # More detailed logic to be added
        infra_score = improvements.get('modernization_score', 0) if improvements else 0
        power_score = power.get('grid_reliability_score', 0) if power else 0
        return (infra_score * 0.6 + power_score * 0.4)

    def _score_ownership(self, data: Dict) -> float:
        # Lower concentration might indicate easier acquisition.
        if not data: return 0.1
        concentration = data.get('ownership_concentration', 0.5) # Normalized 0-1
        return 1.0 - concentration
    
    def _score_mortgage_debt(self, data: Dict) -> float:
        # Higher debt may indicate financial distress and willingness to sell.
        if not data: return 0.1
        risk_level = data.get('financial_risk_level', 0.5) # Normalized 0-1
        return 1.0 - risk_level

    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the analysis results.
        
        Returns:
            Dictionary containing the analysis summary.
        """
        if not self.unified_data:
            return {'error': 'Analysis has not been run.'}

        scores = [s['composite_score'] for s in self.redevelopment_scores.values()]
        
        summary = {
            'bioregion': self.bioregion,
            'h3_resolution': self.resolution,
            'total_hexagons': len(self.target_hexagons),
            'modules_analyzed': list(self.modules.keys()),
            'analysis_timestamp': datetime.now().isoformat(),
            'redevelopment_potential': {
                'mean_score': round(np.mean(scores), 3) if scores else 0,
                'median_score': round(np.median(scores), 3) if scores else 0,
                'std_dev': round(np.std(scores), 3) if scores else 0,
                'high_potential_hexagons': len([s for s in scores if s > 0.75]),
                'low_potential_hexagons': len([s for s in scores if s < 0.25]),
            },
            'module_summaries': {}
        }

        for module_name in self.modules.keys():
            valid_hex_count = sum(1 for hex_data in self.unified_data.values() if hex_data.get(module_name))
            summary['module_summaries'][module_name] = {
                'processed_hexagons': valid_hex_count,
                'coverage': round(valid_hex_count / len(self.target_hexagons) * 100, 2) if self.target_hexagons else 0,
            }
        
        return summary
    
    def export_unified_data(self, output_path: str, export_format: str = 'geojson') -> None:
        """
        Export unified data and scores to a specified format.
        
        Args:
            output_path: Output file path.
            export_format: 'geojson', 'csv', or 'json'.
        """
        if not self.unified_data:
            raise ValueError("No unified data to export. Please run the analysis first.")
        
        # Combine unified data with redevelopment scores
        export_data = {}
        for h3_index, data in self.unified_data.items():
            export_data[h3_index] = data.copy()
            export_data[h3_index]['redevelopment_potential'] = self.redevelopment_scores.get(h3_index, {})

        if export_format == 'geojson':
            self._export_geojson(export_data, output_path)
        elif export_format == 'csv':
            self._export_csv(export_data, output_path)
        elif export_format == 'json':
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, cls=NumpyEncoder)
        else:
            logger.error(f"Unsupported export format: {export_format}")
            return
        logger.info(f"Successfully exported unified data to {output_path}")

    def _export_geojson(self, data_to_export: Dict, output_path: str):
        """Exports the unified dataset to a GeoJSON file."""
        features = []
        for hex_id, properties in data_to_export.items():
            # Get geometry for the hexagon
            boundary = h3.h3_to_geo_boundary(hex_id, geo_json=True)
            
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [boundary]
                },
                'properties': properties
            })
            
        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f, cls=NumpyEncoder)

    def _export_csv(self, data_to_export: Dict, output_path: str):
        """Exports the unified dataset to a CSV file."""
        # This will flatten the nested dictionary structure
        flat_data = []
        for hex_id, props in data_to_export.items():
            row = {'h3_index': hex_id}
            for key, value in props.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        row[f"{key}_{sub_key}"] = sub_value
                else:
                    row[key] = value
            flat_data.append(row)
        
        df = pd.DataFrame(flat_data)
        df.to_csv(output_path, index=False)

    def generate_interactive_dashboard(self, output_path: str) -> None:
        """
        Generate an interactive Folium dashboard with multiple data overlays.
        
        Args:
            output_path: Path to save the HTML dashboard file.
        """
        if not self.unified_data:
            logger.error("No unified data available to generate a dashboard.")
            return

        # Define a sensible default if no hexagons are available
        if not self.target_hexagons:
            map_center = [44.0, -120.5] # Default to center of Oregon
        else:
            # Calculate the centroid of the entire target region for the map center
            all_boundaries = [Polygon(h3.h3_to_geo_boundary(h)) for h in self.target_hexagons]
            gdf_all = gpd.GeoDataFrame({'geometry': all_boundaries}, crs="EPSG:4326")
            unified_geom = gdf_all.unary_union
            centroid = unified_geom.centroid
            map_center = [centroid.y, centroid.x]

        logger.info(f"Generating interactive dashboard centered at {map_center}...")
        m = folium.Map(location=map_center, zoom_start=7, tiles='CartoDB positron')

        # Add a title to the map
        title_html = f'''
            <h3 style="text-align: center; color: #333; padding: 10px; background-color: #f0f0f0; border-radius: 5px; font-family: 'Arial', sans-serif;">
                Cascadian Agricultural Land Redevelopment Potential Dashboard
            </h3>
        '''
        m.get_root().header.add_child(folium.Element(title_html))

        folium.TileLayer('Stamen Terrain', attr='Stamen').add_to(m)
        
        # --- Create Feature Groups for each layer ---
        groups = {
            'redevelopment': folium.FeatureGroup(name="Redevelopment Potential", show=True),
            'zoning': folium.FeatureGroup(name="Zoning", show=False),
            'current_use': folium.FeatureGroup(name="Current Use", show=False),
            'water': folium.FeatureGroup(name="Water Security", show=False),
            'ownership': folium.FeatureGroup(name="Ownership Concentration", show=False)
        }

        # --- Populate Layers ---
        for h3_index, hex_data in self.unified_data.items():
            boundary = hex_data.get('boundary')
            if not boundary: continue
            
            # Redevelopment Layer
            score_data = self.redevelopment_scores.get(h3_index, {})
            score = score_data.get('composite_score', 0)
            popup_html = f"<b>H3:</b> {h3_index}<br><b>Score:</b> {score:.3f}"
            folium.Polygon(
                locations=boundary,
                color=self._get_color_for_score(score),
                fill_color=self._get_color_for_score(score),
                weight=1, fill_opacity=0.6,
                popup=folium.Popup(popup_html),
                tooltip=f"Redevelopment Score: {score:.3f}"
            ).add_to(groups['redevelopment'])

            # Zoning Layer
            zoning_data = hex_data.get('zoning', {})
            if zoning_data:
                z_popup = f"<b>H3:</b> {h3_index}<br><b>Zone:</b> {zoning_data.get('zone_type', 'N/A')}"
                folium.Polygon(
                    locations=boundary, color="purple", weight=1, fill_opacity=0.5,
                    popup=z_popup, tooltip=f"Zone: {zoning_data.get('zone_type', 'N/A')}"
                ).add_to(groups['zoning'])
                
            # Current Use Layer
            use_data = hex_data.get('current_use', {})
            if use_data:
                u_popup = f"<b>H3:</b> {h3_index}<br><b>Use:</b> {use_data.get('primary_use', 'N/A')}"
                folium.Polygon(
                    locations=boundary, color="green", weight=1, fill_opacity=0.5,
                    popup=u_popup, tooltip=f"Use: {use_data.get('primary_use', 'N/A')}"
                ).add_to(groups['current_use'])

            # Water Layer
            water_score = score_data.get('factors', {}).get('water', 0)
            w_popup = f"<b>H3:</b> {h3_index}<br><b>Water Score:</b> {water_score:.3f}"
            folium.Polygon(
                locations=boundary, color=self._get_color_for_score(water_score, 'blue'), 
                fill_color=self._get_color_for_score(water_score, 'blue'),
                weight=1, fill_opacity=0.6,
                popup=w_popup, tooltip=f"Water Score: {water_score:.3f}"
            ).add_to(groups['water'])

            # Ownership Layer
            owner_score = score_data.get('factors', {}).get('ownership', 0)
            o_popup = f"<b>H3:</b> {h3_index}<br><b>Ownership Concentration:</b> {owner_score:.3f}"
            folium.Polygon(
                locations=boundary, color=self._get_color_for_score(owner_score, 'grey'), 
                fill_color=self._get_color_for_score(owner_score, 'grey'),
                weight=1, fill_opacity=0.6,
                popup=o_popup, tooltip=f"Ownership Score: {owner_score:.3f}"
            ).add_to(groups['ownership'])


        # --- Add layers to map ---
        for group in groups.values():
            group.add_to(m)

        # --- Add Heatmap ---
        # Prepare data for heatmap layer (lat, lon, weight)
        heat_data = [
            [
                self.unified_data[h]['centroid'][1], 
                self.unified_data[h]['centroid'][0], 
                self.redevelopment_scores.get(h, {}).get('composite_score', 0)
            ]
            for h in self.target_hexagons 
            if h in self.unified_data and 'centroid' in self.unified_data[h] and self.unified_data[h]['centroid']
        ]

        if heat_data:
            HeatMap(heat_data, name="Redevelopment Heatmap", show=False).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)
        
        try:
            m.save(output_path)
            logger.info(f"Successfully generated interactive dashboard at {output_path}")
        except Exception as e:
            logger.error(f"Failed to save interactive dashboard to {output_path}: {e}")

    def _get_color_for_score(self, score: float, theme: str = 'default') -> str:
        """Helper to get a color based on a score from 0 to 1."""
        if not isinstance(score, (float, int)):
            return '#808080' # Grey for invalid score

        if theme == 'blue': # For water
            if score > 0.85: return '#d73027'
            elif score > 0.7: return '#fc8d59'
            elif score > 0.55: return '#fee08b'
            elif score > 0.4: return '#d9ef8b'
            elif score > 0.25: return '#91cf60'
            else: return '#1a9850'
        elif theme == 'grey': # For ownership
            if score > 0.75: return '#252525'
            if score > 0.5: return '#636363'
            if score > 0.25: return '#969696'
            return '#cccccc'
        else: # Default: Green-Yellow-Red
            if score > 0.75: return '#2ca25f'
            if score > 0.5: return '#99d8c9'
            if score > 0.25: return '#fed976'
            return '#e31a1c' 