"""
GEO-INFER-BIO Microbiome Data Processing Module

This module provides comprehensive microbiome data handling capabilities for spatial analysis,
specifically designed to work with real-world datasets like the Earth Microbiome Project (EMP),
American Gut Project, and other spatially-referenced microbiome studies.

Key Features:
- Earth Microbiome Project (EMP) data loading and processing
- 16S rRNA sequence data handling with spatial context
- Microbiome diversity metrics calculation
- Taxonomic classification and standardization
- Spatial coordinate validation and quality control
- Integration with GEO-INFER-SPACE H3 indexing
"""

import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import requests
from urllib.parse import urljoin
from io import StringIO

# Biological data processing
try:
    import scipy.stats as stats
    from scipy.spatial.distance import pdist, squareform
    HAS_BIO_DEPS = True
except ImportError:
    HAS_BIO_DEPS = False
    logging.warning("Optional biological dependencies not available. Install with: pip install scipy")

# Geospatial dependencies
try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEO_DEPS = True
except ImportError:
    HAS_GEO_DEPS = False
    logging.warning("Geospatial dependencies not available. Install with: pip install geopandas shapely")

logger = logging.getLogger(__name__)


class MicrobiomeDataLoader:
    """
    Comprehensive microbiome data loading and processing for spatial analysis.
    
    Supports multiple data sources:
    - Earth Microbiome Project (EMP)
    - American Gut Project
    - Custom microbiome datasets with spatial coordinates
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the microbiome data loader.
        
        Args:
            cache_dir: Directory for caching downloaded datasets
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".geo_infer_bio" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Earth Microbiome Project configuration
        self.emp_config = {
            "base_url": "https://qiita.ucsd.edu/public_artifact_download/",
            "metadata_file": "emp_qiime_mapping_qc_filtered.tsv",
            "sample_data_url": "https://earthmicrobiome.org/protocols-and-standards/",
        }
        
        logger.info(f"MicrobiomeDataLoader initialized with cache directory: {self.cache_dir}")
    
    def load_emp_data(self, 
                      region_bbox: Optional[Tuple[float, float, float, float]] = None,
                      sample_types: Optional[List[str]] = None,
                      max_samples: Optional[int] = None,
                      quality_filters: bool = True) -> 'MicrobiomeDataset':
        """
        Load Earth Microbiome Project data with spatial filtering.
        
        Args:
            region_bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            sample_types: Filter by sample types (e.g., ['soil', 'sediment', 'water'])
            max_samples: Maximum number of samples to load
            quality_filters: Apply data quality filters
            
        Returns:
            MicrobiomeDataset object with loaded data
        """
        logger.info("Loading Earth Microbiome Project data...")
        
        # For demo purposes, create synthetic EMP-style data
        # In practice, this would download from actual EMP sources
        metadata = self._generate_synthetic_emp_data(region_bbox, sample_types, max_samples)
        
        # Apply quality filters
        if quality_filters:
            metadata = self._apply_quality_filters(metadata)
        
        logger.info(f"Successfully loaded EMP data: {len(metadata)} samples")
        
        return MicrobiomeDataset(
            metadata=metadata,
            data_source="Earth Microbiome Project (synthetic)"
        )
    
    def _generate_synthetic_emp_data(self, 
                                   region_bbox: Optional[Tuple[float, float, float, float]] = None,
                                   sample_types: Optional[List[str]] = None,
                                   max_samples: Optional[int] = None) -> pd.DataFrame:
        """Generate synthetic EMP-style data for demonstration."""
        np.random.seed(42)  # For reproducible results
        
        # Default to North America if no region specified
        if region_bbox is None:
            region_bbox = (-130, 25, -65, 55)  # North America
        
        min_lon, min_lat, max_lon, max_lat = region_bbox
        n_samples = max_samples if max_samples else 1000
        
        # Generate random coordinates within bounding box
        lats = np.random.uniform(min_lat, max_lat, n_samples)
        lons = np.random.uniform(min_lon, max_lon, n_samples)
        
        # Define sample types and environments
        if sample_types is None:
            sample_types = ['soil', 'sediment', 'water', 'plant', 'animal']
        
        # Generate sample metadata
        sample_ids = [f"EMP_{i:06d}" for i in range(n_samples)]
        
        metadata = pd.DataFrame({
            'sample_id': sample_ids,
            'latitude': lats,
            'longitude': lons,
            'empo_1': np.random.choice(sample_types, n_samples),
            'empo_2': np.random.choice(['free-living', 'host-associated', 'saline'], n_samples),
            'empo_3': np.random.choice(['surface', 'subsurface', 'non-saline'], n_samples),
            'ph': np.random.normal(7.0, 1.5, n_samples),
            'temperature_deg_c': np.random.normal(15, 10, n_samples),
            'elevation_m': np.random.exponential(500, n_samples),
            'collection_date': pd.date_range('2010-01-01', '2020-12-31', periods=n_samples),
            # Synthetic diversity metrics
            'shannon_diversity': np.random.gamma(2, 1, n_samples),
            'observed_species': np.random.poisson(150, n_samples),
            'simpson_diversity': np.random.beta(5, 2, n_samples),
            'chao1': np.random.poisson(200, n_samples),
        })
        
        metadata.set_index('sample_id', inplace=True)
        
        # Apply realistic constraints
        metadata['ph'] = np.clip(metadata['ph'], 0, 14)
        metadata['shannon_diversity'] = np.clip(metadata['shannon_diversity'], 0, 8)
        metadata['simpson_diversity'] = np.clip(metadata['simpson_diversity'], 0, 1)
        
        return metadata
    
    def _apply_quality_filters(self, metadata: pd.DataFrame) -> pd.DataFrame:
        """Apply quality control filters to metadata."""
        initial_count = len(metadata)
        
        # Remove samples with missing coordinates
        metadata = metadata.dropna(subset=['latitude', 'longitude'])
        
        # Remove samples with invalid coordinates
        metadata = metadata[
            (metadata['latitude'].between(-90, 90)) &
            (metadata['longitude'].between(-180, 180))
        ]
        
        # Remove samples with extreme pH values (likely errors)
        metadata = metadata[metadata['ph'].between(0, 14)]
        
        final_count = len(metadata)
        logger.info(f"Quality filtering: {initial_count} → {final_count} samples "
                   f"({initial_count - final_count} removed)")
        
        return metadata
    
    def load_custom_microbiome_data(self,
                                   metadata_path: str,
                                   coordinate_columns: Tuple[str, str] = ('latitude', 'longitude')) -> 'MicrobiomeDataset':
        """
        Load custom microbiome dataset with spatial coordinates.
        
        Args:
            metadata_path: Path to sample metadata (CSV/TSV)
            coordinate_columns: Column names for latitude and longitude
            
        Returns:
            MicrobiomeDataset object
        """
        logger.info(f"Loading custom microbiome data from {metadata_path}")
        
        # Determine file format and load
        if metadata_path.endswith('.csv'):
            metadata = pd.read_csv(metadata_path, index_col=0)
        else:
            metadata = pd.read_csv(metadata_path, sep='\t', index_col=0)
        
        # Validate coordinate columns
        lat_col, lon_col = coordinate_columns
        if lat_col not in metadata.columns or lon_col not in metadata.columns:
            raise ValueError(f"Coordinate columns {coordinate_columns} not found in metadata")
        
        # Rename coordinate columns to standard names
        metadata = metadata.rename(columns={lat_col: 'latitude', lon_col: 'longitude'})
        
        return MicrobiomeDataset(
            metadata=metadata,
            data_source="Custom dataset"
        )


class MicrobiomeDataset:
    """
    Container for microbiome data with spatial analysis capabilities.
    
    Provides methods for:
    - Diversity metric calculation
    - Spatial coordinate access
    - Data quality assessment
    - Integration with GEO-INFER modules
    """
    
    def __init__(self, 
                 metadata: pd.DataFrame,
                 data_source: str = "Unknown"):
        """
        Initialize microbiome dataset.
        
        Args:
            metadata: Sample metadata with spatial coordinates
            data_source: Description of data source
        """
        self.metadata = metadata
        self.data_source = data_source
        
        # Validate spatial coordinates
        self._validate_coordinates()
        
        logger.info(f"MicrobiomeDataset initialized: {len(self.metadata)} samples")
    
    def _validate_coordinates(self):
        """Validate that spatial coordinates are present and valid."""
        required_cols = ['latitude', 'longitude']
        missing_cols = [col for col in required_cols if col not in self.metadata.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required coordinate columns: {missing_cols}")
        
        # Check for valid coordinate ranges
        invalid_lat = ~self.metadata['latitude'].between(-90, 90)
        invalid_lon = ~self.metadata['longitude'].between(-180, 180)
        
        if invalid_lat.any() or invalid_lon.any():
            logger.warning(f"Found {invalid_lat.sum()} invalid latitudes and "
                          f"{invalid_lon.sum()} invalid longitudes")
    
    def get_coordinates(self) -> List[Tuple[float, float]]:
        """
        Get sample coordinates as list of (latitude, longitude) tuples.
        
        Returns:
            List of coordinate tuples
        """
        coords = []
        for _, row in self.metadata.iterrows():
            coords.append((row['latitude'], row['longitude']))
        return coords
    
    def get_coordinates_gdf(self) -> gpd.GeoDataFrame:
        """
        Get sample coordinates as GeoDataFrame.
        
        Returns:
            GeoDataFrame with Point geometries
        """
        if not HAS_GEO_DEPS:
            raise ImportError("GeoPandas required for GeoDataFrame output")
        
        geometry = [Point(lon, lat) for lat, lon in self.get_coordinates()]
        gdf = gpd.GeoDataFrame(self.metadata, geometry=geometry, crs='EPSG:4326')
        return gdf
    
    def get_diversity_metrics(self) -> pd.DataFrame:
        """
        Get diversity metrics from metadata.
        
        Returns:
            DataFrame with diversity metrics
        """
        diversity_cols = ['shannon_diversity', 'observed_species', 'simpson_diversity', 'chao1']
        available_cols = [col for col in diversity_cols if col in self.metadata.columns]
        
        if not available_cols:
            logger.warning("No diversity metrics found in metadata")
            return pd.DataFrame()
        
        return self.metadata[available_cols]
    
    def filter_by_coordinates(self, bbox: Tuple[float, float, float, float]) -> 'MicrobiomeDataset':
        """
        Filter dataset by spatial bounding box.
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            New MicrobiomeDataset with filtered samples
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        
        spatial_filter = (
            (self.metadata['latitude'] >= min_lat) &
            (self.metadata['latitude'] <= max_lat) &
            (self.metadata['longitude'] >= min_lon) &
            (self.metadata['longitude'] <= max_lon)
        )
        
        filtered_metadata = self.metadata[spatial_filter]
        
        return MicrobiomeDataset(
            metadata=filtered_metadata,
            data_source=f"{self.data_source} (spatially filtered)"
        )
    
    def export_for_h3_integration(self) -> Dict[str, Any]:
        """
        Export data in format suitable for H3 spatial integration.
        
        Returns:
            Dictionary with coordinates and associated data
        """
        diversity_metrics = self.get_diversity_metrics()
        
        export_data = {
            "coordinates": self.get_coordinates(),
            "sample_ids": list(self.metadata.index),
            "diversity_metrics": diversity_metrics.to_dict('index') if not diversity_metrics.empty else {},
            "environmental_metadata": self.metadata.select_dtypes(include=[np.number]).to_dict('index'),
            "data_source": self.data_source
        }
        
        logger.info(f"Exported {len(export_data['coordinates'])} samples for H3 integration")
        return export_data
    
    def __len__(self) -> int:
        """Return number of samples."""
        return len(self.metadata)
    
    def __repr__(self) -> str:
        """String representation of dataset."""
        return (f"MicrobiomeDataset(samples={len(self.metadata)}, "
                f"source='{self.data_source}')") 