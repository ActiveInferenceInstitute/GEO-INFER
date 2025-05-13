"""
Zoning analysis module for geospatial analysis of zoning laws and land use regulations.

This module provides classes and functions for analyzing zoning regulations,
land use classifications, and their spatial implications.
"""

import geopandas as gpd
from typing import Dict, List, Optional, Set, Tuple, Union, Any
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon, LineString
import logging
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import networkx as nx

from ..models.zoning import ZoningCode, LandUseType, ZoningDistrict

logger = logging.getLogger(__name__)


class ZoningAnalyzer:
    """
    A class for analyzing zoning regulations and their spatial implications.
    
    This class provides methods for analyzing zoning districts, assessing compatibility
    between different zoning types, and evaluating zoning changes.
    """
    
    def __init__(
        self, 
        zoning_districts: Optional[List[ZoningDistrict]] = None,
        zoning_codes: Optional[List[ZoningCode]] = None
    ):
        """
        Initialize a ZoningAnalyzer instance.
        
        Args:
            zoning_districts: List of ZoningDistrict objects
            zoning_codes: List of ZoningCode objects defining zoning regulations
        """
        self.zoning_districts = zoning_districts or []
        self.zoning_codes = zoning_codes or []
        self._district_index = {d.id: d for d in self.zoning_districts}
        self._code_index = {c.code: c for c in self.zoning_codes}
        
        # Create compatibility matrix between zoning types
        self._compatibility_matrix = self._build_compatibility_matrix()
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Build a compatibility matrix between different zoning codes.
        
        Returns:
            A nested dictionary mapping zoning code pairs to compatibility scores (0-1)
        """
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
                
                matrix[code1.code][code2.code] = compatibility
        
        return matrix
    
    def add_zoning_district(self, district: ZoningDistrict) -> None:
        """
        Add a zoning district to the analyzer.
        
        Args:
            district: The ZoningDistrict object to add
        """
        self.zoning_districts.append(district)
        self._district_index[district.id] = district
    
    def add_zoning_code(self, code: ZoningCode) -> None:
        """
        Add a zoning code to the analyzer.
        
        Args:
            code: The ZoningCode object to add
        """
        self.zoning_codes.append(code)
        self._code_index[code.code] = code
        # Rebuild compatibility matrix
        self._compatibility_matrix = self._build_compatibility_matrix()
    
    def get_district_by_id(self, district_id: str) -> Optional[ZoningDistrict]:
        """
        Get a zoning district by its ID.
        
        Args:
            district_id: The ID of the district
            
        Returns:
            The ZoningDistrict object or None if not found
        """
        return self._district_index.get(district_id)
    
    def get_code_by_id(self, code_id: str) -> Optional[ZoningCode]:
        """
        Get a zoning code by its ID.
        
        Args:
            code_id: The ID of the code
            
        Returns:
            The ZoningCode object or None if not found
        """
        return self._code_index.get(code_id)
    
    def get_zoning_at_point(self, point: Point) -> List[ZoningDistrict]:
        """
        Get all zoning districts that contain a specific point.
        
        Args:
            point: A Shapely Point geometry
            
        Returns:
            A list of ZoningDistrict objects that contain the point
        """
        containing_districts = []
        
        for district in self.zoning_districts:
            if district.geometry is not None and district.geometry.contains(point):
                containing_districts.append(district)
        
        return containing_districts
    
    def calculate_compatibility(self, code1: str, code2: str) -> float:
        """
        Calculate the compatibility score between two zoning codes.
        
        Args:
            code1: The first zoning code
            code2: The second zoning code
            
        Returns:
            A compatibility score between 0 (incompatible) and 1 (fully compatible)
        """
        if code1 not in self._compatibility_matrix or code2 not in self._compatibility_matrix:
            logger.warning(f"Zoning code {code1} or {code2} not found in compatibility matrix")
            return 0.5  # Default medium compatibility
        
        return self._compatibility_matrix[code1][code2]
    
    def analyze_zoning_boundaries(self) -> Dict[str, Any]:
        """
        Analyze zoning district boundaries for potential conflicts.
        
        Returns:
            A dictionary containing analysis results
        """
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
                    if isinstance(boundary, (LineString, MultiPolygon)):
                        boundary_length = boundary.length
                    else:
                        boundary_length = 0
                    
                    # Get compatibility score
                    compatibility = self.calculate_compatibility(
                        district1.zoning_code, district2.zoning_code
                    )
                    
                    adjacency.append({
                        "district1_id": district1.id,
                        "district2_id": district2.id,
                        "district1_code": district1.zoning_code,
                        "district2_code": district2.zoning_code,
                        "boundary_length": boundary_length
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
            (adj["district1_id"], adj["district2_id"], c_score)
            for adj, c_score in zip(adjacency, compatibility_scores)
            if c_score < 0.3  # Threshold for potential conflict
        ]
        
        total_boundary_length = sum(boundary_lengths)
        conflict_boundary_length = sum(
            length for length, score in zip(boundary_lengths, compatibility_scores)
            if score < 0.3
        )
        
        return {
            "status": "success",
            "adjacency_count": len(adjacency),
            "average_compatibility": avg_compatibility,
            "potential_conflicts": potential_conflicts,
            "conflict_percentage": (conflict_boundary_length / total_boundary_length) * 100 if total_boundary_length else 0,
            "adjacency_details": adjacency
        }
    
    def evaluate_zoning_change(
        self, 
        district_id: str, 
        new_code: str
    ) -> Dict[str, Any]:
        """
        Evaluate the impact of changing a district's zoning code.
        
        Args:
            district_id: The ID of the district to change
            new_code: The new zoning code to apply
            
        Returns:
            A dictionary containing the evaluation results
        """
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
            "adjacent_details": adjacent_details
        }
    
    def visualize_zoning(
        self, 
        figsize: Tuple[int, int] = (12, 8),
        highlight_district: Optional[str] = None,
        highlight_color: str = 'red',
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a visualization of zoning districts.
        
        Args:
            figsize: Figure size as (width, height) in inches
            highlight_district: Optional ID of a district to highlight
            highlight_color: Color for highlighting the selected district
            save_path: Optional path to save the figure
            
        Returns:
            A matplotlib Figure object
        """
        if not self.zoning_districts:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No zoning districts available for visualization", 
                    ha='center', va='center')
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        
        districts_gdf = self.export_districts_to_geodataframe()
        
        # Create a color mapping for zoning categories
        unique_categories = districts_gdf['category'].unique()
        cmap = plt.colormaps['tab10'].resampled(len(unique_categories))
        color_dict = {cat: f"#{int(cmap(i)[0]*255):02x}{int(cmap(i)[1]*255):02x}{int(cmap(i)[2]*255):02x}" 
                      for i, cat in enumerate(unique_categories)}
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot all districts
        for _, district in districts_gdf.iterrows():
            color = color_dict.get(district.category, '#CCCCCC')
            if highlight_district and district.id == highlight_district:
                districts_gdf[districts_gdf.id == highlight_district].plot(
                    ax=ax, color=highlight_color, edgecolor='black', linewidth=2
                )
            else:
                ax.plot(*district.geometry.exterior.xy, color=color, linewidth=1)
                ax.fill(*district.geometry.exterior.xy, color=color, alpha=0.6)
        
        # Add legend
        patches = [plt.Rectangle((0, 0), 1, 1, color=color, alpha=0.6) for color in color_dict.values()]
        ax.legend(patches, color_dict.keys(), loc='upper right', title='Zoning Categories')
        
        ax.set_title('Zoning Districts')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.axis('equal')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    def export_districts_to_geodataframe(self) -> gpd.GeoDataFrame:
        """
        Export zoning districts to a GeoDataFrame.
        
        Returns:
            A GeoDataFrame containing district geometries and properties
        """
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
                    'geometry': district.geometry
                }
                data.append(district_dict)
        
        if not data:
            logger.warning("No districts with geometry found for GeoDataFrame export")
            return gpd.GeoDataFrame()
        
        return gpd.GeoDataFrame(data, crs="EPSG:4326")
    
    def __repr__(self) -> str:
        return f"ZoningAnalyzer(districts={len(self.zoning_districts)}, codes={len(self.zoning_codes)})"


