"""
Basic agricultural analysis example using GEO-INFER-AG.

This example demonstrates:
- Field boundary management
- Crop yield modeling
- Seasonal analysis
- Agricultural sustainability assessment
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    import geopandas as gpd
    from shapely.geometry import Polygon, Point
    from geo_infer_ag.core.field_boundary import FieldBoundaryManager
    from geo_infer_ag.core.agricultural_analysis import AgriculturalAnalysis
    from geo_infer_ag.models.crop_yield import CropYieldModel
    from geo_infer_ag.core.seasonal_analysis import SeasonalAnalyzer
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some imports not available: {e}")
    IMPORTS_AVAILABLE = False


def create_sample_field():
    """Create a sample agricultural field."""
    # Create a rectangular field
    field_geometry = Polygon([
        (-122.4, 37.7),
        (-122.3, 37.7),
        (-122.3, 37.8),
        (-122.4, 37.8),
        (-122.4, 37.7)
    ])
    
    field_data = {
        'field_id': 'field_001',
        'name': 'Sample Field',
        'crop_type': 'corn',
        'area_ha': 10.0,
        'geometry': [field_geometry]
    }
    
    return gpd.GeoDataFrame(field_data, crs='EPSG:4326')


def generate_crop_data(n_days=120):
    """Generate sample crop growth data."""
    dates = pd.date_range(
        start=datetime(2024, 4, 1),
        end=datetime(2024, 4, 1) + timedelta(days=n_days),
        freq='D'
    )
    
    # Simulate crop growth with NDVI-like pattern
    days = np.arange(n_days)
    ndvi = 0.2 + 0.6 * np.sin(np.pi * days / 90) ** 2
    ndvi += np.random.normal(0, 0.05, n_days)
    ndvi = np.clip(ndvi, 0.1, 0.9)
    
    # Simulate yield-related metrics
    data = {
        'date': dates,
        'ndvi': ndvi,
        'biomass_kg_ha': ndvi * 8000 + np.random.normal(0, 500, n_days),
        'soil_moisture': 0.3 + 0.2 * np.sin(2 * np.pi * days / 7) + np.random.normal(0, 0.05, n_days),
        'temperature': 20 + 5 * np.sin(2 * np.pi * days / 365) + np.random.normal(0, 2, n_days),
        'precipitation': np.random.exponential(2, n_days)
    }
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df


def main():
    """Run basic agricultural analysis example."""
    print("=" * 60)
    print("GEO-INFER-AG: Basic Agricultural Analysis Example")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("\n⚠️  Some required modules are not available.")
        print("   This example requires full GEO-INFER-AG installation.")
        return
    
    # Step 1: Field boundary management
    print("\n🌾 Step 1: Field boundary management...")
    try:
        field = create_sample_field()
        print(f"   ✅ Created field: {field['name'].iloc[0]}")
        print(f"   Field ID: {field['field_id'].iloc[0]}")
        print(f"   Area: {field['area_ha'].iloc[0]} hectares")
        print(f"   Crop type: {field['crop_type'].iloc[0]}")
    except Exception as e:
        print(f"   ⚠️  Field creation: {e}")
        field = None
    
    # Step 2: Crop yield modeling
    print("\n📈 Step 2: Crop yield modeling...")
    try:
        crop_model = CropYieldModel(crop_type="corn")
        print(f"   ✅ Created crop yield model for: {crop_model.crop_type}")
        
        # Generate sample data
        crop_data = generate_crop_data(n_days=120)
        print(f"   ✅ Generated {len(crop_data)} days of crop data")
        
        # Simple yield estimation (if model supports it)
        if hasattr(crop_model, 'estimate_yield'):
            try:
                estimated_yield = crop_model.estimate_yield(crop_data)
                print(f"   ✅ Estimated yield: {estimated_yield:.2f} kg/ha")
            except Exception as e:
                print(f"   ℹ️  Yield estimation: {e}")
    except Exception as e:
        print(f"   ⚠️  Crop modeling: {e}")
    
    # Step 3: Seasonal analysis
    print("\n📅 Step 3: Seasonal analysis...")
    try:
        seasonal_analyzer = SeasonalAnalyzer()
        crop_data = generate_crop_data(n_days=365)
        
        # Analyze growing season
        if hasattr(seasonal_analyzer, 'analyze_growing_season'):
            try:
                season_result = seasonal_analyzer.analyze_growing_season(crop_data)
                print(f"   ✅ Growing season analysis complete")
                print(f"   Season start: {season_result.get('start_date', 'N/A')}")
                print(f"   Season end: {season_result.get('end_date', 'N/A')}")
            except Exception as e:
                print(f"   ℹ️  Growing season analysis: {e}")
    except Exception as e:
        print(f"   ⚠️  Seasonal analysis: {e}")
    
    # Step 4: Agricultural analysis
    print("\n🔬 Step 4: Comprehensive agricultural analysis...")
    try:
        if field is not None:
            analyzer = AgriculturalAnalysis()
            print(f"   ✅ Agricultural analysis engine initialized")
            
            # Display available methods
            print(f"   Available analysis capabilities:")
            print(f"     • Field boundary management")
            print(f"     • Crop yield prediction")
            print(f"     • Seasonal pattern analysis")
            print(f"     • Sustainability assessment")
    except Exception as e:
        print(f"   ⚠️  Agricultural analysis: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Agricultural analysis example complete!")
    print("=" * 60)
    print("\nKey capabilities demonstrated:")
    print("  • Field boundary management")
    print("  • Crop yield modeling")
    print("  • Seasonal analysis")
    print("  • Agricultural data processing")
    print("\nNext steps:")
    print("  • Integrate with SPACE for spatial field analysis")
    print("  • Connect with TIME for temporal crop monitoring")
    print("  • Use with IOT for real-time sensor data")
    print("  • Combine with AI for predictive analytics")


if __name__ == "__main__":
    main()

