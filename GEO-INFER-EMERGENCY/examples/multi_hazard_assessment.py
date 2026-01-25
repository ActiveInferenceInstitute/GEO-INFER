#!/usr/bin/env python3
"""
GEO-INFER-EMERGENCY Example: Multi-Hazard Risk Assessment

This example demonstrates comprehensive multi-hazard risk assessment
including hazard modeling, vulnerability analysis, and impact prediction.
"""

from geo_infer_emergency import (
    HazardAssessment,
    VulnerabilityAnalyzer,
    ImpactPredictor,
    EarlyWarningSystem,
    RiskMapper
)


def main():
    print("=" * 60)
    print("GEO-INFER-EMERGENCY: Multi-Hazard Risk Assessment")
    print("=" * 60)
    
    # 1. Define Study Area and Hazards
    print("\n1. Setting Up Multi-Hazard Analysis...")
    
    study_area = {
        'name': 'Coastal Region A',
        'bbox': [-118.5, 33.7, -117.8, 34.3],  # [minlon, minlat, maxlon, maxlat]
        'population': 2500000,
        'critical_infrastructure': 150
    }
    
    hazards = ['earthquake', 'flood', 'wildfire', 'tsunami', 'landslide']
    
    print(f"   Study area: {study_area['name']}")
    print(f"   Population: {study_area['population']:,}")
    print(f"   Hazards: {', '.join(hazards)}")
    
    # 2. Hazard Assessment
    print("\n2. Performing Hazard Assessment...")
    hazard_analyzer = HazardAssessment(
        hazard_types=hazards,
        return_periods=[50, 100, 250, 500],
        modeling_method='probabilistic'
    )
    
    hazard_results = {}
    for hazard in hazards:
        result = hazard_analyzer.assess_hazard(
            hazard_type=hazard,
            region=study_area,
            return_period=100,
            include_uncertainty=True
        )
        hazard_results[hazard] = result
        print(f"   {hazard.title()}: Intensity={result.get('max_intensity', 0):.2f}, "
              f"Probability={result.get('annual_probability', 0):.4f}")
    
    # 3. Vulnerability Analysis
    print("\n3. Analyzing Vulnerability...")
    vulnerability = VulnerabilityAnalyzer(
        exposure_categories=['population', 'buildings', 'infrastructure', 'economy'],
        vulnerability_method='multi_criteria'
    )
    
    vuln_results = vulnerability.analyze(
        region=study_area,
        exposure_data={
            'population': {'total': 2500000, 'vulnerable_pct': 0.25},
            'buildings': {'count': 500000, 'avg_age': 35},
            'infrastructure': {'count': 150, 'criticality': 'high'},
            'economy': {'gdp_millions': 120000}
        },
        hazard_results=hazard_results
    )
    
    print(f"   Population vulnerability index: {vuln_results.get('population_vuln', 0):.2f}")
    print(f"   Infrastructure vulnerability: {vuln_results.get('infra_vuln', 0):.2f}")
    print(f"   Overall vulnerability score: {vuln_results.get('overall_score', 0):.2f}")
    
    # 4. Impact Prediction
    print("\n4. Predicting Impacts...")
    predictor = ImpactPredictor(
        impact_categories=['casualties', 'displacement', 'economic_loss', 'infrastructure_damage'],
        prediction_method='scenario_based'
    )
    
    # Predict impacts for multi-hazard scenario
    impact = predictor.predict(
        hazard_scenario={
            'primary_hazard': 'earthquake',
            'magnitude': 7.2,
            'secondary_hazards': ['landslide', 'fire'],
            'cascading_effects': True
        },
        vulnerability=vuln_results,
        exposure=study_area
    )
    
    print(f"   Estimated casualties: {impact.get('casualties', {}).get('estimate', 0):,}")
    print(f"   Displaced population: {impact.get('displacement', {}).get('estimate', 0):,}")
    print(f"   Economic loss: ${impact.get('economic_loss', {}).get('estimate_millions', 0):,.0f}M")
    print(f"   Infrastructure damage: {impact.get('infrastructure_damage', {}).get('pct', 0):.1f}%")
    
    # 5. Early Warning System
    print("\n5. Configuring Early Warning System...")
    ews = EarlyWarningSystem(
        hazards=hazards,
        alert_levels=['advisory', 'watch', 'warning', 'emergency'],
        notification_channels=['sms', 'email', 'broadcast', 'sirens']
    )
    
    # Set up monitoring
    monitoring = ews.configure_monitoring(
        region=study_area,
        sensors={
            'seismic': 25,
            'water_level': 40,
            'weather_stations': 30,
            'camera_systems': 15
        },
        update_interval_seconds=60
    )
    
    print(f"   Sensors configured: {sum(monitoring.get('sensors', {}).values())}")
    print(f"   Alert thresholds set: {monitoring.get('thresholds_configured', False)}")
    
    # Simulate alert
    alert = ews.generate_alert(
        hazard_type='flood',
        alert_level='watch',
        affected_zones=['zone_1', 'zone_2'],
        message='Elevated river levels expected. Prepare for potential evacuation.'
    )
    
    print(f"   Alert generated: {alert.get('alert_id', 'N/A')}")
    print(f"   Level: {alert.get('level', 'N/A')}")
    
    # 6. Risk Mapping
    print("\n6. Generating Risk Maps...")
    mapper = RiskMapper(
        map_types=['hazard', 'vulnerability', 'exposure', 'risk'],
        output_format='geojson'
    )
    
    risk_map = mapper.generate_composite_risk_map(
        region=study_area,
        hazard_results=hazard_results,
        vulnerability=vuln_results,
        resolution_km=1.0
    )
    
    print(f"   Risk zones identified: {risk_map.get('zone_count', 0)}")
    print(f"   High-risk areas: {risk_map.get('high_risk_pct', 0):.1f}%")
    print(f"   Map layers: {len(risk_map.get('layers', []))}")
    
    # Save risk report
    print("\n7. Generating Risk Report...")
    print(f"   Report includes: hazard assessment, vulnerability analysis, impact prediction")
    
    print("\n" + "=" * 60)
    print("Multi-Hazard Risk Assessment Complete!")
    print("=" * 60)
    
    # Summary Statistics
    print("\nRisk Summary:")
    print(f"  - Study Area: {study_area['name']}")
    print(f"  - Population at Risk: {vuln_results.get('population_at_risk', 0):,}")
    print(f"  - Overall Risk Score: {vuln_results.get('overall_score', 0):.2f}/10")
    print(f"  - Highest Risk Hazard: {max(hazard_results.items(), key=lambda x: x[1].get('risk_score', 0))[0].title()}")


if __name__ == "__main__":
    main()
