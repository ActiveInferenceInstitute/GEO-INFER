#!/usr/bin/env python3
"""
GEO-INFER-AG Example: Precision Agriculture Analysis

This example demonstrates precision agriculture workflows including
soil analysis, crop yield prediction, and sustainable farming practices.
"""

import numpy as np

from geo_infer_ag import (
    SoilAnalyzer,
    CropYieldPredictor,
    SustainabilityAnalyzer,
    SeasonalAnalyzer,
    IrrigationOptimizer
)


def main():
    print("=" * 60)
    print("GEO-INFER-AG: Precision Agriculture Analysis")
    print("=" * 60)
    
    # 1. Define Farm Data
    print("\n1. Setting Up Farm Analysis...")
    
    farm = {
        'name': 'Green Valley Farm',
        'location': {'lat': 38.5, 'lon': -121.5},
        'area_hectares': 500,
        'fields': 12,
        'primary_crop': 'wheat',
        'secondary_crops': ['corn', 'soybeans']
    }
    
    print(f"   Farm: {farm['name']}")
    print(f"   Area: {farm['area_hectares']} hectares")
    print(f"   Fields: {farm['fields']}")
    
    # 2. Soil Analysis
    print("\n2. Performing Soil Analysis...")
    
    soil_analyzer = SoilAnalyzer(
        analysis_methods=['spectral', 'chemical'],
        depth_intervals=[0, 30, 60, 100]  # cm
    )
    
    # Sample soil data for multiple fields
    soil_samples = [
        {
            'field_id': f'F{i+1}',
            'ph': np.random.uniform(6.0, 7.5),
            'nitrogen_ppm': np.random.uniform(20, 80),
            'phosphorus_ppm': np.random.uniform(15, 50),
            'potassium_ppm': np.random.uniform(100, 300),
            'organic_matter_pct': np.random.uniform(2, 6),
            'moisture_pct': np.random.uniform(15, 35)
        }
        for i in range(farm['fields'])
    ]
    
    # Analyze each field
    soil_analysis = soil_analyzer.analyze_batch(soil_samples)
    
    print("   Field Soil Health Summary:")
    for i, analysis in enumerate(soil_analysis[:3]):
        print(f"   - Field {i+1}: pH={analysis['ph']:.1f}, "
              f"N={analysis['nitrogen_ppm']:.0f}ppm, "
              f"Health Score={analysis.get('health_score', 75):.0f}/100")
    
    # Overall soil health
    avg_health = np.mean([a.get('health_score', 75) for a in soil_analysis])
    print(f"   Average soil health: {avg_health:.1f}/100")
    
    # 3. Crop Yield Prediction
    print("\n3. Predicting Crop Yields...")
    
    predictor = CropYieldPredictor(
        model_type='ensemble',
        climate_integration=True
    )
    
    # Weather forecast for growing season
    weather_forecast = {
        'avg_temperature': 22.5,
        'total_precipitation_mm': 450,
        'growing_degree_days': 2800,
        'frost_risk': 0.1
    }
    
    yield_predictions = predictor.predict(
        crop='wheat',
        soil_data=soil_analysis,
        weather=weather_forecast,
        management_practices={
            'fertilization': 'optimal',
            'pest_control': 'integrated',
            'irrigation': 'scheduled'
        }
    )
    
    print(f"   Predicted yield: {yield_predictions['yield_tonnes_per_ha']:.2f} t/ha")
    print(f"   Confidence interval: ±{yield_predictions['uncertainty_tonnes']:.2f} t/ha")
    print(f"   Total expected: {yield_predictions['total_tonnes']:.0f} tonnes")
    print(f"   Yield factors:")
    for factor, impact in yield_predictions.get('factor_impacts', {}).items():
        print(f"   - {factor}: {impact:+.1f}%")
    
    # 4. Seasonal Analysis
    print("\n4. Analyzing Seasonal Patterns...")
    
    seasonal = SeasonalAnalyzer(
        crop_type='wheat',
        climate_zone='mediterranean'
    )
    
    phenology = seasonal.analyze_phenology(
        planting_date='2024-10-15',
        weather_data=weather_forecast,
        soil_conditions={'moisture': 'adequate', 'temperature': 'optimal'}
    )
    
    print("   Phenological Stages:")
    for stage, date in phenology.get('stages', {}).items():
        print(f"   - {stage.replace('_', ' ').title()}: {date}")
    
    print(f"   Growing season length: {phenology.get('season_length_days', 0)} days")
    
    # 5. Sustainability Assessment
    print("\n5. Assessing Sustainability...")
    
    sustainability = SustainabilityAnalyzer(
        assessment_framework='global_gap',
        metrics=['carbon', 'water', 'biodiversity', 'soil']
    )
    
    sustainability_report = sustainability.assess(
        farm_data=farm,
        practices={
            'cover_crops': True,
            'crop_rotation': '3_year',
            'tillage': 'reduced',
            'pesticide_use': 'minimal',
            'organic_amendments': True,
            'renewable_energy': 0.3  # 30% renewable
        },
        inputs={
            'fertilizer_kg_per_ha': 120,
            'pesticide_applications': 2,
            'diesel_liters_per_ha': 50,
            'electricity_kwh_per_ha': 100
        }
    )
    
    print(f"   Overall sustainability score: {sustainability_report['overall_score']:.0f}/100")
    print("   Category scores:")
    for category, score in sustainability_report.get('category_scores', {}).items():
        print(f"   - {category.title()}: {score:.0f}/100")
    
    print(f"\n   Carbon footprint: {sustainability_report.get('carbon_footprint_kg_co2_per_ha', 0):.0f} kg CO2/ha")
    print(f"   Water efficiency: {sustainability_report.get('water_efficiency', 0):.1%}")
    
    # 6. Irrigation Optimization
    print("\n6. Optimizing Irrigation...")
    
    irrigation = IrrigationOptimizer(
        method='deficit_irrigation',
        sensor_integration=True
    )
    
    irrigation_schedule = irrigation.optimize(
        crop='wheat',
        growth_stage='grain_fill',
        soil_moisture_pct=22,
        forecast_precipitation_mm=5,
        evapotranspiration_mm_day=5.5,
        water_availability='adequate'
    )
    
    print(f"   Recommended irrigation: {irrigation_schedule['recommended_mm']:.0f} mm")
    print(f"   Timing: {irrigation_schedule['timing']}")
    print(f"   Water savings vs. standard: {irrigation_schedule['savings_pct']:.1f}%")
    print(f"   Efficiency rating: {irrigation_schedule['efficiency']}")
    
    # 7. Generate Recommendations
    print("\n7. Management Recommendations...")
    
    recommendations = []
    
    # Soil-based recommendations
    if avg_health < 70:
        recommendations.append("Increase organic matter through cover cropping")
    
    # Yield optimization
    if yield_predictions['yield_tonnes_per_ha'] < 4.5:
        recommendations.append("Consider optimizing fertilizer timing for higher yields")
    
    # Sustainability improvements
    if sustainability_report['overall_score'] < 80:
        recommendations.append("Transition to reduced tillage for improved carbon sequestration")
    
    # Default recommendations
    recommendations.extend([
        "Monitor soil moisture sensors for precision irrigation",
        "Implement variable rate fertilization based on soil maps",
        "Consider beneficial insect habitat strips for pest control"
    ])
    
    print("   Key Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 60)
    print("Precision Agriculture Analysis Complete!")
    print("=" * 60)
    
    # Summary
    print("\nFarm Summary:")
    print(f"  - Predicted yield: {yield_predictions['yield_tonnes_per_ha']:.2f} t/ha")
    print(f"  - Soil health: {avg_health:.0f}/100")
    print(f"  - Sustainability: {sustainability_report['overall_score']:.0f}/100")
    print(f"  - Water savings potential: {irrigation_schedule['savings_pct']:.0f}%")


if __name__ == "__main__":
    main()
