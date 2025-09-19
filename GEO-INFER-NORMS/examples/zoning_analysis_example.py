"""
Zoning Analysis Example for GEO-INFER-NORMS

This example demonstrates how to use the GEO-INFER-NORMS module to analyze zoning
regulations, evaluate zoning changes, and visualize land use patterns.

The example includes:
1. Creating and analyzing zoning districts and codes
2. Evaluating potential zoning changes and their impacts
3. Classifying land use patterns
4. Visualizing zoning and land use data
5. Time-series analysis of zoning changes
6. Sustainability and environmental impact assessment
7. Report generation
"""

import os
import sys
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import json
import numpy as np
import networkx as nx
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry import mapping
import textwrap
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional, Any
from pathlib import Path
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import warnings
import colorsys
import random

# Try to import optional packages
try:
    import contextily as cx
    HAS_CONTEXTILY = True
except ImportError:
    HAS_CONTEXTILY = False
    print("Note: contextily package not found. Basemaps will not be available.")

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Note: seaborn package not found. Using matplotlib for visualizations.")

try:
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Note: scikit-learn package not found. Advanced clustering methods will not be available.")

try:
    import folium
    from folium.plugins import MarkerCluster, HeatMap
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("Note: folium package not found. Interactive web maps will not be available.")

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*The input coordinates to Voronoi.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*Geometry is in a geographic CRS.*")

# Import GEO-INFER-NORMS classes
from geo_infer_norms.core.zoning_analysis import ZoningAnalyzer, LandUseClassifier
from geo_infer_norms.models.zoning import ZoningCode, ZoningDistrict, LandUseType
from geo_infer_norms.models.legal_entity import LegalEntity

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

# Utility functions
def generate_color_palette(num_colors, base_color=None, mode='pastel'):
    """Generate a visually pleasing color palette with specified number of colors."""
    if base_color is None:
        base_hue = random.random()
    else:
        # Convert hex color to HSV
        if base_color.startswith('#'):
            r = int(base_color[1:3], 16) / 255.0
            g = int(base_color[3:5], 16) / 255.0
            b = int(base_color[5:7], 16) / 255.0
            base_hue, _, _ = colorsys.rgb_to_hsv(r, g, b)
        else:
            base_hue = random.random()
    
    colors = []
    for i in range(num_colors):
        hue = (base_hue + i / num_colors) % 1.0
        
        if mode == 'pastel':
            saturation = 0.4 + 0.2 * random.random()
            value = 0.8 + 0.2 * random.random()
        elif mode == 'bright':
            saturation = 0.7 + 0.3 * random.random()
            value = 0.9
        elif mode == 'dark':
            saturation = 0.6 + 0.2 * random.random()
            value = 0.4 + 0.2 * random.random()
        else:  # default
            saturation = 0.6
            value = 0.8
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
        colors.append(hex_color)
    
    return colors

def create_custom_colormap(categories, color_mode='pastel'):
    """Create a custom colormap for plotting categories."""
    colors = generate_color_palette(len(categories), mode=color_mode)
    return {category: color for category, color in zip(categories, colors)}

def get_current_timestamp():
    """Get a formatted timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_dict_for_display(data, indent=0):
    """Format a dictionary for display in console with proper indentation."""
    output = []
    for key, value in data.items():
        if isinstance(value, dict):
            output.append(" " * indent + f"{key}:")
            output.append(format_dict_for_display(value, indent + 2))
        elif isinstance(value, list):
            output.append(" " * indent + f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    output.append(format_dict_for_display(item, indent + 2))
                else:
                    output.append(" " * (indent + 2) + f"{item}")
        else:
            # Format floating point numbers nicely
            if isinstance(value, float):
                value = f"{value:.2f}"
            output.append(" " * indent + f"{key}: {value}")
    return "\n".join(output)

def save_plot(fig, filename, dpi=300, transparent=False):
    """Save a plot with standardized settings."""
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, bbox_inches='tight', dpi=dpi, transparent=transparent)
    print(f"Saved visualization to {filepath}")
    return filepath

def calculate_area(geometry, to_unit='hectares'):
    """Calculate area in desired units."""
    area_m2 = geometry.area
    
    if to_unit == 'hectares':
        return area_m2 / 10000
    elif to_unit == 'km2':
        return area_m2 / 1000000
    elif to_unit == 'sqmi':
        return area_m2 / 2589988.11
    elif to_unit == 'acres':
        return area_m2 / 4046.86
    else:
        return area_m2  # default is square meters

def wrap_labels(ax, width=10):
    """Wrap long axis labels."""
    for label in ax.get_xticklabels():
        text = label.get_text()
        if len(text) > width:
            wrapped_text = textwrap.fill(text, width=width)
            label.set_text(wrapped_text)
    
    for label in ax.get_yticklabels():
        text = label.get_text()
        if len(text) > width:
            wrapped_text = textwrap.fill(text, width=width)
            label.set_text(wrapped_text)

# Note: This example uses self-contained classes and does not rely on external imports
# to avoid package structure issues.

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

# Define the required model classes
class ZoningCode:
    """A class representing a zoning code in a jurisdiction."""
    
    def __init__(self, code, name, description, category, jurisdiction_id, allowed_uses=None,
                 max_height=None, min_lot_size=None, max_floor_area_ratio=None, 
                 max_density=None, setbacks=None, environmental_requirements=None):
        self.code = code
        self.name = name
        self.description = description
        self.category = category
        self.jurisdiction_id = jurisdiction_id
        self.allowed_uses = allowed_uses or []
        self.max_height = max_height  # in meters
        self.min_lot_size = min_lot_size  # in square meters
        self.max_floor_area_ratio = max_floor_area_ratio  # ratio
        self.max_density = max_density  # units per hectare
        self.setbacks = setbacks or {}  # dict with front, rear, side setbacks
        self.environmental_requirements = environmental_requirements or {}  # eco-requirements
        self.history = []  # track changes over time
        
    def add_historical_record(self, date, change_type, description, previous_values=None):
        """Add a historical record of changes to this zoning code."""
        self.history.append({
            'date': date,
            'change_type': change_type,
            'description': description,
            'previous_values': previous_values or {}
        })
        
    def to_dict(self):
        """Convert the zoning code to a dictionary."""
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'jurisdiction_id': self.jurisdiction_id,
            'allowed_uses': self.allowed_uses,
            'max_height': self.max_height,
            'min_lot_size': self.min_lot_size,
            'max_floor_area_ratio': self.max_floor_area_ratio,
            'max_density': self.max_density,
            'setbacks': self.setbacks,
            'environmental_requirements': self.environmental_requirements
        }
    
    def allows_use(self, use_type):
        """Check if this zoning code allows a specific use."""
        return use_type in self.allowed_uses
    
    def get_development_capacity(self, area):
        """Calculate the potential development capacity based on this zoning code."""
        if not self.max_density:
            return None
        
        # Calculate hectares from square meters
        hectares = area / 10000
        return hectares * self.max_density
    
    @property
    def is_residential(self):
        return self.category == "residential"
    
    @property
    def is_commercial(self):
        return self.category == "commercial"
    
    @property
    def is_industrial(self):
        return self.category == "industrial"
    
    @property
    def is_mixed_use(self):
        return self.category == "mixed_use"


class ZoningDistrict:
    """A class representing a geographic area with specific zoning regulations."""
    
    def __init__(self, id, name, zoning_code, jurisdiction_id, geometry=None, 
                 date_established=None, population=None, employment=None,
                 overlay_codes=None, environmental_features=None):
        self.id = id
        self.name = name
        self.zoning_code = zoning_code
        self.jurisdiction_id = jurisdiction_id
        self.geometry = geometry
        self.date_established = date_established or datetime.now().date()
        self.population = population
        self.employment = employment
        self.overlay_codes = overlay_codes or []
        self.environmental_features = environmental_features or {}
        self.history = []  # track zoning changes over time
        self.properties = []  # associated properties
        
    def add_historical_record(self, date, previous_code, change_description, ordinance_id=None):
        """Add a historical record of zoning changes."""
        self.history.append({
            'date': date,
            'previous_code': previous_code,
            'current_code': self.zoning_code,
            'description': change_description,
            'ordinance_id': ordinance_id
        })
        
    def add_property(self, property_id, address, land_use, area, value):
        """Add a property to this district."""
        self.properties.append({
            'id': property_id,
            'address': address,
            'land_use': land_use,
            'area': area,
            'value': value
        })
    
    @property
    def area(self):
        """Get the area of this district in square meters."""
        return self.geometry.area if self.geometry else 0
    
    @property
    def area_hectares(self):
        """Get the area of this district in hectares."""
        return self.area / 10000
    
    @property
    def area_km2(self):
        """Get the area of this district in square kilometers."""
        return self.area / 1000000
    
    @property
    def population_density(self):
        """Calculate population density (people per square km)."""
        if self.population and self.area > 0:
            return self.population / self.area_km2
        return 0
    
    @property
    def employment_density(self):
        """Calculate employment density (jobs per square km)."""
        if self.employment and self.area > 0:
            return self.employment / self.area_km2
        return 0
    
    def to_dict(self):
        """Convert the district to a dictionary."""
        result = {
            'id': self.id,
            'name': self.name,
            'zoning_code': self.zoning_code,
            'jurisdiction_id': self.jurisdiction_id,
            'date_established': str(self.date_established),
            'area_hectares': self.area_hectares,
            'population': self.population,
            'employment': self.employment,
            'overlay_codes': self.overlay_codes,
            'environmental_features': self.environmental_features,
            'property_count': len(self.properties)
        }
        
        # Only add these if they're not None to avoid json serialization errors
        if self.geometry:
            result['centroid'] = [self.geometry.centroid.x, self.geometry.centroid.y]
            
        return result


class LandUseType:
    """A class representing a type of land use."""
    
    def __init__(self, id, name, description, category, 
                 impervious_surface_ratio=None, trip_generation_rate=None,
                 environmental_impact_score=None, resource_usage=None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.impervious_surface_ratio = impervious_surface_ratio  # 0-1
        self.trip_generation_rate = trip_generation_rate  # trips per day per hectare
        self.environmental_impact_score = environmental_impact_score  # 0-100
        self.resource_usage = resource_usage or {}  # water, energy usage
        
    def to_dict(self):
        """Convert the land use type to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'impervious_surface_ratio': self.impervious_surface_ratio,
            'trip_generation_rate': self.trip_generation_rate,
            'environmental_impact_score': self.environmental_impact_score,
            'resource_usage': self.resource_usage
        }
    
    @property
    def sustainability_rating(self):
        """Get a sustainability rating based on environmental impact and resource usage."""
        if self.environmental_impact_score is None:
            return None
        
        # Invert scale so higher is better (0-100)
        return 100 - self.environmental_impact_score


