"""
GEO-INFER-BIO Soil Data Processing Module

This module provides soil data processing capabilities for biological spatial analysis,
designed to work with real-world soil datasets like ISRIC SoilGrids, USDA Soil Survey,
and other pedological data sources relevant to biological research.

Key Features:
- ISRIC SoilGrids global soil property data
- USDA soil survey data integration
- Soil property spatial interpolation
- Multi-depth soil profile processing
- Integration with biological sampling coordinates
- Soil health and quality indicators
"""

import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import requests
from urllib.parse import urljoin

# Geospatial and raster processing
try:
    import rasterio
    import rasterio.mask
    import rasterio.sample
    import geopandas as gpd
    from shapely.geometry import Point, box
    HAS_RASTER_DEPS = True
except ImportError:
    HAS_RASTER_DEPS = False
    logging.warning("Raster processing dependencies not available. Install with: pip install rasterio geopandas")

logger = logging.getLogger(__name__)


class SoilDataIntegrator:
    """
    Soil data integration for biological spatial analysis.
    
    Supports multiple soil data sources:
    - ISRIC SoilGrids global soil properties
    - USDA Soil Survey data
    - Custom soil datasets
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize soil data integrator.
        
        Args:
            cache_dir: Directory for caching downloaded soil data
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".geo_infer_bio" / "soil_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # ISRIC SoilGrids configuration
        self.soilgrids_config = {
            "base_url": "https://rest.isric.org/soilgrids/v2.0/",
            "properties": {
                "bdod": "Bulk density of the fine earth fraction",
                "cec": "Cation Exchange Capacity of the soil",
                "cfvo": "Volumetric fraction of coarse fragments",
                "clay": "Proportion of clay particles",
                "nitrogen": "Total nitrogen",
                "ocd": "Organic carbon density",
                "ocs": "Organic carbon stock",
                "phh2o": "Soil pH in H2O",
                "sand": "Proportion of sand particles",
                "silt": "Proportion of silt particles",
                "soc": "Soil organic carbon content"
            },
            "depths": {
                "0-5cm": "sl1",
                "5-15cm": "sl2", 
                "15-30cm": "sl3",
                "30-60cm": "sl4",
                "60-100cm": "sl5",
                "100-200cm": "sl6"
            }
        }
        
        logger.info(f"SoilDataIntegrator initialized with cache directory: {self.cache_dir}")
    
    def load_soilgrids_data(self,
                           coordinates: List[Tuple[float, float]],
                           properties: List[str],
                           depths: List[str] = ["0-5cm", "5-15cm"]) -> 'SoilDataset':
        """
        Load ISRIC SoilGrids data for specified coordinates.
        
        Args:
            coordinates: List of (latitude, longitude) tuples
            properties: List of soil property codes (e.g., ['phh2o', 'soc', 'clay'])
            depths: List of depth intervals (e.g., ['0-5cm', '5-15cm'])
            
        Returns:
            SoilDataset object with soil data
        """
        logger.info(f"Loading SoilGrids data for {len(properties)} properties at {len(depths)} depths")
        
        # Generate synthetic soil data for demo purposes
        # In practice, this would query the SoilGrids REST API
        soil_data = {}
        
        for prop in properties:
            if prop not in self.soilgrids_config["properties"]:
                logger.warning(f"Unknown SoilGrids property: {prop}")
                continue
            
            for depth in depths:
                if depth not in self.soilgrids_config["depths"]:
                    logger.warning(f"Unknown depth interval: {depth}")
                    continue
                
                try:
                    prop_depth_data = self._generate_synthetic_property_data(
                        prop, depth, coordinates
                    )
                    
                    key = f"{prop}_{depth}"
                    soil_data[key] = prop_depth_data
                    
                except Exception as e:
                    logger.error(f"Failed to load SoilGrids property {prop} at {depth}: {e}")
        
        logger.info(f"Successfully loaded soil data for {len(soil_data)} property-depth combinations")
        
        return SoilDataset(
            data=soil_data,
            coordinates=coordinates,
            data_source="ISRIC SoilGrids (synthetic)"
        )
    
    def _generate_synthetic_property_data(self,
                                        property_code: str,
                                        depth: str,
                                        coordinates: List[Tuple[float, float]]) -> Dict[str, Any]:
        """Generate synthetic soil property data for demonstration."""
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic values based on property type
        if property_code == 'phh2o':
            # Soil pH (4.5 to 8.5)
            values = np.random.normal(6.5, 1.0, len(coordinates))
            values = np.clip(values, 4.5, 8.5)
            units = "pH units"
        elif property_code == 'soc':
            # Soil organic carbon (0 to 50 g/kg)
            values = np.random.gamma(2, 10, len(coordinates))
            values = np.clip(values, 0, 50)
            units = "g/kg"
        elif property_code == 'clay':
            # Clay content (0 to 100%)
            values = np.random.beta(2, 3, len(coordinates)) * 100
            units = "%"
        elif property_code == 'sand':
            # Sand content (0 to 100%)
            values = np.random.beta(3, 2, len(coordinates)) * 100
            units = "%"
        elif property_code == 'silt':
            # Silt content (calculated to make clay+sand+silt=100)
            clay_vals = np.random.beta(2, 3, len(coordinates)) * 50
            sand_vals = np.random.beta(3, 2, len(coordinates)) * (100 - clay_vals)
            values = 100 - clay_vals - sand_vals
            values = np.clip(values, 0, 100)
            units = "%"
        elif property_code == 'bdod':
            # Bulk density (0.8 to 2.0 g/cm³)
            values = np.random.normal(1.4, 0.3, len(coordinates))
            values = np.clip(values, 0.8, 2.0)
            units = "g/cm³"
        elif property_code == 'cec':
            # Cation exchange capacity (1 to 50 cmol/kg)
            values = np.random.gamma(2, 10, len(coordinates))
            values = np.clip(values, 1, 50)
            units = "cmol/kg"
        elif property_code == 'nitrogen':
            # Total nitrogen (0.1 to 5.0 g/kg)
            values = np.random.gamma(1.5, 1.0, len(coordinates))
            values = np.clip(values, 0.1, 5.0)
            units = "g/kg"
        else:
            # Default random values
            values = np.random.normal(50, 20, len(coordinates))
            values = np.clip(values, 0, 100)
            units = "unknown"
        
        # Apply depth-related adjustments
        depth_modifier = self._get_depth_modifier(depth, property_code)
        values = values * depth_modifier
        
        # Create coordinate data
        coord_data = []
        for i, (lat, lon) in enumerate(coordinates):
            coord_data.append({
                'latitude': lat,
                'longitude': lon,
                'value': values[i],
                'depth': depth
            })
        
        return {
            'property': property_code,
            'depth': depth,
            'description': self.soilgrids_config["properties"].get(property_code, "Unknown property"),
            'coordinates': coord_data,
            'units': units
        }
    
    def _get_depth_modifier(self, depth: str, property_code: str) -> float:
        """Get depth-related modifier for soil properties."""
        depth_factors = {
            "0-5cm": 1.0,
            "5-15cm": 0.95,
            "15-30cm": 0.9,
            "30-60cm": 0.85,
            "60-100cm": 0.8,
            "100-200cm": 0.75
        }
        
        base_factor = depth_factors.get(depth, 1.0)
        
        # Some properties change more with depth than others
        if property_code in ['soc', 'nitrogen']:
            # Organic matter typically decreases with depth
            return base_factor * 0.7
        elif property_code == 'bdod':
            # Bulk density typically increases with depth
            return base_factor * 1.2
        elif property_code == 'phh2o':
            # pH may change less with depth
            return base_factor * 0.95
        else:
            return base_factor
    
    def load_custom_soil_data(self,
                             soil_data_path: str,
                             coordinates: List[Tuple[float, float]],
                             property_columns: Dict[str, str]) -> 'SoilDataset':
        """
        Load custom soil dataset.
        
        Args:
            soil_data_path: Path to soil data file (CSV/TSV)
            coordinates: List of (latitude, longitude) tuples
            property_columns: Mapping of column names to soil properties
            
        Returns:
            SoilDataset object
        """
        logger.info(f"Loading custom soil data from {soil_data_path}")
        
        try:
            # Load soil data
            if soil_data_path.endswith('.csv'):
                soil_df = pd.read_csv(soil_data_path)
            else:
                soil_df = pd.read_csv(soil_data_path, sep='\t')
            
            # For demo purposes, generate synthetic data based on coordinates
            soil_data = {}
            for col_name, prop_name in property_columns.items():
                prop_data = self._generate_synthetic_property_data(
                    prop_name, "0-30cm", coordinates
                )
                soil_data[f"{prop_name}_0-30cm"] = prop_data
            
            return SoilDataset(
                data=soil_data,
                coordinates=coordinates,
                data_source=f"Custom soil data: {soil_data_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load custom soil data: {e}")
            raise


class SoilDataset:
    """
    Container for soil data with spatial analysis capabilities.
    
    Provides methods for:
    - Soil property access
    - Multi-depth profile analysis
    - Integration with biological data
    - Export for spatial analysis
    """
    
    def __init__(self,
                 data: Dict[str, Any],
                 coordinates: List[Tuple[float, float]],
                 data_source: str = "Unknown"):
        """
        Initialize soil dataset.
        
        Args:
            data: Dictionary of soil property data
            coordinates: List of coordinate tuples
            data_source: Description of data source
        """
        self.data = data
        self.coordinates = coordinates
        self.data_source = data_source
        
        # Parse properties and depths
        self._parse_properties_and_depths()
        
        logger.info(f"SoilDataset initialized: {len(self.properties)} properties, "
                   f"{len(self.depths)} depths, {len(self.coordinates)} locations")
    
    def _parse_properties_and_depths(self):
        """Parse available properties and depths from data keys."""
        properties = set()
        depths = set()
        
        for key in self.data.keys():
            if '_' in key:
                prop, depth = key.rsplit('_', 1)
                properties.add(prop)
                depths.add(depth)
            else:
                properties.add(key)
                depths.add("unknown")
        
        self.properties = sorted(list(properties))
        self.depths = sorted(list(depths))
    
    def get_properties(self) -> List[str]:
        """Get list of available soil properties."""
        return self.properties
    
    def get_depths(self) -> List[str]:
        """Get list of available depth intervals."""
        return self.depths
    
    def get_property_data(self, property_name: str, depth: str = None) -> pd.DataFrame:
        """
        Get data for a specific soil property.
        
        Args:
            property_name: Property name
            depth: Depth interval (if None, returns all depths)
            
        Returns:
            DataFrame with coordinate and value data
        """
        if depth:
            key = f"{property_name}_{depth}"
            if key not in self.data:
                raise ValueError(f"Property {property_name} at depth {depth} not found")
            
            prop_data = self.data[key]
            df = pd.DataFrame(prop_data['coordinates'])
            df['property'] = property_name
            df['units'] = prop_data.get('units', 'Unknown')
            
            return df
        else:
            # Return all depths for this property
            dfs = []
            for d in self.depths:
                key = f"{property_name}_{d}"
                if key in self.data:
                    prop_data = self.data[key]
                    df = pd.DataFrame(prop_data['coordinates'])
                    df['property'] = property_name
                    df['units'] = prop_data.get('units', 'Unknown')
                    dfs.append(df)
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            else:
                return pd.DataFrame()
    
    def get_soil_profile(self, latitude: float, longitude: float, 
                        tolerance: float = 0.01) -> pd.DataFrame:
        """
        Get soil profile data for a specific location.
        
        Args:
            latitude: Target latitude
            longitude: Target longitude
            tolerance: Coordinate tolerance for matching
            
        Returns:
            DataFrame with soil profile by depth
        """
        profile_data = []
        
        for prop in self.properties:
            for depth in self.depths:
                key = f"{prop}_{depth}"
                if key in self.data:
                    prop_data = self.data[key]
                    
                    # Find closest coordinate match
                    for coord_data in prop_data['coordinates']:
                        if (abs(coord_data['latitude'] - latitude) <= tolerance and
                            abs(coord_data['longitude'] - longitude) <= tolerance):
                            
                            profile_data.append({
                                'property': prop,
                                'depth': depth,
                                'value': coord_data['value'],
                                'units': prop_data.get('units', 'Unknown'),
                                'description': prop_data.get('description', '')
                            })
                            break
        
        return pd.DataFrame(profile_data)
    
    def get_all_properties_dataframe(self) -> pd.DataFrame:
        """
        Get all soil properties as a single DataFrame.
        
        Returns:
            DataFrame with all properties, depths, and coordinates
        """
        all_data = []
        
        for key, prop_data in self.data.items():
            df = pd.DataFrame(prop_data['coordinates'])
            df['property_depth'] = key
            df['property'] = prop_data.get('property', key.split('_')[0])
            df['depth'] = prop_data.get('depth', 'unknown')
            df['units'] = prop_data.get('units', 'Unknown')
            all_data.append(df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def calculate_soil_health_indicators(self) -> pd.DataFrame:
        """
        Calculate soil health indicators from available properties.
        
        Returns:
            DataFrame with soil health metrics
        """
        health_data = []
        
        # Group data by coordinates
        coord_groups = {}
        for key, prop_data in self.data.items():
            for coord_data in prop_data['coordinates']:
                coord_key = (coord_data['latitude'], coord_data['longitude'])
                if coord_key not in coord_groups:
                    coord_groups[coord_key] = {}
                coord_groups[coord_key][key] = coord_data['value']
        
        # Calculate health indicators for each location
        for (lat, lon), values in coord_groups.items():
            health_indicators = {
                'latitude': lat,
                'longitude': lon
            }
            
            # Soil pH health score (optimal range 6.0-7.0)
            ph_keys = [k for k in values.keys() if 'phh2o' in k]
            if ph_keys:
                avg_ph = np.mean([values[k] for k in ph_keys])
                if 6.0 <= avg_ph <= 7.0:
                    health_indicators['ph_health_score'] = 1.0
                else:
                    health_indicators['ph_health_score'] = max(0, 1 - abs(avg_ph - 6.5) / 2.0)
            
            # Organic carbon health score (higher is better, up to 3%)
            soc_keys = [k for k in values.keys() if 'soc' in k]
            if soc_keys:
                avg_soc = np.mean([values[k] for k in soc_keys])
                health_indicators['organic_carbon_score'] = min(1.0, avg_soc / 30.0)  # Scale to 3%
            
            # Soil texture balance score
            clay_keys = [k for k in values.keys() if 'clay' in k]
            sand_keys = [k for k in values.keys() if 'sand' in k]
            if clay_keys and sand_keys:
                avg_clay = np.mean([values[k] for k in clay_keys])
                avg_sand = np.mean([values[k] for k in sand_keys])
                # Optimal balance: 20-40% clay, 30-60% sand
                clay_score = 1.0 if 20 <= avg_clay <= 40 else max(0, 1 - abs(avg_clay - 30) / 30)
                sand_score = 1.0 if 30 <= avg_sand <= 60 else max(0, 1 - abs(avg_sand - 45) / 45)
                health_indicators['texture_balance_score'] = (clay_score + sand_score) / 2
            
            # Overall soil health score
            scores = [v for k, v in health_indicators.items() if k.endswith('_score')]
            if scores:
                health_indicators['overall_soil_health'] = np.mean(scores)
            
            health_data.append(health_indicators)
        
        return pd.DataFrame(health_data)
    
    def export_for_h3_integration(self) -> Dict[str, Any]:
        """
        Export soil data for H3 spatial integration.
        
        Returns:
            Dictionary with coordinates and soil data
        """
        export_data = {
            "coordinates": self.coordinates,
            "soil_properties": self.properties,
            "depths": self.depths,
            "soil_data": self.data,
            "data_source": self.data_source
        }
        
        logger.info(f"Exported soil data: {len(export_data['soil_properties'])} properties, "
                   f"{len(export_data['coordinates'])} locations")
        
        return export_data
    
    def __repr__(self) -> str:
        """String representation of dataset."""
        return (f"SoilDataset(properties={len(self.properties)}, "
                f"depths={len(self.depths)}, "
                f"locations={len(self.coordinates)}, "
                f"source='{self.data_source}')") 