class LandUseClassifier:
    """
    A class for classifying and analyzing land use patterns.
    
    This class provides methods for classifying land use types, analyzing
    land use patterns, and evaluating land use compatibility.
    """
    
    def __init__(
        self, 
        land_use_types: Optional[List[LandUseType]] = None,
        compatibility_thresholds: Optional[Dict[str, Dict[str, float]]] = None
    ):
        """
        Initialize a LandUseClassifier instance.
        
        Args:
            land_use_types: List of LandUseType objects
            compatibility_thresholds: Optional dictionary defining compatibility thresholds
        """
        self.land_use_types = land_use_types or []
        self._type_index = {t.id: t for t in self.land_use_types}
        
        # Set default compatibility thresholds if not provided
        self.compatibility_thresholds = compatibility_thresholds or {
            "residential": {
                "residential": 0.9,
                "commercial": 0.6,
                "industrial": 0.2,
                "agricultural": 0.7,
                "recreational": 0.8,
                "institutional": 0.7,
                "mixed_use": 0.8
            },
            "commercial": {
                "residential": 0.6,
                "commercial": 0.9,
                "industrial": 0.5,
                "agricultural": 0.4,
                "recreational": 0.7,
                "institutional": 0.8,
                "mixed_use": 0.8
            },
            "industrial": {
                "residential": 0.2,
                "commercial": 0.5,
                "industrial": 0.9,
                "agricultural": 0.4,
                "recreational": 0.3,
                "institutional": 0.4,
                "mixed_use": 0.5
            },
            "agricultural": {
                "residential": 0.7,
                "commercial": 0.4,
                "industrial": 0.4,
                "agricultural": 0.9,
                "recreational": 0.8,
                "institutional": 0.6,
                "mixed_use": 0.6
            },
            "recreational": {
                "residential": 0.8,
                "commercial": 0.7,
                "industrial": 0.3,
                "agricultural": 0.8,
                "recreational": 0.9,
                "institutional": 0.8,
                "mixed_use": 0.8
            },
            "institutional": {
                "residential": 0.7,
                "commercial": 0.8,
                "industrial": 0.4,
                "agricultural": 0.6,
                "recreational": 0.8,
                "institutional": 0.9,
                "mixed_use": 0.8
            },
            "mixed_use": {
                "residential": 0.8,
                "commercial": 0.8,
                "industrial": 0.5,
                "agricultural": 0.6,
                "recreational": 0.8,
                "institutional": 0.8,
                "mixed_use": 0.9
            }
        }
    
    def add_land_use_type(self, land_use_type: LandUseType) -> None:
        """
        Add a land use type to the classifier.
        
        Args:
            land_use_type: The LandUseType object to add
        """
        self.land_use_types.append(land_use_type)
        self._type_index[land_use_type.id] = land_use_type
    
    def get_land_use_type_by_id(self, type_id: str) -> Optional[LandUseType]:
        """
        Get a land use type by its ID.
        
        Args:
            type_id: The ID of the land use type
            
        Returns:
            The LandUseType object or None if not found
        """
        return self._type_index.get(type_id)
    
    def calculate_compatibility(self, type1_category: str, type2_category: str) -> float:
        """
        Calculate the compatibility score between two land use categories.
        
        Args:
            type1_category: The first land use category
            type2_category: The second land use category
            
        Returns:
            A compatibility score between 0 (incompatible) and 1 (fully compatible)
        """
        if type1_category not in self.compatibility_thresholds or \
           type2_category not in self.compatibility_thresholds.get(type1_category, {}):
            logger.warning(f"Land use category {type1_category} or {type2_category} not found in compatibility matrix")
            return 0.5  # Default medium compatibility
        
        return self.compatibility_thresholds[type1_category][type2_category]
    
    def analyze_land_use_pattern(
        self,
        land_use_gdf: gpd.GeoDataFrame,
        category_column: str = 'category'
    ) -> Dict[str, Any]:
        """
        Analyze the pattern of land use in a given area.
        
        Args:
            land_use_gdf: GeoDataFrame containing land use polygons
            category_column: Column name for land use categories
            
        Returns:
            A dictionary containing analysis results
        """
        results = {}
        if land_use_gdf.empty:
            results["status"] = "error"
            results["message"] = "Empty GeoDataFrame provided"
            logger.error(results["message"])
            return results
        
        # Ensure the GeoDataFrame has the required column
        if category_column not in land_use_gdf.columns:
            results["status"] = "error"
            results["message"] = f"Category column '{category_column}' not found in GeoDataFrame"
            logger.error(results["message"])
            return results
        
        # Ensure valid geometries
        land_use_gdf = land_use_gdf[land_use_gdf.geometry.is_valid]
        if land_use_gdf.empty:
            results["status"] = "error"
            results["message"] = "No valid geometries found in GeoDataFrame"
            logger.error(results["message"])
            return results
            
        # Reproject for accurate area calculation (using EPSG:3857 as a common web mercator)
        # Store original CRS to potentially revert later if needed, though area is the goal here.
        original_crs = land_use_gdf.crs
        try:
            gdf_proj = land_use_gdf.to_crs(epsg=3857) 
        except Exception as e:
            logger.error(f"Failed to reproject GeoDataFrame for area calculation: {e}")
            results["status"] = "error"
            results["message"] = f"Failed to reproject GeoDataFrame: {e}"
            return results
            
        gdf_proj['area'] = gdf_proj.geometry.area
        # land_use_gdf['area'] = land_use_gdf.geometry.area # Original line
        
        total_area = gdf_proj['area'].sum()
        results["total_area"] = total_area
        
        # Calculate area and percentage by category
        area_by_category = gdf_proj.groupby(category_column)['area'].sum()
        percentage_by_category = (area_by_category / total_area) * 100
        results["area_by_category"] = area_by_category.to_dict()
        results["percentage_by_category"] = percentage_by_category.to_dict()
        results["category_count"] = land_use_gdf[category_column].nunique()
        
        # Analyze adjacency and compatibility
        adjacency_matrix = {}
        compatibility_scores = []
        
        # Create a spatial index for more efficient computation
        spatial_index = land_use_gdf.sindex
        
        for idx, parcel in land_use_gdf.iterrows():
            parcel_category = parcel[category_column]
            
            if parcel_category not in adjacency_matrix:
                adjacency_matrix[parcel_category] = {}
            
            # Find adjacent parcels using the spatial index
            possible_matches_index = list(spatial_index.intersection(parcel.geometry.bounds))
            possible_matches = land_use_gdf.iloc[possible_matches_index]
            
            for adj_idx, adj_parcel in possible_matches.iterrows():
                if idx == adj_idx:
                    continue
                
                adj_category = adj_parcel[category_column]
                
                if parcel.geometry.touches(adj_parcel.geometry):
                    if adj_category not in adjacency_matrix[parcel_category]:
                        adjacency_matrix[parcel_category][adj_category] = 0
                    
                    adjacency_matrix[parcel_category][adj_category] += 1
                    
                    # Calculate compatibility
                    compatibility = self.calculate_compatibility(parcel_category, adj_category)
                    compatibility_scores.append(compatibility)
        
        # Build a network representation
        land_use_network = nx.Graph()
        
        for cat1 in adjacency_matrix:
            for cat2 in adjacency_matrix[cat1]:
                weight = adjacency_matrix[cat1][cat2]
                land_use_network.add_edge(cat1, cat2, weight=weight)
        
        # Calculate network metrics
        network_metrics = {}
        if land_use_network.nodes():
            try:
                network_metrics = {
                    "density": nx.density(land_use_network),
                    "avg_clustering": nx.average_clustering(land_use_network),
                    "centrality": {node: score for node, score in 
                                  nx.degree_centrality(land_use_network).items()}
                }
            except Exception as e:
                network_metrics = {"error": str(e)}
        
        # Overall compatibility score
        avg_compatibility = np.mean(compatibility_scores) if compatibility_scores else 0
        
        results["status"] = "success"
        results["adjacency_matrix"] = adjacency_matrix
        results["average_compatibility"] = avg_compatibility
        results["network_metrics"] = network_metrics
        
        return results
    
    def classify_land_use(
        self,
        features_gdf: gpd.GeoDataFrame,
        feature_columns: List[str]
    ) -> gpd.GeoDataFrame:
        """
        Classify land use based on feature characteristics.
        
        Args:
            features_gdf: GeoDataFrame containing parcels and their features
            feature_columns: List of column names to use as features
            
        Returns:
            A copy of the input GeoDataFrame with added land use classification
        """
        if features_gdf.empty:
            logger.warning("Empty GeoDataFrame provided for classification")
            return features_gdf.copy()
        
        # Check if all required columns exist
        missing_columns = [col for col in feature_columns if col not in features_gdf.columns]
        if missing_columns:
            logger.warning(f"Missing feature columns: {missing_columns}")
            return features_gdf.copy()
        
        # Simple rule-based classification
        result_gdf = features_gdf.copy()
        result_gdf['land_use_category'] = 'unclassified'
        result_gdf['land_use_confidence'] = 0.0
        
        # This is a placeholder for a more sophisticated classification algorithm
        # In a real implementation, this could use machine learning or more complex rules
        
        # For demonstration, we'll use a very simple rule-based approach
        for idx, parcel in result_gdf.iterrows():
            # Extract features
            features = {col: parcel[col] for col in feature_columns if col in parcel}
            
            # Apply simple rules (these would be much more sophisticated in practice)
            category = 'unclassified'
            confidence = 0.5
            
            # Example rules (these would be based on real-world knowledge in practice)
            if 'building_count' in features and features['building_count'] > 10:
                if 'population_density' in features and features['population_density'] > 5000:
                    category = 'residential'
                    confidence = 0.8
                elif 'business_count' in features and features['business_count'] > 5:
                    category = 'commercial'
                    confidence = 0.7
            elif 'farmland_percentage' in features and features['farmland_percentage'] > 70:
                category = 'agricultural'
                confidence = 0.9
            elif 'park_area' in features and features['park_area'] > 10000:
                category = 'recreational'
                confidence = 0.85
            
            result_gdf.at[idx, 'land_use_category'] = category
            result_gdf.at[idx, 'land_use_confidence'] = confidence
        
        return result_gdf
    
    def visualize_land_use(
        self,
        land_use_gdf: gpd.GeoDataFrame,
        category_column: str = 'land_use_category',
        figsize: Tuple[int, int] = (12, 8),
        cmap: Optional[Union[str, ListedColormap]] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a visualization of land use patterns.
        
        Args:
            land_use_gdf: GeoDataFrame containing land use polygons
            category_column: Column name for land use categories
            figsize: Figure size as (width, height) in inches
            cmap: Optional colormap for visualization
            save_path: Optional path to save the figure
            
        Returns:
            A matplotlib Figure object
        """
        if land_use_gdf.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No land use data available for visualization", 
                    ha='center', va='center')
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        
        if category_column not in land_use_gdf.columns:
            logger.warning(f"Category column '{category_column}' not found in GeoDataFrame")
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Column '{category_column}' not found in data", 
                    ha='center', va='center')
            if save_path:
                plt.savefig(save_path, bbox_inches='tight')
            return fig
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create a categorical plot
        land_use_gdf.plot(
            column=category_column,
            ax=ax,
            legend=True,
            cmap=cmap or 'tab10',
            categorical=True,
            legend_kwds={'title': 'Land Use Categories', 'loc': 'upper right'}
        )
        
        ax.set_title('Land Use Classification')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        return fig
    
    def __repr__(self) -> str:
        return f"LandUseClassifier(types={len(self.land_use_types)})" 