class Parcel:
    """A class representing a land parcel."""
    
    def __init__(self, id, address, geometry, land_use, zoning_district_id,
                 area=None, building_footprint=None, building_height=None,
                 year_built=None, assessed_value=None, owner=None):
        self.id = id
        self.address = address
        self.geometry = geometry
        self.land_use = land_use
        self.zoning_district_id = zoning_district_id
        self.area = area or (geometry.area if geometry else 0)
        self.building_footprint = building_footprint
        self.building_height = building_height
        self.year_built = year_built
        self.assessed_value = assessed_value
        self.owner = owner
        
    @property
    def building_area(self):
        """Calculate total building area."""
        if self.building_footprint and self.building_height:
            # Approximate number of floors
            floors = max(1, int(self.building_height / 3))  # assuming 3m per floor
            return self.building_footprint * floors
        return None
    
    @property
    def floor_area_ratio(self):
        """Calculate floor area ratio."""
        if self.building_area and self.area:
            return self.building_area / self.area
        return None
    
    @property
    def building_coverage(self):
        """Calculate building coverage ratio."""
        if self.building_footprint and self.area:
            return self.building_footprint / self.area
        return None
    
    def to_dict(self):
        """Convert the parcel to a dictionary."""
        result = {
            'id': self.id,
            'address': self.address,
            'land_use': self.land_use,
            'zoning_district_id': self.zoning_district_id,
            'area': self.area,
            'building_footprint': self.building_footprint,
            'building_height': self.building_height,
            'year_built': self.year_built,
            'assessed_value': self.assessed_value,
            'owner': self.owner,
            'building_area': self.building_area,
            'floor_area_ratio': self.floor_area_ratio,
            'building_coverage': self.building_coverage
        }
        
        # Only add these if geometry is not None
        if self.geometry:
            result['centroid'] = [self.geometry.centroid.x, self.geometry.centroid.y]
            
        return result


class EnvironmentalAssessment:
    """A class for environmental impact assessment of land use and zoning."""
    
    def __init__(self, land_use_types=None):
        self.land_use_types = land_use_types or {}
        
        # Environmental impact factors by land use category
        self.impact_factors = {
            'residential': {
                'water_usage': 150,  # liters per person per day
                'energy_usage': 10,  # kWh per square meter per year
                'co2_emissions': 5,  # tonnes per hectare per year
                'imperviousness': 0.5  # percentage of impervious surface
            },
            'commercial': {
                'water_usage': 250,
                'energy_usage': 25,
                'co2_emissions': 15,
                'imperviousness': 0.8
            },
            'industrial': {
                'water_usage': 500,
                'energy_usage': 40,
                'co2_emissions': 25,
                'imperviousness': 0.9
            },
            'agricultural': {
                'water_usage': 2000,
                'energy_usage': 5,
                'co2_emissions': 2,
                'imperviousness': 0.1
            },
            'recreational': {
                'water_usage': 300,
                'energy_usage': 3,
                'co2_emissions': 1,
                'imperviousness': 0.3
            },
            'institutional': {
                'water_usage': 200,
                'energy_usage': 15,
                'co2_emissions': 8,
                'imperviousness': 0.7
            },
            'mixed_use': {
                'water_usage': 200,
                'energy_usage': 18,
                'co2_emissions': 10,
                'imperviousness': 0.6
            }
        }
    
    def calculate_environmental_impact(self, districts_gdf, population=None):
        """Calculate environmental impact of zoning districts."""
        if districts_gdf.empty:
            return {}
        
        results = {}
        total_area = districts_gdf.geometry.area.sum()
        
        # Calculate water usage
        water_usage = 0
        energy_usage = 0
        co2_emissions = 0
        imperviousness = 0
        
        for _, district in districts_gdf.iterrows():
            category = district.get('category', 'mixed_use')  # Default if not found
            area_hectares = district.geometry.area / 10000  # Convert to hectares
            
            # Get impact factors for this category
            factors = self.impact_factors.get(category, self.impact_factors['mixed_use'])
            
            # Calculate impacts
            district_water = factors['water_usage'] * area_hectares
            district_energy = factors['energy_usage'] * area_hectares
            district_co2 = factors['co2_emissions'] * area_hectares
            district_imperv = factors['imperviousness'] * district.geometry.area
            
            water_usage += district_water
            energy_usage += district_energy
            co2_emissions += district_co2
            imperviousness += district_imperv
        
        # Calculate overall impervious percentage
        if total_area > 0:
            imperviousness_percentage = (imperviousness / total_area) * 100
        else:
            imperviousness_percentage = 0
        
        results['total_water_usage'] = water_usage  # liters per day
        results['total_energy_usage'] = energy_usage  # kWh per year
        results['total_co2_emissions'] = co2_emissions  # tonnes per year
        results['imperviousness_percentage'] = imperviousness_percentage
        
        # Calculate runoff potential
        results['runoff_potential'] = self._calculate_runoff(imperviousness_percentage)
        
        # Urban heat island effect (simple model based on imperviousness)
        results['heat_island_effect'] = self._calculate_heat_island(imperviousness_percentage)
        
        return results
    
    def _calculate_runoff(self, imperviousness):
        """Calculate runoff potential based on imperviousness."""
        # Simple linear model: higher imperviousness = higher runoff
        # Returns a value between 0-100
        return min(100, imperviousness * 1.2)
    
    def _calculate_heat_island(self, imperviousness):
        """Calculate urban heat island effect based on imperviousness."""
        # Simple model: higher imperviousness = higher UHI effect
        # Returns temperature increase in degrees C
        return imperviousness / 20  # 100% impervious = 5C increase

