"""Performance tests for the FieldBoundaryManager class."""

import pytest
import time
import numpy as np
from shapely.geometry import Polygon
import geopandas as gpd
import tempfile
import os
import rasterio
from rasterio.transform import from_origin

from geo_infer_ag.core.field_boundary import FieldBoundaryManager


class TestFieldBoundaryManagerPerformance:
    """Performance test suite for FieldBoundaryManager class."""
    
    @pytest.fixture
    def large_field_dataset(self, n_fields=1000):
        """Create a large dataset of fields for performance testing."""
        field_ids = [f"field_{i}" for i in range(n_fields)]
        names = [f"Field {i}" for i in range(n_fields)]
        
        # Create a grid of fields
        grid_size = int(np.ceil(np.sqrt(n_fields)))
        geometries = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                if len(geometries) < n_fields:
                    geometries.append(
                        Polygon([
                            (i*10, j*10),
                            (i*10, (j+1)*10),
                            ((i+1)*10, (j+1)*10),
                            ((i+1)*10, j*10)
                        ])
                    )
        
        # Crop types with realistic distribution
        crop_types = np.random.choice(
            ["corn", "wheat", "soybean", "cotton", "rice"], 
            size=n_fields,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        )
        
        # Create GeoDataFrame
        return gpd.GeoDataFrame(
            {
                "field_id": field_ids[:n_fields],
                "name": names[:n_fields],
                "crop_type": crop_types,
                "geometry": geometries[:n_fields]
            },
            crs="EPSG:4326"
        )
    
    @pytest.fixture
    def large_raster(self, size=1000):
        """Create a large raster file for performance testing."""
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
            raster_path = tmp.name
            
            # Create a random raster with field-like patterns
            data = np.zeros((size, size), dtype=np.uint8)
            
            # Create random field patterns
            for _ in range(50):
                x = np.random.randint(0, size - 100)
                y = np.random.randint(0, size - 100)
                w = np.random.randint(20, 100)
                h = np.random.randint(20, 100)
                data[y:y+h, x:x+w] = 1
            
            transform = from_origin(0, size, 1, 1)
            
            with rasterio.open(
                raster_path, 'w',
                driver='GTiff',
                height=data.shape[0],
                width=data.shape[1],
                count=1,
                dtype=data.dtype,
                crs='+proj=latlong',
                transform=transform,
            ) as dst:
                dst.write(data, 1)
                
        return raster_path
    
    def test_initialization_performance(self, large_field_dataset):
        """Test initialization performance with a large dataset."""
        start_time = time.time()
        
        fbm = FieldBoundaryManager(fields=large_field_dataset)
        
        elapsed_time = time.time() - start_time
        print(f"\nInitialization with {len(large_field_dataset)} fields: {elapsed_time:.4f} seconds")
        
        # Performance assertion - should initialize in less than 2 seconds
        # Adjust threshold based on hardware expectations
        assert elapsed_time < 2.0
    
    def test_add_field_performance(self):
        """Test performance of adding many fields."""
        fbm = FieldBoundaryManager()
        n_fields = 1000
        
        start_time = time.time()
        
        for i in range(n_fields):
            fbm.add_field(
                geometry=Polygon([
                    (i, 0),
                    (i, 1),
                    (i+1, 1),
                    (i+1, 0)
                ]),
                field_id=f"field_{i}",
                name=f"Field {i}",
                crop_type="corn"
            )
        
        elapsed_time = time.time() - start_time
        print(f"\nAdding {n_fields} fields: {elapsed_time:.4f} seconds")
        
        # Performance assertion - should add fields in less than 5 seconds
        # Adjust threshold based on hardware expectations
        assert elapsed_time < 5.0
    
    def test_get_neighboring_fields_performance(self, large_field_dataset):
        """Test performance of finding neighboring fields."""
        fbm = FieldBoundaryManager(fields=large_field_dataset)
        
        start_time = time.time()
        
        # Find neighbors for 50 random fields
        for _ in range(50):
            field_id = np.random.choice(fbm.fields["field_id"])
            neighbors = fbm.get_neighboring_fields(field_id, buffer_distance=20.0)
        
        elapsed_time = time.time() - start_time
        print(f"\nFinding neighbors for 50 fields among {len(large_field_dataset)}: {elapsed_time:.4f} seconds")
        
        # Performance assertion - should find neighbors in less than 3 seconds
        # Adjust threshold based on hardware expectations
        assert elapsed_time < 3.0
    
    def test_get_fields_by_crop_performance(self, large_field_dataset):
        """Test performance of filtering fields by crop type."""
        fbm = FieldBoundaryManager(fields=large_field_dataset)
        
        start_time = time.time()
        
        for crop_type in ["corn", "wheat", "soybean", "cotton", "rice"]:
            crop_fields = fbm.get_fields_by_crop(crop_type)
        
        elapsed_time = time.time() - start_time
        print(f"\nFiltering by 5 crop types among {len(large_field_dataset)} fields: {elapsed_time:.4f} seconds")
        
        # Performance assertion - should filter in less than 0.5 seconds
        # Adjust threshold based on hardware expectations
        assert elapsed_time < 0.5
    
    def test_extract_fields_from_raster_performance(self, large_raster):
        """Test performance of extracting fields from a large raster."""
        fbm = FieldBoundaryManager()
        
        try:
            start_time = time.time()
            
            n_fields = fbm.extract_fields_from_raster(
                raster_path=large_raster,
                value_field=1,
                min_area=0.01,
                simplify_tolerance=1.0
            )
            
            elapsed_time = time.time() - start_time
            print(f"\nExtracting {n_fields} fields from large raster: {elapsed_time:.4f} seconds")
            
            # Performance assertion - should extract in less than 10 seconds
            # Adjust threshold based on hardware expectations
            assert elapsed_time < 10.0
            
        finally:
            # Clean up the temporary file
            if os.path.exists(large_raster):
                os.unlink(large_raster)
    
    def test_export_to_file_performance(self, large_field_dataset):
        """Test performance of exporting a large dataset to a file."""
        fbm = FieldBoundaryManager(fields=large_field_dataset)
        
        # Create a temporary output file
        with tempfile.NamedTemporaryFile(suffix='.shp', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            start_time = time.time()
            
            fbm.export_to_file(output_path=output_path)
            
            elapsed_time = time.time() - start_time
            print(f"\nExporting {len(large_field_dataset)} fields to shapefile: {elapsed_time:.4f} seconds")
            
            # Performance assertion - should export in less than 5 seconds
            # Adjust threshold based on hardware expectations
            assert elapsed_time < 5.0
            
        finally:
            # Clean up temporary files
            if os.path.exists(output_path):
                # Need to remove all associated files (.dbf, .shx, etc.)
                base_path = output_path[:-4]  # Remove .shp extension
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    if os.path.exists(base_path + ext):
                        os.unlink(base_path + ext) 