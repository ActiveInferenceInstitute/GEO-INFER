#!/usr/bin/env python3
"""
Unified H3 Backend for Cascadian Agricultural Land Analysis

This module provides a unified interface for integrating multiple data sources
through H3 spatial indexing, enabling cross-border analysis between California
and Oregon agricultural areas.
"""
import sys
from pathlib import Path
import logging

# --- Robust Path Setup ---
# This ensures modules can be imported across the GEO-INFER project.
try:
    # Assumes this file is in GEO-INFER-PLACE/locations/cascadia/
    current_dir = Path(__file__).resolve().parent
    locations_dir = current_dir.parent # a/b/c -> a/b
    project_root = locations_dir.parents[1] # a/b -> root

    # 1. Add GEO-INFER-SPACE/src for OSC utils
    space_src_path = project_root / 'GEO-INFER-SPACE' / 'src'
    if str(space_src_path) not in sys.path:
        sys.path.insert(0, str(space_src_path))
        print(f"INFO: unified_backend.py added {space_src_path} to sys.path")

    # 2. Add the 'locations' directory to allow absolute imports from 'cascadia'
    if str(locations_dir) not in sys.path:
        sys.path.insert(0, str(locations_dir))
        print(f"INFO: unified_backend.py added {locations_dir} to sys.path for absolute imports")

except Exception as e:
    print(f"CRITICAL: unified_backend.py path setup failed: {e}")
# --- End Path Setup ---


import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import folium
from folium.plugins import HeatMap, MarkerCluster

# Import our refactored H3 utility
from utils_h3 import geo_to_h3, h3_to_geo, h3_to_geo_boundary, polyfill, osc_h3_to_geojson

# Import all the specialized modules
# These are placeholders for the actual module implementations
from zoning import geo_infer_zoning
from current_use import geo_infer_current_use
from ownership import geo_infer_ownership
from mortgage_debt import geo_infer_mortgage_debt
from improvements import geo_infer_improvements
from surface_water import geo_infer_surface_water
from ground_water import geo_infer_ground_water
from power_source import geo_infer_power_source
from water_rights import geo_infer_water_rights

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy data types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return super(NumpyEncoder, self).default(obj)