# Define the ZoningAnalyzer class
class ZoningAnalyzer:
    """
    A class for analyzing zoning regulations and their spatial implications.
    """
    
    def __init__(self, zoning_districts=None, zoning_codes=None, parcels=None):
        self.zoning_districts = zoning_districts or []
        self.zoning_codes = zoning_codes or []
        self.parcels = parcels or []
        self._district_index = {d.id: d for d in self.zoning_districts}
        self._code_index = {c.code: c for c in self.zoning_codes}
        self._parcel_index = {p.id: p for p in self.parcels}
        
        # Create compatibility matrix between zoning types
        self._compatibility_matrix = self._build_compatibility_matrix()
        
        # Track historical zoning changes
        self.historical_changes = []
        
        # Environmental assessment
        self.environmental_assessment = EnvironmentalAssessment()
    
    def _build_compatibility_matrix(self):
        """Build a compatibility matrix between zoning codes."""
        matrix = {}
        
        for code1 in self.zoning_codes:
            matrix[code1.code] = {}
            for code2 in self.zoning_codes:
                # Default compatibility is 0.5
                compatibility = 0.5
                
                # Same code is fully compatible
                if code1.code == code2.code:
                    compatibility = 1.0
                # Similar categories are more compatible
                elif code1.category == code2.category:
                    compatibility = 0.8
                # Residential and industrial tend to be incompatible
                elif (code1.category == "residential" and code2.category == "industrial") or \
                     (code1.category == "industrial" and code2.category == "residential"):
                    compatibility = 0.1
                # Commercial can be somewhat compatible with residential
                elif (code1.category == "residential" and code2.category == "commercial") or \
                     (code1.category == "commercial" and code2.category == "residential"):
                    compatibility = 0.6
                # Commercial and industrial compatibility
                elif (code1.category == "commercial" and code2.category == "industrial") or \
                     (code1.category == "industrial" and code2.category == "commercial"):
                    compatibility = 0.4
                # Mixed use is compatible with both residential and commercial
                elif code1.category == "mixed_use" or code2.category == "mixed_use":
                    if (code1.category == "residential" or code2.category == "residential" or
                        code1.category == "commercial" or code2.category == "commercial"):
                        compatibility = 0.7
                # Agricultural zoning compatibility
                elif code1.category == "agricultural" or code2.category == "agricultural":
                    if (code1.category == "industrial" or code2.category == "industrial"):
                        compatibility = 0.2
                    elif (code1.category == "residential" or code2.category == "residential"):
                        compatibility = 0.5
                    elif (code1.category == "recreational" or code2.category == "recreational"):
                        compatibility = 0.8
                # Recreational zoning compatibility
                elif code1.category == "recreational" or code2.category == "recreational":
                    if (code1.category == "residential" or code2.category == "residential"):
                        compatibility = 0.8
                    elif (code1.category == "industrial" or code2.category == "industrial"):
                        compatibility = 0.3
                
                matrix[code1.code][code2.code] = compatibility
        
        return matrix
    
    def get_district_by_id(self, district_id):
        """Get a district by ID."""
        return self._district_index.get(district_id)
    
    def get_code_by_id(self, code_id):
        """Get a zoning code by ID."""
        return self._code_index.get(code_id)
    
    def get_parcel_by_id(self, parcel_id):
        """Get a parcel by ID."""
        return self._parcel_index.get(parcel_id)
    
    def get_parcels_in_district(self, district_id):
        """Get all parcels in a specific district."""
        return [p for p in self.parcels if p.zoning_district_id == district_id]
    
    def calculate_compatibility(self, code1, code2):
        """Calculate compatibility between two zoning codes."""
        if code1 not in self._compatibility_matrix or code2 not in self._compatibility_matrix:
            return 0.5  # Default medium compatibility
        
        return self._compatibility_matrix[code1][code2]
    
    def add_district(self, district):
        """Add a zoning district to the analyzer."""
        self.zoning_districts.append(district)
        self._district_index[district.id] = district
    
    def add_code(self, code):
        """Add a zoning code to the analyzer."""
        self.zoning_codes.append(code)
        self._code_index[code.code] = code
        # Rebuild compatibility matrix when adding a new code
        self._compatibility_matrix = self._build_compatibility_matrix()
    
    def add_parcel(self, parcel):
        """Add a parcel to the analyzer."""
        self.parcels.append(parcel)
        self._parcel_index[parcel.id] = parcel
    
    def change_district_zoning(self, district_id, new_code, change_date=None, description=None, ordinance_id=None):
        """Change the zoning code for a district and record the history."""
        district = self.get_district_by_id(district_id)
        if not district:
            return {
                "status": "error", 
                "message": f"District with ID {district_id} not found"
            }
        
        if new_code not in self._code_index:
            return {
                "status": "error", 
                "message": f"Zoning code {new_code} not found"
            }
        
        # Record the change
        date = change_date or datetime.now().date()
        previous_code = district.zoning_code
        
        # Add to district history
        district.add_historical_record(
            date=date,
            previous_code=previous_code,
            change_description=description or f"Changed from {previous_code} to {new_code}",
            ordinance_id=ordinance_id
        )
        
        # Add to analyzer history
        self.historical_changes.append({
            'date': date,
            'district_id': district_id,
            'district_name': district.name,
            'previous_code': previous_code,
            'new_code': new_code,
            'description': description,
            'ordinance_id': ordinance_id
        })
        
        # Update the district's zoning code
        district.zoning_code = new_code
        
        return {
            "status": "success",
            "message": f"Zoning for district '{district.name}' changed from {previous_code} to {new_code}",
            "district_id": district_id,
            "previous_code": previous_code,
            "new_code": new_code,
            "date": date
        }
    
    def analyze_zoning_boundaries(self):
        """Analyze zoning boundaries and identify potential conflicts."""
        if not self.zoning_districts:
            return {"status": "error", "message": "No zoning districts available for analysis"}
        
        districts_gdf = self.export_districts_to_geodataframe()
        
        # Find adjacent districts
        adjacency = []
        compatibility_scores = []
        boundary_lengths = []
        
        for i, district1 in districts_gdf.iterrows():
            for j, district2 in districts_gdf.iterrows():
                if i >= j:  # Skip self-comparisons and duplicates
                    continue
                
                if district1.geometry.touches(district2.geometry):
                    # Calculate the boundary length
                    boundary = district1.geometry.intersection(district2.geometry)
                    boundary_length = getattr(boundary, 'length', 0)
                    
                    # Get compatibility score
                    compatibility = self.calculate_compatibility(
                        district1.zoning_code, district2.zoning_code
                    )
                    
                    adjacency.append({
                        "district1_id": district1.id,
                        "district1_name": district1.name,
                        "district2_id": district2.id,
                        "district2_name": district2.name,
                        "district1_code": district1.zoning_code,
                        "district2_code": district2.zoning_code,
                        "boundary_length": boundary_length,
                        "compatibility_score": compatibility
                    })
                    
                    compatibility_scores.append(compatibility)
                    boundary_lengths.append(boundary_length)
        
        # Calculate statistics
        if not compatibility_scores:
            return {
                "status": "success", 
                "message": "No adjacent zoning districts found",
                "adjacency_count": 0
            }
        
        avg_compatibility = np.mean(compatibility_scores)
        potential_conflicts = [
            {
                "district1_id": adj["district1_id"],
                "district1_name": adj["district1_name"],
                "district2_id": adj["district2_id"],
                "district2_name": adj["district2_name"],
                "district1_code": adj["district1_code"],
                "district2_code": adj["district2_code"],
                "compatibility_score": adj["compatibility_score"],
                "boundary_length": adj["boundary_length"]
            }
            for adj in adjacency
            if adj["compatibility_score"] < 0.3  # Threshold for potential conflict
        ]
        
        total_boundary_length = sum(boundary_lengths)
        conflict_boundary_length = sum(
            adj["boundary_length"] for adj in adjacency
            if adj["compatibility_score"] < 0.3
        )
        
        # Calculate a graph-based adjacency network for visualization
        adjacency_graph = nx.Graph()
        for adj in adjacency:
            adjacency_graph.add_edge(
                adj["district1_id"], 
                adj["district2_id"], 
                weight=adj["compatibility_score"],
                boundary_length=adj["boundary_length"]
            )
        
        # Calculate network metrics
        connectivity = nx.average_node_connectivity(adjacency_graph) if adjacency_graph.nodes() else 0
        clustering = nx.average_clustering(adjacency_graph) if adjacency_graph.nodes() else 0
        
        return {
            "status": "success",
            "adjacency_count": len(adjacency),
            "average_compatibility": avg_compatibility,
            "potential_conflicts": potential_conflicts,
            "conflict_percentage": (conflict_boundary_length / total_boundary_length) * 100 if total_boundary_length else 0,
            "adjacency_details": adjacency,
            "network_metrics": {
                "connectivity": connectivity,
                "clustering": clustering,
                "node_count": len(adjacency_graph.nodes()),
                "edge_count": len(adjacency_graph.edges())
            },
            "adjacency_graph": adjacency_graph
        }
    
    def evaluate_zoning_change(self, district_id, new_code):
        """Evaluate the impact of changing a district's zoning code."""
        district = self.get_district_by_id(district_id)
        if not district:
            return {
                "status": "error", 
                "message": f"District with ID {district_id} not found"
            }
        
        if new_code not in self._code_index:
            return {
                "status": "error", 
                "message": f"Zoning code {new_code} not found"
            }
        
        old_code = district.zoning_code
        old_code_obj = self.get_code_by_id(old_code)
        new_code_obj = self.get_code_by_id(new_code)
        
        # Get adjacent districts
        districts_gdf = self.export_districts_to_geodataframe()
        district_row = districts_gdf[districts_gdf.id == district_id].iloc[0]
        
        adjacent_districts = []
        for _, adjacent in districts_gdf.iterrows():
            if adjacent.id != district_id and district_row.geometry.touches(adjacent.geometry):
                adjacent_districts.append(adjacent.id)
        
        # Calculate current and proposed compatibility with adjacent districts
        current_compatibility = []
        proposed_compatibility = []
        adjacent_details = []
        
        for adj_id in adjacent_districts:
            adj_district = self.get_district_by_id(adj_id)
            if adj_district:
                current_score = self.calculate_compatibility(old_code, adj_district.zoning_code)
                proposed_score = self.calculate_compatibility(new_code, adj_district.zoning_code)
                
                current_compatibility.append(current_score)
                proposed_compatibility.append(proposed_score)
                
                adjacent_details.append({
                    "district_id": adj_id,
                    "district_name": adj_district.name,
                    "zoning_code": adj_district.zoning_code,
                    "current_compatibility": current_score,
                    "proposed_compatibility": proposed_score,
                    "compatibility_change": proposed_score - current_score
                })
        
        if not current_compatibility:
            return {
                "status": "success",
                "message": "District has no adjacent districts for comparison",
                "district_id": district_id,
                "current_code": old_code,
                "proposed_code": new_code,
                "adjacent_count": 0
            }
        
        avg_current_compatibility = np.mean(current_compatibility)
        avg_proposed_compatibility = np.mean(proposed_compatibility)
        
        # Assess development capacity change
        current_capacity = None
        proposed_capacity = None
        
        if old_code_obj and old_code_obj.max_density:
            current_capacity = district.area_hectares * old_code_obj.max_density
            
        if new_code_obj and new_code_obj.max_density:
            proposed_capacity = district.area_hectares * new_code_obj.max_density
        
        capacity_change = None
        if current_capacity is not None and proposed_capacity is not None:
            capacity_change = proposed_capacity - current_capacity
        
        # Assess land use transitions
        land_use_transition = "unknown"
        if old_code_obj and new_code_obj:
            if old_code_obj.is_residential and new_code_obj.is_commercial:
                land_use_transition = "residential_to_commercial"
            elif old_code_obj.is_residential and new_code_obj.is_industrial:
                land_use_transition = "residential_to_industrial"
            elif old_code_obj.is_commercial and new_code_obj.is_residential:
                land_use_transition = "commercial_to_residential"
            elif old_code_obj.is_commercial and new_code_obj.is_industrial:
                land_use_transition = "commercial_to_industrial"
            elif old_code_obj.is_industrial and new_code_obj.is_commercial:
                land_use_transition = "industrial_to_commercial"
            elif old_code_obj.is_industrial and new_code_obj.is_residential:
                land_use_transition = "industrial_to_residential"
            elif old_code_obj.category == new_code_obj.category:
                land_use_transition = f"{old_code_obj.category}_intensity_change"
            else:
                land_use_transition = f"{old_code_obj.category}_to_{new_code_obj.category}"
        
        # Environmental impact assessment
        current_gdf = districts_gdf.copy()
        proposed_gdf = districts_gdf.copy()
        
        # Update the zoning code for the proposed scenario
        proposed_gdf.loc[proposed_gdf.id == district_id, 'zoning_code'] = new_code
        proposed_gdf.loc[proposed_gdf.id == district_id, 'category'] = new_code_obj.category if new_code_obj else "unknown"
        
        current_env_impact = self.environmental_assessment.calculate_environmental_impact(
            current_gdf[current_gdf.id == district_id]
        )
        
        proposed_env_impact = self.environmental_assessment.calculate_environmental_impact(
            proposed_gdf[proposed_gdf.id == district_id]
        )
        
        # Calculate environmental impact changes
        env_impact_changes = {}
        for key in current_env_impact:
            if key in proposed_env_impact:
                env_impact_changes[key] = proposed_env_impact[key] - current_env_impact[key]
        
        return {
            "status": "success",
            "district_id": district_id,
            "district_name": district.name,
            "current_code": old_code,
            "proposed_code": new_code,
            "adjacent_count": len(adjacent_districts),
            "average_current_compatibility": avg_current_compatibility,
            "average_proposed_compatibility": avg_proposed_compatibility,
            "compatibility_change": avg_proposed_compatibility - avg_current_compatibility,
            "adjacent_details": adjacent_details,
            "development_capacity": {
                "current": current_capacity,
                "proposed": proposed_capacity,
                "change": capacity_change
            },
            "land_use_transition": land_use_transition,
            "environmental_impact": {
                "current": current_env_impact,
                "proposed": proposed_env_impact,
                "changes": env_impact_changes
            }
        }
    
    def analyze_historical_zoning_changes(self, start_date=None, end_date=None):
        """Analyze historical zoning changes."""
        if not self.historical_changes:
            return {
                "status": "success",
                "message": "No historical zoning changes found",
                "change_count": 0
            }
        
        # Filter by date range if provided
        changes = self.historical_changes
        if start_date:
            changes = [c for c in changes if c['date'] >= start_date]
        if end_date:
            changes = [c for c in changes if c['date'] <= end_date]
        
        if not changes:
            return {
                "status": "success",
                "message": "No zoning changes found in the specified date range",
                "change_count": 0
            }
        
        # Sort by date
        changes = sorted(changes, key=lambda x: x['date'])
        
        # Calculate statistics
        change_count = len(changes)
        districts_changed = len(set(c['district_id'] for c in changes))
        
        # Count changes by type
        changes_by_category = {}
        for change in changes:
            previous_code = self.get_code_by_id(change['previous_code'])
            new_code = self.get_code_by_id(change['new_code'])
            
            if previous_code and new_code:
                transition = f"{previous_code.category}_to_{new_code.category}"
                if transition not in changes_by_category:
                    changes_by_category[transition] = 0
                changes_by_category[transition] += 1
        
        # Calculate change frequency over time
        time_periods = {}
        for change in changes:
            year = change['date'].year
            month = change['date'].month
            period = f"{year}-{month:02d}"
            
            if period not in time_periods:
                time_periods[period] = 0
            time_periods[period] += 1
        
        # Sort time periods
        sorted_periods = sorted(time_periods.items())
        periods = [p[0] for p in sorted_periods]
        frequencies = [p[1] for p in sorted_periods]
        
        return {
            "status": "success",
            "change_count": change_count,
            "districts_changed": districts_changed,
            "changes_by_category": changes_by_category,
            "time_periods": periods,
            "frequencies": frequencies,
            "changes": changes
        }
    
    def calculate_zoning_diversity(self):
        """Calculate zoning diversity metrics."""
        if not self.zoning_districts:
            return {
                "status": "error",
                "message": "No zoning districts available for analysis"
            }
        
        districts_gdf = self.export_districts_to_geodataframe()
        
        # Count zoning codes and categories
        code_counts = districts_gdf['zoning_code'].value_counts().to_dict()
        category_counts = districts_gdf['category'].value_counts().to_dict()
        
        total_districts = len(districts_gdf)
        unique_codes = len(code_counts)
        unique_categories = len(category_counts)
        
        # Calculate Shannon diversity index for zoning codes
        code_shannon = 0
        for code, count in code_counts.items():
            p = count / total_districts
            code_shannon -= p * np.log(p)
        
        # Calculate Shannon diversity index for categories
        category_shannon = 0
        for category, count in category_counts.items():
            p = count / total_districts
            category_shannon -= p * np.log(p)
        
        # Calculate evenness (normalized diversity)
        max_code_shannon = np.log(unique_codes) if unique_codes > 1 else 0
        max_category_shannon = np.log(unique_categories) if unique_categories > 1 else 0
        
        code_evenness = code_shannon / max_code_shannon if max_code_shannon > 0 else 0
        category_evenness = category_shannon / max_category_shannon if max_category_shannon > 0 else 0
        
        # Calculate area-weighted metrics
        total_area = districts_gdf.geometry.area.sum()
        
        area_by_code = {}
        for code in code_counts:
            area = districts_gdf[districts_gdf['zoning_code'] == code].geometry.area.sum()
            area_by_code[code] = area
        
        area_by_category = {}
        for category in category_counts:
            area = districts_gdf[districts_gdf['category'] == category].geometry.area.sum()
            area_by_category[category] = area
        
        # Area-weighted Shannon diversity
        area_code_shannon = 0
        for code, area in area_by_code.items():
            p = area / total_area
            area_code_shannon -= p * np.log(p)
        
        area_category_shannon = 0
        for category, area in area_by_category.items():
            p = area / total_area
            area_category_shannon -= p * np.log(p)
        
        return {
            "status": "success",
            "total_districts": total_districts,
            "unique_codes": unique_codes,
            "unique_categories": unique_categories,
            "code_counts": code_counts,
            "category_counts": category_counts,
            "diversity": {
                "code_shannon": code_shannon,
                "category_shannon": category_shannon,
                "code_evenness": code_evenness,
                "category_evenness": category_evenness,
                "area_code_shannon": area_code_shannon,
                "area_category_shannon": area_category_shannon
            },
            "area_by_code": area_by_code,
            "area_by_category": area_by_category
        }
    
    def export_districts_to_geodataframe(self):
        """Export zoning districts to a GeoDataFrame."""
        data = []
        
        for district in self.zoning_districts:
            if district.geometry is not None:
                code_obj = self._code_index.get(district.zoning_code)
                category = code_obj.category if code_obj else "unknown"
                
                district_dict = {
                    'id': district.id,
                    'name': district.name,
                    'zoning_code': district.zoning_code,
                    'category': category,
                    'geometry': district.geometry,
                    'date_established': district.date_established,
                    'population': district.population,
                    'employment': district.employment
                }
                data.append(district_dict)
        
        if not data:
            return gpd.GeoDataFrame()
        
        return gpd.GeoDataFrame(data, crs="EPSG:4326")
    
    def visualize_zoning(self, figsize=(12, 8), highlight_district=None, highlight_color='red', 
                       basemap=False, output_file=None, show_labels=True, title="Zoning Districts"):
        """Visualize zoning districts with enhanced styling."""
        if not self.zoning_districts:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No zoning districts available for visualization", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        districts_gdf = self.export_districts_to_geodataframe()
        
        # Create a color mapping for zoning categories
        unique_categories = sorted(districts_gdf['category'].unique())
        color_dict = create_custom_colormap(unique_categories)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot all districts
        for _, district in districts_gdf.iterrows():
            color = color_dict.get(district.category, '#CCCCCC')
            alpha = 0.8
            
            if highlight_district and district.id == highlight_district:
                # Highlight specific district
                label = district.name if show_labels else None
                districts_gdf[districts_gdf.id == highlight_district].plot(
                    ax=ax, 
                    color=highlight_color, 
                    edgecolor='black', 
                    linewidth=2,
                    alpha=0.9,
                    label=label
                )
            else:
                # Plot regular district
                label = district.name if show_labels else None
                ax.plot(*district.geometry.exterior.xy, color='black', linewidth=0.8)
                ax.fill(*district.geometry.exterior.xy, color=color, alpha=alpha, label=label)
        
        # Add basemap if requested and available
        if basemap and HAS_CONTEXTILY:
            try:
                cx.add_basemap(ax, crs=districts_gdf.crs)
            except Exception as e:
                print(f"Warning: Could not add basemap - {str(e)}")
        elif basemap and not HAS_CONTEXTILY:
            print("Warning: contextily package not found. Basemap not added.")
        
        # Add district labels if requested
        if show_labels:
            for _, district in districts_gdf.iterrows():
                centroid = district.geometry.centroid
                ax.annotate(district.name, 
                           (centroid.x, centroid.y),
                           fontsize=8,
                           ha='center',
                           va='center',
                           bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.3'))
        
        # Add legend for categories
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.6, edgecolor='black')
            for color in [color_dict[cat] for cat in unique_categories]
        ]
        
        ax.legend(legend_elements, unique_categories, 
                  loc='upper right', 
                  title='Zoning Categories',
                  framealpha=0.7,
                  fontsize=10)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.axis('equal')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add scalebar
        self._add_scale_bar(ax, districts_gdf)
        
        # Add north arrow
        self._add_north_arrow(ax)
        
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def visualize_zoning_comparison(self, district_id, new_code, figsize=(18, 8), 
                                   basemap=False, output_file=None):
        """Visualize a side-by-side comparison of current and proposed zoning."""
        district = self.get_district_by_id(district_id)
        if not district:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"District with ID {district_id} not found", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        if new_code not in self._code_index:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Zoning code {new_code} not found", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        # Get the original zoning code
        original_code = district.zoning_code
        
        # Create a temporary copy of the district with the new code
        temp_district = ZoningDistrict(
            id=district.id,
            name=district.name,
            zoning_code=new_code,
            jurisdiction_id=district.jurisdiction_id,
            geometry=district.geometry
        )
        
        # Create temporary copies of the analyzer with the original and new codes
        original_analyzer = ZoningAnalyzer(
            zoning_districts=self.zoning_districts,
            zoning_codes=self.zoning_codes
        )
        
        new_analyzer = ZoningAnalyzer(
            zoning_districts=[d if d.id != district_id else temp_district for d in self.zoning_districts],
            zoning_codes=self.zoning_codes
        )
        
        # Create the figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Visualize the original zoning
        original_analyzer.visualize_zoning(
            highlight_district=district_id,
            highlight_color='blue',
            basemap=basemap,
            title=f"Current Zoning: {original_code}",
            show_labels=False
        )
        
        # Get the axes from the original figure
        ax1.clear()
        original_gdf = original_analyzer.export_districts_to_geodataframe()
        
        # Visualize the new zoning
        new_analyzer.visualize_zoning(
            highlight_district=district_id,
            highlight_color='red',
            basemap=basemap,
            title=f"Proposed Zoning: {new_code}",
            show_labels=False
        )
        
        # Get the axes from the new figure
        ax2.clear()
        new_gdf = new_analyzer.export_districts_to_geodataframe()
        
        # Plot the original zoning
        unique_categories = sorted(original_gdf['category'].unique())
        color_dict = create_custom_colormap(unique_categories)
        
        for _, d in original_gdf.iterrows():
            color = color_dict.get(d.category, '#CCCCCC')
            if d.id == district_id:
                original_gdf[original_gdf.id == district_id].plot(
                    ax=ax1, color='blue', edgecolor='black', linewidth=2, alpha=0.9
                )
            else:
                ax1.plot(*d.geometry.exterior.xy, color='black', linewidth=0.8)
                ax1.fill(*d.geometry.exterior.xy, color=color, alpha=0.7)
        
        # Add labels
        for _, d in original_gdf.iterrows():
            if d.id == district_id:
                centroid = d.geometry.centroid
                ax1.annotate(d.name, 
                            (centroid.x, centroid.y),
                            fontsize=10,
                            ha='center',
                            va='center',
                            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
        
        # Plot the new zoning
        for _, d in new_gdf.iterrows():
            color = color_dict.get(d.category, '#CCCCCC')
            if d.id == district_id:
                new_gdf[new_gdf.id == district_id].plot(
                    ax=ax2, color='red', edgecolor='black', linewidth=2, alpha=0.9
                )
            else:
                ax2.plot(*d.geometry.exterior.xy, color='black', linewidth=0.8)
                ax2.fill(*d.geometry.exterior.xy, color=color, alpha=0.7)
        
        # Add labels
        for _, d in new_gdf.iterrows():
            if d.id == district_id:
                centroid = d.geometry.centroid
                ax2.annotate(d.name, 
                            (centroid.x, centroid.y),
                            fontsize=10,
                            ha='center',
                            va='center',
                            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
        
        # Add legend for categories
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.6, edgecolor='black')
            for color in [color_dict[cat] for cat in unique_categories]
        ]
        
        for ax in [ax1, ax2]:
            ax.legend(legend_elements, unique_categories, 
                    loc='upper right', 
                    title='Zoning Categories',
                    framealpha=0.7,
                    fontsize=9)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.axis('equal')
            ax.grid(True, linestyle='--', alpha=0.3)
        
        ax1.set_title(f"Current Zoning: {original_code}", fontsize=14, fontweight='bold')
        ax2.set_title(f"Proposed Zoning: {new_code}", fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def visualize_compatibility_matrix(self, figsize=(10, 8), cmap='RdYlGn', output_file=None):
        """Visualize the compatibility matrix between zoning codes."""
        if not self._compatibility_matrix:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No compatibility matrix available", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        # Convert matrix to DataFrame for easier plotting
        codes = sorted(self._compatibility_matrix.keys())
        matrix_data = []
        
        for code1 in codes:
            row = []
            for code2 in codes:
                row.append(self._compatibility_matrix[code1][code2])
            matrix_data.append(row)
        
        matrix_df = pd.DataFrame(matrix_data, index=codes, columns=codes)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Use seaborn for heatmap if available, otherwise use matplotlib
        if HAS_SEABORN:
            sns.heatmap(matrix_df, annot=True, cmap=cmap, vmin=0, vmax=1, ax=ax,
                       linewidths=0.5, square=True, cbar_kws={'label': 'Compatibility Score'})
        else:
            # Create our own heatmap with matplotlib
            im = ax.imshow(matrix_df.values, cmap=plt.cm.get_cmap(cmap), vmin=0, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Compatibility Score')
            
            # Add text annotations
            for i in range(len(codes)):
                for j in range(len(codes)):
                    text = ax.text(j, i, f"{matrix_df.iloc[i, j]:.2f}",
                                 ha="center", va="center", color="black")
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(codes)))
            ax.set_yticks(np.arange(len(codes)))
            ax.set_xticklabels(codes)
            ax.set_yticklabels(codes)
        
        # Create custom tick labels with categories
        xticklabels = []
        yticklabels = []
        
        for code in codes:
            zoning_code = self.get_code_by_id(code)
            if zoning_code:
                label = f"{code}\n({zoning_code.category})"
                xticklabels.append(label)
                yticklabels.append(label)
            else:
                xticklabels.append(code)
                yticklabels.append(code)
        
        ax.set_xticklabels(xticklabels, rotation=45, ha='right')
        ax.set_yticklabels(yticklabels, rotation=0)
        
        # Add a legend for categories
        category_colors = {}
        colors = generate_color_palette(len(set(zc.category for zc in self.zoning_codes)))
        categories = sorted(set(zc.category for zc in self.zoning_codes))
        
        for i, category in enumerate(categories):
            category_colors[category] = colors[i]
        
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black')
            for color in category_colors.values()
        ]
        
        plt.legend(legend_elements, category_colors.keys(), 
                  loc='upper left', 
                  bbox_to_anchor=(1.05, 1),
                  title='Categories')
        
        ax.set_title('Zoning Code Compatibility Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def visualize_adjacency_network(self, figsize=(12, 10), output_file=None):
        """Visualize the adjacency network of zoning districts."""
        boundary_analysis = self.analyze_zoning_boundaries()
        
        if boundary_analysis.get('status') != 'success' or boundary_analysis.get('adjacency_count', 0) == 0:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No adjacency information available for visualization", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        # Get the graph from the analysis
        adjacency_graph = boundary_analysis.get('adjacency_graph', nx.Graph())
        
        if not adjacency_graph.nodes():
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "Empty adjacency graph", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get district positions based on centroids
        districts_gdf = self.export_districts_to_geodataframe()
        pos = {}
        
        district_codes = {}  # Map district IDs to zoning codes
        district_categories = {}  # Map district IDs to categories
        
        for _, district in districts_gdf.iterrows():
            if district.id in adjacency_graph.nodes():
                centroid = district.geometry.centroid
                pos[district.id] = (centroid.x, centroid.y)
                district_codes[district.id] = district.zoning_code
                district_categories[district.id] = district.category
        
        # Node colors based on zoning category
        unique_categories = sorted(set(district_categories.values()))
        color_dict = create_custom_colormap(unique_categories)
        
        node_colors = [color_dict.get(district_categories.get(node, 'unknown'), '#CCCCCC') 
                       for node in adjacency_graph.nodes()]
        
        # Edge colors based on compatibility
        edge_colors = []
        edge_widths = []
        
        for u, v, data in adjacency_graph.edges(data=True):
            compatibility = data.get('weight', 0.5)
            
            # Use a gradient from red (low compatibility) to green (high compatibility)
            if compatibility < 0.3:
                color = 'red'
            elif compatibility < 0.6:
                color = 'orange'
            else:
                color = 'green'
            
            edge_colors.append(color)
            
            # Edge width based on boundary length
            boundary_length = data.get('boundary_length', 1)
            normalized_width = 1 + (boundary_length / 100)  # Scale for visibility
            edge_widths.append(normalized_width)
        
        # Draw the network
        nx.draw_networkx_nodes(adjacency_graph, pos, ax=ax, 
                              node_color=node_colors, 
                              node_size=300, 
                              alpha=0.8,
                              edgecolors='black')
        
        nx.draw_networkx_edges(adjacency_graph, pos, ax=ax,
                              edge_color=edge_colors,
                              width=edge_widths,
                              alpha=0.7)
        
        nx.draw_networkx_labels(adjacency_graph, pos, ax=ax,
                               labels={node: node for node in adjacency_graph.nodes()},
                               font_size=8)
        
        # Add legend for categories
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10)
            for color in [color_dict[cat] for cat in unique_categories]
        ]
        
        ax.legend(legend_elements, unique_categories, 
                  loc='upper right', 
                  title='Zoning Categories')
        
        # Add legend for edge colors
        edge_legend_elements = [
            plt.Line2D([0], [0], color='red', lw=2, label='Low Compatibility (<0.3)'),
            plt.Line2D([0], [0], color='orange', lw=2, label='Medium Compatibility (0.3-0.6)'),
            plt.Line2D([0], [0], color='green', lw=2, label='High Compatibility (>0.6)')
        ]
        
        ax.legend(handles=edge_legend_elements, 
                 loc='upper left',
                 title='Edge Compatibility')
        
        ax.set_title('Zoning District Adjacency Network', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def visualize_zoning_distribution(self, by='category', figsize=(12, 8), output_file=None):
        """Visualize the distribution of zoning districts by code or category."""
        if not self.zoning_districts:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No zoning districts available for visualization", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        districts_gdf = self.export_districts_to_geodataframe()
        
        # Calculate areas
        districts_gdf['area_hectares'] = districts_gdf.geometry.area / 10000
        
        if by == 'code':
            # Group by zoning code
            grouped = districts_gdf.groupby('zoning_code')['area_hectares'].sum().reset_index()
            grouped = grouped.sort_values('area_hectares', ascending=False)
            column = 'zoning_code'
            title = 'Zoning Distribution by Code'
        else:
            # Group by category
            grouped = districts_gdf.groupby('category')['area_hectares'].sum().reset_index()
            grouped = grouped.sort_values('area_hectares', ascending=False)
            column = 'category'
            title = 'Zoning Distribution by Category'
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Bar plot
        unique_values = grouped[column].unique()
        colors = generate_color_palette(len(unique_values))
        color_dict = {val: color for val, color in zip(unique_values, colors)}
        
        bar_colors = [color_dict[val] for val in grouped[column]]
        
        ax1.bar(grouped[column], grouped['area_hectares'], color=bar_colors)
        ax1.set_title(f'Area by {by.capitalize()}', fontsize=12)
        ax1.set_xlabel(by.capitalize())
        ax1.set_ylabel('Area (hectares)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on the bars
        for i, (value, area) in enumerate(zip(grouped[column], grouped['area_hectares'])):
            ax1.text(i, area + 0.1, f'{area:.1f}', ha='center', va='bottom', fontsize=8)
        
        # Pie chart
        wedges, texts, autotexts = ax2.pie(
            grouped['area_hectares'], 
            labels=grouped[column],
            autopct='%1.1f%%',
            colors=bar_colors,
            startangle=90,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # Customize pie chart text
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
        
        ax2.set_title(f'Percentage by {by.capitalize()}', fontsize=12)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def visualize_historical_changes(self, start_date=None, end_date=None, figsize=(12, 8), output_file=None):
        """Visualize historical zoning changes."""
        historical_analysis = self.analyze_historical_zoning_changes(start_date, end_date)
        
        if historical_analysis.get('status') != 'success' or historical_analysis.get('change_count', 0) == 0:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No historical zoning changes available for visualization", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        changes = historical_analysis['changes']
        periods = historical_analysis['time_periods']
        frequencies = historical_analysis['frequencies']
        changes_by_category = historical_analysis['changes_by_category']
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=figsize)
        gs = gridspec.GridSpec(2, 2, figure=fig)
        
        # 1. Timeline of changes
        ax1 = fig.add_subplot(gs[0, :])
        
        # Convert string periods to datetime for better x-axis formatting
        period_dates = [datetime.strptime(period, '%Y-%m') for period in periods]
        
        ax1.bar(period_dates, frequencies, color='skyblue', width=20)
        ax1.set_title('Zoning Changes Over Time', fontsize=12)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Changes')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Format x-axis with dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 2. Changes by transition type
        ax2 = fig.add_subplot(gs[1, 0])
        
        # Sort by count
        sorted_categories = sorted(changes_by_category.items(), key=lambda x: x[1], reverse=True)
        category_names = [cat[0] for cat in sorted_categories]
        category_counts = [cat[1] for cat in sorted_categories]
        
        # Generate colors
        transition_colors = generate_color_palette(len(category_names), mode='bright')
        
        # Create horizontal bar chart
        bars = ax2.barh(category_names, category_counts, color=transition_colors)
        ax2.set_title('Changes by Transition Type', fontsize=12)
        ax2.set_xlabel('Number of Changes')
        ax2.set_ylabel('Transition Type')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.0f}', va='center', fontsize=8)
        
        # Adjust tick labels if they're too long
        wrap_labels(ax2, width=15)
        
        # 3. District change frequency
        ax3 = fig.add_subplot(gs[1, 1])
        
        # Count changes by district
        district_changes = {}
        for change in changes:
            district_id = change['district_id']
            if district_id not in district_changes:
                district_changes[district_id] = 0
            district_changes[district_id] += 1
        
        # Sort by count
        sorted_districts = sorted(district_changes.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 10 districts if there are more than 10
        top_districts = sorted_districts[:10] if len(sorted_districts) > 10 else sorted_districts
        
        district_ids = [d[0] for d in top_districts]
        district_counts = [d[1] for d in top_districts]
        district_names = []
        
        # Get district names for labels
        for district_id in district_ids:
            district = self.get_district_by_id(district_id)
            name = district.name if district else district_id
            district_names.append(name)
        
        # Generate colors
        district_colors = generate_color_palette(len(district_names), mode='pastel')
        
        # Create horizontal bar chart
        bars = ax3.barh(district_names, district_counts, color=district_colors)
        ax3.set_title('Districts with Most Changes', fontsize=12)
        ax3.set_xlabel('Number of Changes')
        ax3.set_ylabel('District')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.0f}', va='center', fontsize=8)
        
        # Adjust tick labels if they're too long
        wrap_labels(ax3, width=15)
        
        plt.suptitle('Historical Zoning Change Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig
    
    def _add_scale_bar(self, ax, gdf, length=0.2):
        """Add a scale bar to the map."""
        # Find x range
        x_min, y_min, x_max, y_max = gdf.total_bounds
        x_range = x_max - x_min
        
        # Position of scale bar (bottom left)
        bar_x_left = x_min + x_range * 0.05
        bar_y = y_min + (y_max - y_min) * 0.05
        bar_x_right = bar_x_left + length
        
        # Draw scale bar
        ax.plot([bar_x_left, bar_x_right], [bar_y, bar_y], 'k-', linewidth=2)
        ax.plot([bar_x_left, bar_x_left], [bar_y - 0.01, bar_y + 0.01], 'k-', linewidth=2)
        ax.plot([bar_x_right, bar_x_right], [bar_y - 0.01, bar_y + 0.01], 'k-', linewidth=2)
        
        # Add label (assuming the units are degrees)
        ax.text((bar_x_left + bar_x_right) / 2, bar_y - 0.02, f'{length:.1f} units', 
                ha='center', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))
    
    def _add_north_arrow(self, ax):
        """Add a north arrow to the map."""
        # Get axis limits
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # Arrow position (top right)
        arrow_x = x_max - (x_max - x_min) * 0.05
        arrow_y = y_max - (y_max - y_min) * 0.1
        arrow_length = (y_max - y_min) * 0.05
        
        # Draw arrow
        ax.arrow(arrow_x, arrow_y, 0, arrow_length, head_width=arrow_length*0.3, 
                 head_length=arrow_length*0.3, fc='k', ec='k')
        
        # Add "N" label
        ax.text(arrow_x, arrow_y + arrow_length * 1.1, 'N', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    def visualize_land_use(self, land_use_gdf, category_column='land_use_category', 
                         confidence_column='land_use_confidence', figsize=(12, 8), 
                         basemap=False, output_file=None, cmap=None):
        """
        Visualize land use classification with enhanced styling.
        
        Parameters:
        -----------
        land_use_gdf : GeoDataFrame
            GeoDataFrame containing land use classifications
        category_column : str
            Column name containing land use categories
        confidence_column : str
            Column name containing confidence scores (optional)
        figsize : tuple
            Figure size (width, height)
        basemap : bool
            Whether to add a basemap
        output_file : str
            Filename to save the visualization
        cmap : str or colormap
            Colormap to use for categories
        """
        if land_use_gdf.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No land use data available for visualization", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        if category_column not in land_use_gdf.columns:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Column '{category_column}' not found in data", 
                    ha='center', va='center')
            if output_file:
                save_plot(fig, output_file)
            return fig
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create custom colormap for categories
        unique_categories = sorted(land_use_gdf[category_column].unique())
        if not cmap:
            color_dict = create_custom_colormap(unique_categories)
            
            # Create a custom colormap
            colors = [color_dict[cat] for cat in unique_categories]
            cmap = ListedColormap(colors)
        
        # Create a categorical plot
        land_use_gdf.plot(
            column=category_column,
            ax=ax,
            legend=True,
            cmap=cmap,
            categorical=True,
            legend_kwds={'title': 'Land Use Categories', 'loc': 'upper right'}
        )
        
        # If confidence column is available, add transparency based on confidence
        if confidence_column in land_use_gdf.columns:
            for idx, row in land_use_gdf.iterrows():
                confidence = row[confidence_column]
                if pd.notna(confidence):
                    # Minimum alpha is 0.3, maximum is 0.9
                    alpha = 0.3 + (confidence * 0.6)
                    
                    # Get category color
                    category = row[category_column]
                    color = color_dict.get(category, '#CCCCCC')
                    
                    # Plot with transparency
                    ax.plot(*row.geometry.exterior.xy, color='black', linewidth=0.5)
                    ax.fill(*row.geometry.exterior.xy, color=color, alpha=alpha)
        
        # Add basemap if requested and available
        if basemap and HAS_CONTEXTILY:
            try:
                cx.add_basemap(ax, crs=land_use_gdf.crs)
            except Exception as e:
                print(f"Warning: Could not add basemap - {str(e)}")
        elif basemap and not HAS_CONTEXTILY:
            print("Warning: contextily package not found. Basemap not added.")
        
        ax.set_title('Land Use Classification', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            save_plot(fig, output_file)
        
        return fig

def create_sample_data():
    """Create sample zoning data for the example."""
    # Create zoning codes with detailed specifications
    zoning_codes = [
        ZoningCode(
            code="R-1",
            name="Low Density Residential",
            description="Single-family residential zoning with large minimum lot sizes",
            category="residential",
            jurisdiction_id="city1",
            allowed_uses=["single_family_dwelling", "parks", "schools"],
            max_height=10,  # meters
            min_lot_size=800,  # square meters
            max_floor_area_ratio=0.35,
            max_density=12,  # units per hectare
            setbacks={"front": 6, "rear": 8, "side": 3},
            environmental_requirements={"min_permeable_surface": 0.4, "tree_canopy": 0.2}
        ),
        ZoningCode(
            code="R-2",
            name="Medium Density Residential",
            description="Single and two-family residential zoning",
            category="residential",
            jurisdiction_id="city1",
            allowed_uses=["single_family_dwelling", "duplex", "townhomes", "parks", "schools"],
            max_height=12,
            min_lot_size=500,
            max_floor_area_ratio=0.45,
            max_density=25,
            setbacks={"front": 5, "rear": 6, "side": 2.5},
            environmental_requirements={"min_permeable_surface": 0.35, "tree_canopy": 0.15}
        ),
        ZoningCode(
            code="C-1",
            name="Neighborhood Commercial",
            description="Small-scale commercial uses serving neighborhood needs",
            category="commercial",
            jurisdiction_id="city1",
            allowed_uses=["retail", "restaurants", "offices", "personal_services"],
            max_height=15,
            min_lot_size=300,
            max_floor_area_ratio=0.6,
            max_density=None,
            setbacks={"front": 3, "rear": 5, "side": 2},
            environmental_requirements={"min_permeable_surface": 0.25, "tree_canopy": 0.1}
        ),
        ZoningCode(
            code="C-2",
            name="General Commercial",
            description="Larger-scale commercial uses serving the community",
            category="commercial",
            jurisdiction_id="city1",
            allowed_uses=["retail", "restaurants", "offices", "personal_services", "hotels", "entertainment"],
            max_height=20,
            min_lot_size=500,
            max_floor_area_ratio=0.75,
            max_density=None,
            setbacks={"front": 2, "rear": 5, "side": 2},
            environmental_requirements={"min_permeable_surface": 0.2, "tree_canopy": 0.1}
        ),
        ZoningCode(
            code="I-1",
            name="Light Industrial",
            description="Light manufacturing and industrial uses",
            category="industrial",
            jurisdiction_id="city1",
            allowed_uses=["manufacturing", "warehousing", "research_facilities"],
            max_height=25,
            min_lot_size=1000,
            max_floor_area_ratio=0.5,
            max_density=None,
            setbacks={"front": 5, "rear": 5, "side": 5},
            environmental_requirements={"min_permeable_surface": 0.15, "tree_canopy": 0.05}
        ),
        ZoningCode(
            code="MU-1",
            name="Mixed Use",
            description="Mix of residential and commercial uses",
            category="mixed_use",
            jurisdiction_id="city1",
            allowed_uses=["multi_family_dwelling", "retail", "offices", "restaurants"],
            max_height=30,
            min_lot_size=400,
            max_floor_area_ratio=1.2,
            max_density=60,
            setbacks={"front": 2, "rear": 4, "side": 2},
            environmental_requirements={"min_permeable_surface": 0.2, "tree_canopy": 0.1}
        ),
        ZoningCode(
            code="P-1",
            name="Parks and Open Space",
            description="Public parks and open spaces",
            category="recreational",
            jurisdiction_id="city1",
            allowed_uses=["parks", "recreational_facilities", "nature_preserves"],
            max_height=12,
            min_lot_size=None,
            max_floor_area_ratio=0.1,
            max_density=None,
            setbacks={"front": 10, "rear": 10, "side": 10},
            environmental_requirements={"min_permeable_surface": 0.8, "tree_canopy": 0.4}
        ),
        ZoningCode(
            code="A-1",
            name="Agricultural",
            description="Agricultural uses and farming",
            category="agricultural",
            jurisdiction_id="city1",
            allowed_uses=["farming", "agriculture", "single_family_dwelling"],
            max_height=15,
            min_lot_size=20000,
            max_floor_area_ratio=0.1,
            max_density=0.5,
            setbacks={"front": 15, "rear": 15, "side": 10},
            environmental_requirements={"min_permeable_surface": 0.9, "tree_canopy": 0.2}
        ),
        ZoningCode(
            code="INS-1",
            name="Institutional",
            description="Schools, hospitals, and other institutional uses",
            category="institutional",
            jurisdiction_id="city1",
            allowed_uses=["schools", "hospitals", "government", "religious"],
            max_height=25,
            min_lot_size=1000,
            max_floor_area_ratio=0.8,
            max_density=None,
            setbacks={"front": 8, "rear": 8, "side": 5},
            environmental_requirements={"min_permeable_surface": 0.3, "tree_canopy": 0.2}
        )
    ]
    
    # Create zoning districts with enhanced metadata
    # Downtown core (mixed use)
    downtown = ZoningDistrict(
        id="district1",
        name="Downtown",
        zoning_code="MU-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (0, 0), (0, 1), (1, 1), (1, 0), (0, 0)
        ]),
        date_established=datetime(2000, 5, 15).date(),
        population=2500,
        employment=3000,
        overlay_codes=["historic_preservation"],
        environmental_features={"flood_zone": False, "wetlands": False}
    )
    
    # Commercial corridor along major road
    commercial_corridor = ZoningDistrict(
        id="district2",
        name="Main Street Commercial",
        zoning_code="C-2",
        jurisdiction_id="city1",
        geometry=Polygon([
            (1, 0), (1, 1), (3, 1), (3, 0), (1, 0)
        ]),
        date_established=datetime(1995, 8, 22).date(),
        population=500,
        employment=2000,
        overlay_codes=["business_improvement"],
        environmental_features={"flood_zone": False, "wetlands": False}
    )
    
    # Residential neighborhoods
    north_residential = ZoningDistrict(
        id="district3",
        name="North Residential",
        zoning_code="R-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (0, 1), (0, 3), (2, 3), (2, 1), (0, 1)
        ]),
        date_established=datetime(1985, 3, 10).date(),
        population=3500,
        employment=200,
        overlay_codes=["tree_preservation"],
        environmental_features={"flood_zone": False, "wetlands": True}
    )
    
    east_residential = ZoningDistrict(
        id="district4",
        name="East Residential",
        zoning_code="R-2",
        jurisdiction_id="city1",
        geometry=Polygon([
            (3, 0), (3, 2), (5, 2), (5, 0), (3, 0)
        ]),
        date_established=datetime(1990, 11, 5).date(),
        population=5000,
        employment=400,
        overlay_codes=[],
        environmental_features={"flood_zone": False, "wetlands": False}
    )
    
    # Industrial area
    industrial_area = ZoningDistrict(
        id="district5",
        name="South Industrial",
        zoning_code="I-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (0, -2), (0, 0), (2, 0), (2, -2), (0, -2)
        ]),
        date_established=datetime(1970, 6, 30).date(),
        population=100,
        employment=1500,
        overlay_codes=["brownfield_remediation"],
        environmental_features={"flood_zone": True, "wetlands": False}
    )
    
    # Park
    central_park = ZoningDistrict(
        id="district6",
        name="Central Park",
        zoning_code="P-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (2, 1), (2, 2), (3, 2), (3, 1), (2, 1)
        ]),
        date_established=datetime(1950, 4, 22).date(),
        population=0,
        employment=15,
        overlay_codes=["conservation"],
        environmental_features={"flood_zone": True, "wetlands": True}
    )
    
    # Neighborhood commercial
    neighborhood_commercial = ZoningDistrict(
        id="district7",
        name="East Commercial",
        zoning_code="C-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (2, 2), (2, 3), (3, 3), (3, 2), (2, 2)
        ]),
        date_established=datetime(2005, 9, 15).date(),
        population=200,
        employment=450,
        overlay_codes=[],
        environmental_features={"flood_zone": False, "wetlands": False}
    )
    
    # Agricultural area
    agricultural_area = ZoningDistrict(
        id="district8",
        name="North Agricultural",
        zoning_code="A-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (3, 2), (3, 4), (6, 4), (6, 2), (3, 2)
        ]),
        date_established=datetime(1960, 2, 10).date(),
        population=120,
        employment=80,
        overlay_codes=["agricultural_preservation"],
        environmental_features={"flood_zone": False, "wetlands": True}
    )
    
    # Institutional area
    institutional_area = ZoningDistrict(
        id="district9",
        name="University District",
        zoning_code="INS-1",
        jurisdiction_id="city1",
        geometry=Polygon([
            (2, -2), (2, -1), (4, -1), (4, -2), (2, -2)
        ]),
        date_established=datetime(1980, 8, 12).date(),
        population=1000,
        employment=800,
        overlay_codes=["educational"],
        environmental_features={"flood_zone": False, "wetlands": False}
    )
    
    # Add historical zoning changes to some districts
    north_residential.add_historical_record(
        date=datetime(1975, 5, 10).date(),
        previous_code="A-1",
        change_description="Converted from agricultural to low-density residential",
        ordinance_id="ORD-1975-42"
    )
    
    industrial_area.add_historical_record(
        date=datetime(1965, 3, 15).date(),
        previous_code="R-1",
        change_description="Converted from residential to industrial use",
        ordinance_id="ORD-1965-18"
    )
    
    industrial_area.add_historical_record(
        date=datetime(1995, 7, 20).date(),
        previous_code="I-2",
        change_description="Downzoned from heavy to light industrial",
        ordinance_id="ORD-1995-103"
    )
    
    downtown.add_historical_record(
        date=datetime(1990, 11, 5).date(),
        previous_code="C-2",
        change_description="Rezoned from commercial to mixed use to encourage residential development",
        ordinance_id="ORD-1990-87"
    )
    
    zoning_districts = [
        downtown,
        commercial_corridor,
        north_residential,
        east_residential,
        industrial_area,
        central_park,
        neighborhood_commercial,
        agricultural_area,
        institutional_area
    ]
    
    # Create land use types
    land_use_types = [
        LandUseType(
            id="residential_sf",
            name="Single-Family Residential",
            description="Single-family detached homes",
            category="residential",
            impervious_surface_ratio=0.4,
            trip_generation_rate=10,
            environmental_impact_score=30,
            resource_usage={"water": 150, "energy": 10}
        ),
        LandUseType(
            id="residential_mf",
            name="Multi-Family Residential",
            description="Apartments and condominiums",
            category="residential",
            impervious_surface_ratio=0.7,
            trip_generation_rate=6,
            environmental_impact_score=25,
            resource_usage={"water": 120, "energy": 8}
        ),
        LandUseType(
            id="commercial_retail",
            name="Retail Commercial",
            description="Retail stores and shopping centers",
            category="commercial",
            impervious_surface_ratio=0.8,
            trip_generation_rate=40,
            environmental_impact_score=50,
            resource_usage={"water": 5, "energy": 15}
        ),
        LandUseType(
            id="commercial_office",
            name="Office Commercial",
            description="Office buildings",
            category="commercial",
            impervious_surface_ratio=0.9,
            trip_generation_rate=15,
            environmental_impact_score=40,
            resource_usage={"water": 5, "energy": 18}
        ),
        LandUseType(
            id="industrial_light",
            name="Light Industrial",
            description="Light manufacturing and warehousing",
            category="industrial",
            impervious_surface_ratio=0.8,
            trip_generation_rate=8,
            environmental_impact_score=60,
            resource_usage={"water": 10, "energy": 25}
        ),
        LandUseType(
            id="parks_recreation",
            name="Parks and Recreation",
            description="Public parks and recreational areas",
            category="recreational",
            impervious_surface_ratio=0.1,
            trip_generation_rate=5,
            environmental_impact_score=10,
            resource_usage={"water": 20, "energy": 2}
        ),
        LandUseType(
            id="institutional",
            name="Institutional",
            description="Schools, hospitals, and government buildings",
            category="institutional",
            impervious_surface_ratio=0.7,
            trip_generation_rate=12,
            environmental_impact_score=35,
            resource_usage={"water": 15, "energy": 20}
        ),
        LandUseType(
            id="agricultural",
            name="Agricultural",
            description="Farms and agricultural areas",
            category="agricultural",
            impervious_surface_ratio=0.05,
            trip_generation_rate=2,
            environmental_impact_score=20,
            resource_usage={"water": 100, "energy": 5}
        ),
        LandUseType(
            id="mixed_use",
            name="Mixed Use",
            description="Combined residential and commercial uses",
            category="mixed_use",
            impervious_surface_ratio=0.8,
            trip_generation_rate=20,
            environmental_impact_score=35,
            resource_usage={"water": 100, "energy": 12}
        )
    ]
    
    # Create sample parcels
    parcels = []
    
    # Downtown parcels
    for i in range(5):
        for j in range(5):
            x = 0.1 + (i * 0.18)
            y = 0.1 + (j * 0.18)
            
            parcel = Parcel(
                id=f"parcel_downtown_{i}_{j}",
                address=f"{100 + i*10 + j} Main St",
                geometry=Polygon([
                    (x, y), (x+0.15, y), (x+0.15, y+0.15), (x, y+0.15), (x, y)
                ]),
                land_use="mixed_use",
                zoning_district_id="district1",
                building_footprint=0.15 * 0.15 * 0.7,  # 70% coverage
                building_height=random.randint(15, 30),
                year_built=random.randint(1950, 2010),
                assessed_value=random.randint(500000, 2000000)
            )
            parcels.append(parcel)
    
    # Commercial corridor parcels
    for i in range(10):
        for j in range(3):
            x = 1.1 + (i * 0.18)
            y = 0.1 + (j * 0.27)
            
            parcel = Parcel(
                id=f"parcel_commercial_{i}_{j}",
                address=f"{100 + i*10 + j} Commercial Ave",
                geometry=Polygon([
                    (x, y), (x+0.15, y), (x+0.15, y+0.25), (x, y+0.25), (x, y)
                ]),
                land_use="commercial_retail" if random.random() < 0.7 else "commercial_office",
                zoning_district_id="district2",
                building_footprint=0.15 * 0.25 * 0.8,  # 80% coverage
                building_height=random.randint(10, 20),
                year_built=random.randint(1960, 2015),
                assessed_value=random.randint(400000, 1500000)
            )
            parcels.append(parcel)
    
    # North residential parcels
    for i in range(6):
        for j in range(6):
            x = 0.2 + (i * 0.3)
            y = 1.2 + (j * 0.3)
            
            parcel = Parcel(
                id=f"parcel_north_res_{i}_{j}",
                address=f"{100 + i*10 + j} Oak St",
                geometry=Polygon([
                    (x, y), (x+0.25, y), (x+0.25, y+0.25), (x, y+0.25), (x, y)
                ]),
                land_use="residential_sf",
                zoning_district_id="district3",
                building_footprint=0.25 * 0.25 * 0.3,  # 30% coverage
                building_height=random.randint(6, 10),
                year_built=random.randint(1970, 2005),
                assessed_value=random.randint(300000, 800000)
            )
            parcels.append(parcel)
    
    # East residential parcels
    for i in range(6):
        for j in range(6):
            x = 3.2 + (i * 0.3)
            y = 0.2 + (j * 0.3)
            
            parcel = Parcel(
                id=f"parcel_east_res_{i}_{j}",
                address=f"{100 + i*10 + j} Elm St",
                geometry=Polygon([
                    (x, y), (x+0.25, y), (x+0.25, y+0.25), (x, y+0.25), (x, y)
                ]),
                land_use="residential_mf" if random.random() < 0.4 else "residential_sf",
                zoning_district_id="district4",
                building_footprint=0.25 * 0.25 * 0.4,  # 40% coverage
                building_height=random.randint(8, 15),
                year_built=random.randint(1980, 2020),
                assessed_value=random.randint(350000, 900000)
            )
            parcels.append(parcel)
    
    # Industrial parcels
    for i in range(4):
        for j in range(4):
            x = 0.2 + (i * 0.45)
            y = -1.8 + (j * 0.45)
            
            parcel = Parcel(
                id=f"parcel_industrial_{i}_{j}",
                address=f"{100 + i*10 + j} Factory Rd",
                geometry=Polygon([
                    (x, y), (x+0.4, y), (x+0.4, y+0.4), (x, y+0.4), (x, y)
                ]),
                land_use="industrial_light",
                zoning_district_id="district5",
                building_footprint=0.4 * 0.4 * 0.6,  # 60% coverage
                building_height=random.randint(8, 25),
                year_built=random.randint(1960, 2000),
                assessed_value=random.randint(200000, 1200000)
            )
            parcels.append(parcel)
    
    # Create a single park parcel
    park_parcel = Parcel(
        id="parcel_park",
        address="100 Park Ave",
        geometry=Polygon([
            (2.05, 1.05), (2.05, 1.95), (2.95, 1.95), (2.95, 1.05), (2.05, 1.05)
        ]),
        land_use="parks_recreation",
        zoning_district_id="district6",
        building_footprint=0.9 * 0.9 * 0.05,  # 5% coverage
        building_height=5,
        year_built=1955,
        assessed_value=500000
    )
    parcels.append(park_parcel)
    
    # Neighborhood commercial parcels
    for i in range(3):
        for j in range(3):
            x = 2.1 + (i * 0.25)
            y = 2.1 + (j * 0.25)
            
            parcel = Parcel(
                id=f"parcel_neigh_comm_{i}_{j}",
                address=f"{100 + i*10 + j} Market St",
                geometry=Polygon([
                    (x, y), (x+0.2, y), (x+0.2, y+0.2), (x, y+0.2), (x, y)
                ]),
                land_use="commercial_retail",
                zoning_district_id="district7",
                building_footprint=0.2 * 0.2 * 0.7,  # 70% coverage
                building_height=random.randint(6, 15),
                year_built=random.randint(1970, 2010),
                assessed_value=random.randint(300000, 800000)
            )
            parcels.append(parcel)
    
    # Agricultural parcels
    for i in range(3):
        for j in range(2):
            x = 3.2 + (i * 0.9)
            y = 2.2 + (j * 0.9)
            
            parcel = Parcel(
                id=f"parcel_agricultural_{i}_{j}",
                address=f"{100 + i*10 + j} Farm Rd",
                geometry=Polygon([
                    (x, y), (x+0.8, y), (x+0.8, y+0.8), (x, y+0.8), (x, y)
                ]),
                land_use="agricultural",
                zoning_district_id="district8",
                building_footprint=0.8 * 0.8 * 0.05,  # 5% coverage
                building_height=random.randint(5, 10),
                year_built=random.randint(1920, 1980),
                assessed_value=random.randint(150000, 500000)
            )
            parcels.append(parcel)
    
    # Institutional parcels
    for i in range(2):
        for j in range(2):
            x = 2.2 + (i * 0.8)
            y = -1.8 + (j * 0.8)
            
            parcel = Parcel(
                id=f"parcel_institutional_{i}_{j}",
                address=f"{100 + i*10 + j} Campus Dr",
                geometry=Polygon([
                    (x, y), (x+0.7, y), (x+0.7, y+0.7), (x, y+0.7), (x, y)
                ]),
                land_use="institutional",
                zoning_district_id="district9",
                building_footprint=0.7 * 0.7 * 0.5,  # 50% coverage
                building_height=random.randint(10, 25),
                year_built=random.randint(1950, 2010),
                assessed_value=random.randint(1000000, 5000000)
            )
            parcels.append(parcel)
    
    return zoning_codes, zoning_districts, land_use_types, parcels


