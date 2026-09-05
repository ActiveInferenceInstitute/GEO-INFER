"""
Basic climate analysis example.

Demonstrates loading climate data, calculating indices, and analyzing extremes.
"""

import numpy as np
import pandas as pd
import xarray as xr
from geo_infer_climate import (
    ClimateDataProcessor,
    ClimateIndicesCalculator,
    ExtremeEventAnalyzer
)


def create_sample_climate_data():
    """Create sample climate dataset for demonstration."""
    time = pd.date_range('2000-01-01', periods=365, freq='D')
    lat = np.linspace(30, 50, 10)
    lon = np.linspace(-120, -100, 10)
    
    # Create realistic temperature and precipitation patterns
    temperature = 20 + 10 * np.sin(2 * np.pi * np.arange(365) / 365)[:, None, None] + np.random.randn(365, 10, 10) * 2
    precipitation = np.maximum(0, 2 + np.sin(2 * np.pi * np.arange(365) / 365)[:, None, None] + np.random.randn(365, 10, 10) * 0.5)
    
    dataset = xr.Dataset({
        'temperature': (['time', 'lat', 'lon'], temperature),
        'precipitation': (['time', 'lat', 'lon'], precipitation)
    }, coords={'time': time, 'lat': lat, 'lon': lon})
    
    return dataset


def main():
    """Run basic climate analysis example."""
    print("GEO-INFER-CLIMATE: Basic Analysis Example")
    print("=" * 50)
    
    # Create sample data
    print("\n1. Creating sample climate dataset...")
    dataset = create_sample_climate_data()
    print(f"   Dataset shape: {dataset.dims}")
    
    # Initialize processors
    print("\n2. Initializing processors...")
    data_processor = ClimateDataProcessor()
    indices_calc = ClimateIndicesCalculator()
    extreme_analyzer = ExtremeEventAnalyzer()
    
    # Validate dataset
    print("\n3. Validating dataset...")
    validation = data_processor.validate_dataset(dataset)
    print(f"   Validation results: {validation}")
    
    # Calculate SPI
    print("\n4. Calculating Standardized Precipitation Index (SPI)...")
    # Use first spatial point for simplicity
    precip_point = dataset['precipitation'].isel(lat=5, lon=5)
    spi = indices_calc.calculate_spi(precip_point, timescale=3)
    print(f"   SPI calculated: mean={spi.mean().values:.2f}, std={spi.std().values:.2f}")
    
    # Detect heatwaves
    print("\n5. Detecting heatwaves...")
    temp_point = dataset['temperature'].isel(lat=5, lon=5)
    heatwaves = extreme_analyzer.detect_heatwaves(temp_point, threshold_percentile=90.0, min_duration=3)
    print(f"   Heatwave events detected: {heatwaves['events_detected']}")
    
    # Calculate extreme indices
    print("\n6. Calculating extreme climate indices...")
    extremes = indices_calc.calculate_extreme_indices(temp_point, precip_point)
    print(f"   Hot days: {extremes['hot_days'].values}")
    print(f"   Cold days: {extremes['cold_days'].values}")
    print(f"   Max temperature: {extremes['max_temp'].values:.2f}°C")
    print(f"   Min temperature: {extremes['min_temp'].values:.2f}°C")
    
    print("\n" + "=" * 50)
    print("Analysis complete!")


if __name__ == "__main__":
    main()