class CascadianAgriculturalH3Backend:
    """
    Unified H3-indexed backend for comprehensive agricultural land analysis
    across the Cascadian bioregion (Northern California + Oregon).
    """
    
    def __init__(self, 
                 resolution: int = 8, 
                 bioregion: str = 'Cascadia',
                 active_modules: Optional[List[str]] = None,
                 target_counties: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the unified backend with H3 spatial indexing.
        
        Args:
            resolution: H3 resolution level (default: 8)
            bioregion: Bioregion identifier (default: 'Cascadia')
            active_modules: A list of module names to activate. If None, all are active.
            target_counties: A dict specifying counties to run, e.g., {'CA': ['all']}.
        """
        self.resolution = resolution
        self.bioregion = bioregion
        self.unified_data: Dict[str, Dict] = {}
        self.redevelopment_scores: Dict[str, Dict] = {}
        
        # This needs to be called before module initialization to define the regions
        self.target_hexagons_by_state, self.target_hexagons = self._define_target_region(target_counties)

        # Initialize all possible data modules
        all_modules = {
            'zoning': geo_infer_zoning.GeoInferZoning(self.resolution),
            'current_use': geo_infer_current_use.GeoInferCurrentUse(self.resolution),
            'ownership': geo_infer_ownership.GeoInferOwnership(self.resolution),
            'mortgage_debt': geo_infer_mortgage_debt.GeoInferMortgageDebt(self.resolution),
            'improvements': geo_infer_improvements.GeoInferImprovements(self.resolution),
            'surface_water': geo_infer_surface_water.GeoInferSurfaceWater(self.resolution),
            'ground_water': geo_infer_ground_water.GeoInferGroundWater(self.resolution),
            'power_source': geo_infer_power_source.GeoInferPowerSource(self.resolution),
            'water_rights': geo_infer_water_rights.GeoInferWaterRights(self.resolution)
        }
        
        # Filter to only the active modules
        if active_modules:
            self.modules = {name: mod for name, mod in all_modules.items() if name in active_modules}
        else:
            self.modules = all_modules # Default to all if not specified

        logger.info(f"CascadianAgriculturalH3Backend initialized for '{self.bioregion}' with {len(self.modules)} active modules at H3 resolution {self.resolution}")
        logger.info(f"Active modules: {list(self.modules.keys())}")
        logger.info(f"Defined {len(self.target_hexagons)} total target hexagons across {len(self.target_hexagons_by_state)} states.")

    def _define_target_region(self, target_counties: Optional[Dict[str, List[str]]] = None) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Define the target region using H3 hexagons, categorized by state and filtered by county.
        
        This method generates a grid of hexagons and uses their centroids
        to determine which state they fall into. If target_counties is provided,
        it will filter the hexagons to those within the specified counties.

        Args:
            target_counties: A dictionary specifying counties to run, e.g., 
                             {'CA': ['Lassen', 'Plumas'], 'OR': ['all']}.
                             If None, defaults to the entire bioregion.

        Returns:
            A tuple containing:
            - A dictionary of H3 hexagon identifiers, keyed by state ('CA', 'OR', 'WA').
            - A list of all unique H3 hexagon identifiers across all filtered areas.
        """
        # Load county boundaries for filtering
        # This is a simplification; a real implementation would use a proper GIS file.
        # For now, we'll rely on broad bounding boxes for "all".
        # A full implementation would load a shapefile of counties.
        county_geoms = self._get_county_geometries(target_counties)

        hexagons_by_state: Dict[str, set] = {'CA': set(), 'OR': set(), 'WA': set()}
        
        # If no specific counties are defined, use the whole bioregion bounds
        if not county_geoms:
            # Define approximate bounding boxes for the bioregions
            bounds = {
                'Cascadia': {'lat_min': 39, 'lat_max': 46, 'lon_min': -125, 'lon_max': -116},
                'Columbia': {'lat_min': 44, 'lat_max': 49, 'lon_min': -124, 'lon_max': -116}
            }
            region_bounds = bounds.get(self.bioregion, bounds['Cascadia'])
            region_polygon = Polygon.from_bounds(
                region_bounds['lon_min'], region_bounds['lat_min'],
                region_bounds['lon_max'], region_bounds['lat_max']
            )
            hexagons_by_state['CA'] = set(polyfill(region_polygon.__geo_interface__, self.resolution))
            hexagons_by_state['OR'] = hexagons_by_state['CA'] # Simplification
            hexagons_by_state['WA'] = hexagons_by_state['CA'] # Simplification
        else:
            for state, counties in county_geoms.items():
                for county_name, geom in counties.items():
                    logger.info(f"Generating hexagons for {county_name}, {state}...")
                    # Polyfill the county geometry
                    hexagons_in_county = set(polyfill(geom.__geo_interface__, self.resolution))
                    hexagons_by_state[state].update(hexagons_in_county)

        # Classify hexagons by state (this is a bit redundant if counties are used, but good for 'all')
        all_hexagons = sorted(list(set.union(*hexagons_by_state.values())))
        classified_hexagons = {'CA': set(), 'OR': set(), 'WA': set()}
        state_bounds = {
            'OR': {'lat_min': 42, 'lat_max': 46.5},
            'CA': {'lat_min': 32, 'lat_max': 42},
        }
        for h3_index in all_hexagons:
            lat, lon = h3_to_geo(h3_index)
            if state_bounds['OR']['lat_min'] <= lat < state_bounds['OR']['lat_max']:
                classified_hexagons['OR'].add(h3_index)
            elif lat < state_bounds['CA']['lat_max']:
                classified_hexagons['CA'].add(h3_index)
            else:
                classified_hexagons['WA'].add(h3_index)

        # Final filtering based on the keys in the target_counties dict
        if target_counties:
            final_hex_sets = [classified_hexagons.get(state, set()) for state in target_counties.keys()]
            final_all_hexagons = sorted(list(set.union(*final_hex_sets)))
            final_hex_by_state = {k: sorted(list(v)) for k, v in classified_hexagons.items() if k in target_counties and v}
        else:
            final_all_hexagons = all_hexagons
            final_hex_by_state = {k: sorted(list(v)) for k, v in classified_hexagons.items() if v}
            
        if not final_all_hexagons:
            logger.error(f"Failed to generate any H3 hexagons for bioregion '{self.bioregion}' with filters {target_counties}")
            return {}, []
            
        return final_hex_by_state, final_all_hexagons

    def _get_county_geometries(self, target_counties: Optional[Dict[str, List[str]]]) -> Dict[str, Dict[str, Polygon]]:
        """
        Loads county geometries for the specified states and counties.
        This is a placeholder for a more robust implementation that would read from a
        GIS file (e.g., a shapefile or GeoJSON of US counties).
        """
        if not target_counties:
            return {}

        # Placeholder: In a real scenario, you'd load a county shapefile here.
        # e.g., counties_gdf = gpd.read_file('path/to/us_counties.shp')
        # And then filter it:
        # counties_gdf[counties_gdf['STATE_ABBR'].isin(target_counties.keys())]
        
        logger.warning("County geometry loading is using placeholder bounding boxes. For accurate analysis, replace with a real county shapefile.")

        # Example placeholder geometries (broad bounding boxes)
        geometries = {
            'CA': {
                'Lassen': Polygon.from_bounds(-121.3, 40.2, -120.0, 41.3),
                'Plumas': Polygon.from_bounds(-121.5, 39.7, -120.2, 40.5),
                'all': Polygon.from_bounds(-124.5, 32.5, -114.0, 42.0)
            },
            'OR': {
                'all': Polygon.from_bounds(-124.6, 42.0, -116.4, 46.3)
            },
            'WA': {
                'all': Polygon.from_bounds(-124.8, 45.5, -116.9, 49.0)
            }
        }
        
        output_geoms = {}
        for state, counties in target_counties.items():
            if state in geometries:
                output_geoms[state] = {}
                for county in counties:
                    if county in geometries[state]:
                        output_geoms[state][county] = geometries[state][county]
        
        return output_geoms

    def run_comprehensive_analysis(self) -> Dict[str, Dict]:
        """
        Execute all active analysis modules and create a unified H3-indexed dataset.
        
        Returns:
            Comprehensive H3-indexed agricultural data.
        """
        module_results = {}
        
        # Determine which modules to run based on the main script's arguments
        # This part is tricky because the backend doesn't have direct access to args.
        # For now, we assume all modules are run, but a more robust implementation
        # might pass the module list during initialization.
        
        # Define which modules are state-specific
        # This could be moved to a config file for more flexibility
        state_specific_modules = {
            'zoning': ['CA', 'OR', 'WA'],
            'ownership': ['CA'],
            'water_rights': ['CA', 'OR', 'WA']
        }

        for module_name, module_instance in self.modules.items():
            logger.info(f"Processing '{module_name}' module...")

            # Determine the correct set of hexagons for this module
            target_hexs = self.target_hexagons # Default to all
            if module_name in state_specific_modules:
                # If a module is state-specific, combine hexagons from its supported states
                hex_sets = [set(self.target_hexagons_by_state.get(state, [])) for state in state_specific_modules[module_name]]
                target_hexs = sorted(list(set.union(*hex_sets)))
                logger.info(f"Module '{module_name}' is state-specific. Using {len(target_hexs)} hexagons from states: {state_specific_modules[module_name]}")

            if not target_hexs:
                logger.warning(f"No target hexagons for module '{module_name}'. Skipping.")
                module_results[module_name] = {}
                continue

            try:
                # Standardized call to the 'run_analysis' method for all modules
                result = module_instance.run_analysis(target_hexs)
                
                module_results[module_name] = result
                # Log a more informative message
                if result:
                    logger.info(f"'{module_name}' module processed {len(result)} hexagons successfully.")
                else:
                    logger.warning(f"'{module_name}' module did not return any data.")

            except AttributeError as e:
                logger.error(f"'{module_name}' module is missing the required 'run_analysis' method. {e}", exc_info=False)
                module_results[module_name] = {}
            except Exception as e:
                logger.error(f"Error processing '{module_name}' module: {e}", exc_info=True)
                module_results[module_name] = {}
        
        self._aggregate_module_results(module_results)
        self.calculate_agricultural_redevelopment_potential()
        
        return self.unified_data

    def _aggregate_module_results(self, results: Dict[str, Dict]):
        """Aggregate results from all modules into the unified_data dictionary."""
        logger.info("Aggregating results from all modules...")
        
        for hexagon in self.target_hexagons:
            hex_data = {'hex_id': hexagon}
            
            # Add geometry and metadata
            try:
                hex_data['centroid'] = h3_to_geo(hexagon)
                hex_data['boundary'] = h3_to_geo_boundary(hexagon)
            except Exception as e:
                logger.warning(f"Could not process geometry for {hexagon}: {e}")
                hex_data['centroid'] = None
                hex_data['boundary'] = None

            # Add module data
            for module_name, module_data in results.items():
                hex_data[module_name] = module_data.get(hexagon, {})
            
            self.unified_data[hexagon] = hex_data
            
        logger.info(f"Successfully aggregated data for {len(self.unified_data)} hexagons.")

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
        return data.get('agricultural_intensity', 0.5) * -1 + 1 if data else 0.5

    def _score_water(self, surface: Dict, ground: Dict) -> float:
        # Score based on water security.
        # More detailed logic to be added
        has_surface = surface.get('has_surface_water', False)
        has_ground = ground.get('has_ground_water', False)
        return float(has_surface or has_ground)

    def _score_water_rights(self, data: Dict) -> float:
        """Score based on the presence and status of water rights."""
        if not data:
            return 0.2  # Neutral score if no data
        
        # Higher score for more secure water rights
        score = 0.0
        if data.get('number_of_active_rights', 0) > 0:
            score = 0.8
        elif data.get('number_of_rights', 0) > 0:
            score = 0.4
            
        # Penalize if data is mocked
        if data.get('is_mock_data', False):
            score *= 0.5
            
        return score

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
        return risk_level

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

        if export_format.lower() == 'geojson':
            self._export_geojson(export_data, output_path)
        elif export_format.lower() == 'csv':
            self._export_csv(export_data, output_path)
        elif export_format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(export_data, f, cls=NumpyEncoder, indent=2)
            logger.info(f"Successfully exported data to JSON: {output_path}")
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

    def _export_geojson(self, data_to_export: Dict, output_path: str):
        """Export data to GeoJSON format."""
        features = []
        for h3_index, props in data_to_export.items():
            boundary_coords = props.get('boundary')
            if not boundary_coords:
                continue
            
            # GeoJSON requires closing the loop
            polygon_coords = list(boundary_coords)
            if polygon_coords[0] != polygon_coords[-1]:
                polygon_coords.append(polygon_coords[0])

            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [polygon_coords]
                },
                'properties': {k: v for k, v in props.items() if k not in ['boundary']}
            })
            
        feature_collection = {'type': 'FeatureCollection', 'features': features}
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f, cls=NumpyEncoder)
        logger.info(f"Successfully exported data to GeoJSON: {output_path}")

    def _export_csv(self, data_to_export: Dict, output_path: str):
        """Export data to CSV format."""
        flat_data = []
        for h3_index, props in data_to_export.items():
            row = {'h3_index': h3_index}
            row['lat'], row['lng'] = props.get('centroid', (None, None))
            
            # Flatten all nested properties
            for key, value in props.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, dict): # Handle one more level of nesting
                             for ssub_key, ssub_value in sub_value.items():
                                row[f"{key}_{sub_key}_{ssub_key}"] = ssub_value
                        else:
                            row[f"{key}_{sub_key}"] = sub_value
                else:
                    row[key] = value
            flat_data.append(row)

        df = pd.DataFrame(flat_data)
        # Drop complex geometry columns for CSV
        df = df.drop(columns=['boundary'], errors='ignore')
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully exported data to CSV: {output_path}")

    def generate_interactive_dashboard(self, output_path: str) -> None:
        """
        Generate an interactive Folium dashboard with multiple data overlays.
        
        Args:
            output_path: Path to save the HTML dashboard file.
        """
        if not self.unified_data:
            logger.error("No unified data available to generate a dashboard.")
            return

        # Center map on the bioregion
        centroids = [d['centroid'] for d in self.unified_data.values() if d.get('centroid')]
        if not centroids:
            map_center = [42.5, -120.0] # Fallback for Cascadia
        else:
            map_center = np.mean(centroids, axis=0).tolist()
            
        m = folium.Map(location=map_center, zoom_start=7, tiles='CartoDB positron')
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
        heat_data = [
            (d['centroid'][0], d['centroid'][1], self.redevelopment_scores.get(h3_index, {}).get('composite_score', 0))
            for h3_index, d in self.unified_data.items() if d.get('centroid')
        ]
        HeatMap(heat_data, name="Redevelopment Heatmap", show=False).add_to(m)

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
            if score > 0.75: return '#2171b5'
            if score > 0.5: return '#6baed6'
            if score > 0.25: return '#bdd7e7'
            return '#eff3ff'
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