def main():
    """Run the zoning analysis example with enhanced features."""
    print("GEO-INFER-NORMS Zoning Analysis Example")
    print("=======================================\n")
    
    # Create enhanced sample data
    print("Creating sample data...")
    zoning_codes, zoning_districts, land_use_types, parcels = create_sample_data()
    
    # Initialize the ZoningAnalyzer with enhanced data
    analyzer = ZoningAnalyzer(
        zoning_districts=zoning_districts, 
        zoning_codes=zoning_codes,
        parcels=parcels
    )
    
    # Initialize a LandUseClassifier
    land_use_classifier = LandUseClassifier(land_use_types=land_use_types)
    
    # 1. Display basic information about zoning districts
    print("\n1. Zoning Districts Overview")
    print("---------------------------")
    
    districts_summary = []
    for district in zoning_districts:
        code = analyzer.get_code_by_id(district.zoning_code)
        category = code.category if code else "unknown"
        districts_summary.append({
            "name": district.name,
            "zoning_code": district.zoning_code,
            "category": category,
            "area_hectares": district.area_hectares,
            "population": district.population,
            "employment": district.employment,
            "population_density": district.population_density
        })
    
    districts_df = pd.DataFrame(districts_summary)
    print(districts_df[['name', 'zoning_code', 'category', 'area_hectares', 'population', 'population_density']])
    
    # 2. Analyze zoning boundaries and compatibility
    print("\n2. Zoning Boundary Analysis")
    print("-------------------------")
    boundary_analysis = analyzer.analyze_zoning_boundaries()
    
    print(f"Total adjacency relationships: {boundary_analysis['adjacency_count']}")
    print(f"Average compatibility score: {boundary_analysis['average_compatibility']:.2f}")
    print(f"Conflict percentage: {boundary_analysis['conflict_percentage']:.2f}%")
    
    if boundary_analysis['potential_conflicts']:
        print("\nPotential conflicts:")
        for conflict in boundary_analysis['potential_conflicts']:
            print(f"  {conflict['district1_name']} ({conflict['district1_code']}) and "
                  f"{conflict['district2_name']} ({conflict['district2_code']})")
            print(f"  Compatibility score: {conflict['compatibility_score']:.2f}")
            print(f"  Boundary length: {conflict['boundary_length']:.2f}")
            print()
    
    # Create an adjacency network visualization
    print("\nGenerating zoning adjacency network visualization...")
    network_fig = analyzer.visualize_adjacency_network(
        output_file="zoning_adjacency_network.png"
    )
    
    # 3. Evaluate a zoning change scenario
    print("\n3. Zoning Change Evaluation")
    print("-------------------------")
    # Evaluate changing the industrial area to mixed use
    evaluation = analyzer.evaluate_zoning_change("district5", "MU-1")
    
    print(f"District: {evaluation['district_name']}")
    print(f"Current zoning: {evaluation['current_code']}")
    print(f"Proposed zoning: {evaluation['proposed_code']}")
    print(f"Current compatibility with neighbors: {evaluation['average_current_compatibility']:.2f}")
    print(f"Proposed compatibility with neighbors: {evaluation['average_proposed_compatibility']:.2f}")
    print(f"Compatibility change: {evaluation['compatibility_change']:.2f}")
    
    # Display capacity changes
    if evaluation['development_capacity']['current'] is not None and evaluation['development_capacity']['proposed'] is not None:
        print(f"\nDevelopment capacity:")
        print(f"  Current: {evaluation['development_capacity']['current']:.1f} units")
        print(f"  Proposed: {evaluation['development_capacity']['proposed']:.1f} units")
        print(f"  Change: {evaluation['development_capacity']['change']:.1f} units")
    
    # Display environmental impact changes
    print("\nEnvironmental impact changes:")
    env_changes = evaluation['environmental_impact']['changes']
    for metric, change in env_changes.items():
        print(f"  {metric}: {change:+.2f}")
    
    # 4. Visualize zoning districts
    print("\n4. Visualizing Zoning Districts")
    print("----------------------------")
    print("Generating zoning district visualizations...")
    
    # Basic zoning district visualization
    fig_basic = analyzer.visualize_zoning(
        figsize=(10, 8),
        output_file="zoning_districts.png"
    )
    
    # Visualization with a highlighted district
    fig_highlight = analyzer.visualize_zoning(
        figsize=(10, 8),
        highlight_district="district5",
        highlight_color='red',
        title="Zoning Districts with Industrial Zone Highlighted",
        output_file="zoning_districts_highlight.png"
    )
    
    # Side-by-side comparison of current vs. proposed zoning
    fig_comparison = analyzer.visualize_zoning_comparison(
        district_id="district5",
        new_code="MU-1",
        output_file="zoning_change_visualization.png"
    )
    
    # 5. Zoning distribution analysis
    print("\n5. Zoning Distribution Analysis")
    print("----------------------------")
    
    # Visualize zoning distribution by category
    fig_distribution = analyzer.visualize_zoning_distribution(
        by='category',
        output_file="zoning_distribution_by_category.png"
    )
    
    # Calculate zoning diversity metrics
    diversity_metrics = analyzer.calculate_zoning_diversity()
    print("\nZoning diversity metrics:")
    print(f"  Shannon diversity index (codes): {diversity_metrics['diversity']['code_shannon']:.3f}")
    print(f"  Shannon diversity index (categories): {diversity_metrics['diversity']['category_shannon']:.3f}")
    print(f"  Evenness (codes): {diversity_metrics['diversity']['code_evenness']:.3f}")
    print(f"  Evenness (categories): {diversity_metrics['diversity']['category_evenness']:.3f}")
    
    # 6. Land Use Classification
    print("\n6. Land Use Classification")
    print("------------------------")
    
    # Create a sample dataset of parcels with features for land use classification
    parcels_gdf = gpd.GeoDataFrame.from_features([
        {
            'type': 'Feature',
            'geometry': mapping(parcel.geometry),
            'properties': {
                'id': parcel.id,
                'building_count': 1,
                'population_density': 50 if 'res' in parcel.id else 5,
                'business_count': 10 if 'comm' in parcel.id else 0,
                'building_height': parcel.building_height,
                'imperviousness': 0.8 if 'comm' in parcel.id else 0.5
            }
        }
        for parcel in parcels[:50]  # Use a subset for demonstration
    ])
    
    # Apply rule-based classification
    print("\nApplying rule-based land use classification...")
    rule_based_result = land_use_classifier.classify_land_use(
        parcels_gdf,
        feature_columns=['building_count', 'population_density', 'business_count', 
                        'building_height', 'imperviousness'],
        method="rule_based"
    )
    
    # Summarize classification results
    rule_based_summary = rule_based_result['land_use_category'].value_counts()
    print("\nRule-based classification results:")
    for category, count in rule_based_summary.items():
        print(f"  {category}: {count} parcels")
    
    # Apply cluster-based classification if scikit-learn is available
    if HAS_SKLEARN:
        print("\nApplying cluster-based land use classification (K-means)...")
        kmeans_result = land_use_classifier.classify_land_use(
        parcels_gdf,
            feature_columns=['building_count', 'population_density', 'business_count', 
                            'building_height', 'imperviousness'],
            method="kmeans"
        )
        
        # Summarize classification results
        kmeans_summary = kmeans_result['land_use_category'].value_counts()
        print("\nK-means classification results:")
        for category, count in kmeans_summary.items():
            print(f"  {category}: {count} parcels")
    else:
        print("\nSkipping K-means classification (scikit-learn not available)")
        kmeans_result = rule_based_result
    
    # Create land use visualizations
    print("\nGenerating land use classification visualizations...")
    fig_landuse = land_use_classifier.visualize_land_use(
        rule_based_result,
        output_file="land_use_classification.png"
    )
    
    fig_confidence = land_use_classifier.visualize_classification_confidence(
        rule_based_result,
        output_file="land_use_classification_confidence.png"
    )
    
    # 7. Land Use Pattern Analysis
    print("\n7. Land Use Pattern Analysis")
    print("-------------------------")
    
    land_use_analysis = land_use_classifier.analyze_land_use_pattern(
        rule_based_result,
        category_column='land_use_category'
    )
    
    print("\nLand use pattern analysis results:")
    print(f"Total categories: {land_use_analysis['category_count']}")
    print(f"Average land use compatibility: {land_use_analysis['average_compatibility']:.2f}")
    
    print("\nPercentage by category:")
    for category, percentage in land_use_analysis['percentage_by_category'].items():
        print(f"  {category}: {percentage:.2f}%")
    
    print("\nFragmentation metrics:")
    print(f"  Patch density: {land_use_analysis['fragmentation_metrics']['patch_density']:.6f}")
    print(f"  Largest patch index: {land_use_analysis['fragmentation_metrics']['largest_patch_index']:.2f}")
    
    print("\nConnectivity metrics:")
    print(f"  Component count: {land_use_analysis['connectivity_metrics']['component_count']}")
    print(f"  Average component size: {land_use_analysis['connectivity_metrics']['avg_component_size']:.2f}")
    print(f"  Connectance: {land_use_analysis['connectivity_metrics']['connectance']:.4f}")
    
    # Visualize land use analysis
    print("\nGenerating land use analysis visualization...")
    fig_landuse_analysis = land_use_classifier.visualize_land_use_analysis(
        land_use_analysis,
        output_file="land_use_analysis.png"
    )
    
    # 8. Historical Zoning Analysis
    print("\n8. Historical Zoning Change Analysis")
    print("--------------------------------")
    
    # Create some additional historical records for demonstration
    analyzer.change_district_zoning(
        "district4", 
        "R-1", 
        change_date=datetime(2005, 4, 15).date(),
        description="Downzoned from medium-density to low-density residential",
        ordinance_id="ORD-2005-42"
    )
    
    analyzer.change_district_zoning(
        "district7", 
        "MU-1", 
        change_date=datetime(2018, 7, 10).date(),
        description="Rezoned from neighborhood commercial to mixed use",
        ordinance_id="ORD-2018-103"
    )
    
    analyzer.change_district_zoning(
        "district2", 
        "MU-1", 
        change_date=datetime(2020, 3, 5).date(),
        description="Rezoned from general commercial to mixed use to encourage housing",
        ordinance_id="ORD-2020-28"
    )
    
    # Analyze historical changes
    historical_analysis = analyzer.analyze_historical_zoning_changes()
    
    print(f"Total zoning changes: {historical_analysis['change_count']}")
    print(f"Districts with changes: {historical_analysis['districts_changed']}")
    print("\nChanges by category transition:")
    for transition, count in historical_analysis['changes_by_category'].items():
        print(f"  {transition}: {count}")
    
    # Visualize historical changes
    print("\nGenerating historical zoning change visualization...")
    fig_historical = analyzer.visualize_historical_changes(
        output_file="historical_zoning_changes.png"
    )
    
    # 9. Zoning compatibility matrix visualization
    print("\n9. Zoning Compatibility Matrix")
    print("---------------------------")
    print("Generating zoning compatibility matrix visualization...")
    fig_compatibility = analyzer.visualize_compatibility_matrix(
        output_file="zoning_compatibility_matrix.png"
    )
    
    # 10. Environmental Impact Assessment
    print("\n10. Environmental Impact Assessment")
    print("-------------------------------")
    
    # Calculate environmental impact of current zoning
    districts_gdf = analyzer.export_districts_to_geodataframe()
    environmental_assessment = analyzer.environmental_assessment.calculate_environmental_impact(districts_gdf)
    
    print("\nEnvironmental impact of current zoning:")
    print(f"  Daily water usage: {environmental_assessment['total_water_usage']:.2f} liters")
    print(f"  Annual energy usage: {environmental_assessment['total_energy_usage']:.2f} kWh")
    print(f"  Annual CO2 emissions: {environmental_assessment['total_co2_emissions']:.2f} tonnes")
    print(f"  Imperviousness percentage: {environmental_assessment['imperviousness_percentage']:.2f}%")
    print(f"  Runoff potential: {environmental_assessment['runoff_potential']:.2f}")
    print(f"  Heat island effect: {environmental_assessment['heat_island_effect']:.2f}°C increase")
    
    # 11. Export Analysis Results
    print("\n11. Exporting Analysis Results")
    print("---------------------------")
    
    # Combine all analysis results
    analysis_results = {
        "zoning_summary": {
            "district_count": len(zoning_districts),
            "code_count": len(zoning_codes),
            "parcel_count": len(parcels),
            "total_area_hectares": sum(district.area_hectares for district in zoning_districts),
            "total_population": sum(district.population or 0 for district in zoning_districts),
            "total_employment": sum(district.employment or 0 for district in zoning_districts)
        },
            "boundary_analysis": {
                "adjacency_count": boundary_analysis['adjacency_count'],
                "average_compatibility": float(boundary_analysis['average_compatibility']),
                "conflict_percentage": float(boundary_analysis['conflict_percentage']),
                "potential_conflicts": [
                    {
                    "district1": conflict["district1_name"],
                    "district2": conflict["district2_name"],
                    "score": float(conflict["compatibility_score"])
                }
                for conflict in boundary_analysis['potential_conflicts']
                ]
            },
            "zoning_change_evaluation": {
                "district": evaluation['district_name'],
                "current_code": evaluation['current_code'],
                "proposed_code": evaluation['proposed_code'],
                "current_compatibility": float(evaluation['average_current_compatibility']),
                "proposed_compatibility": float(evaluation['average_proposed_compatibility']),
            "compatibility_change": float(evaluation['compatibility_change']),
            "development_capacity_change": float(evaluation['development_capacity']['change']) 
                if evaluation['development_capacity']['change'] is not None else None
            },
            "land_use_analysis": {
                "category_count": land_use_analysis['category_count'],
                "percentage_by_category": {
                    k: float(v) for k, v in land_use_analysis['percentage_by_category'].items()
                },
            "average_compatibility": float(land_use_analysis['average_compatibility']),
            "shannon_diversity": float(land_use_analysis['diversity_metrics']['shannon_index']),
            "evenness": float(land_use_analysis['diversity_metrics']['evenness'])
        },
        "environmental_assessment": {
            "water_usage": float(environmental_assessment['total_water_usage']),
            "energy_usage": float(environmental_assessment['total_energy_usage']),
            "co2_emissions": float(environmental_assessment['total_co2_emissions']),
            "imperviousness": float(environmental_assessment['imperviousness_percentage']),
            "runoff_potential": float(environmental_assessment['runoff_potential']),
            "heat_island_effect": float(environmental_assessment['heat_island_effect'])
        },
        "historical_changes": {
            "total_changes": historical_analysis['change_count'],
            "districts_changed": historical_analysis['districts_changed'],
            "changes_by_category": historical_analysis['changes_by_category']
        },
        "timestamp": get_current_timestamp(),
        "dependencies": {
            "has_seaborn": HAS_SEABORN,
            "has_contextily": HAS_CONTEXTILY,
            "has_sklearn": HAS_SKLEARN,
            "has_folium": HAS_FOLIUM
        }
    }
    
    # Export to JSON file
    with open(os.path.join(output_dir, "zoning_analysis_results.json"), "w") as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"Exported comprehensive analysis results to {os.path.join(output_dir, 'zoning_analysis_results.json')}")
    
    # Generate a list of all output files
    output_files = [f for f in os.listdir(output_dir) if f.endswith(('.png', '.json'))]
    print(f"\nTotal output files generated: {len(output_files)}")
    for file in output_files:
        print(f"  - {file}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 