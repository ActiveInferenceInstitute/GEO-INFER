#!/usr/bin/env python3
"""
GEO-INFER-FOREST Example: Wildfire Risk Management

This example demonstrates comprehensive wildfire risk assessment including
fire weather analysis, spread modeling, suppression planning, and damage assessment.
"""

import numpy as np
import xarray as xr

from geo_infer_forest import (
    WildfireRiskAnalyzer,
    FireDangerRating,
    FuelType,
    FireWeatherObservation,
    FireIncident,
)


def main():
    print("=" * 60)
    print("GEO-INFER-FOREST: Wildfire Risk Management")
    print("=" * 60)

    # 1. Initialize Wildfire Risk Analyzer
    print("\n1. Setting Up Wildfire Risk Analysis...")

    analyzer = WildfireRiskAnalyzer()

    region = {
        "name": "Sierra Nevada Foothills",
        "area_km2": 5000,
        "dominant_fuel": "Mixed Chaparral",
        "fire_season": "May - October",
    }

    print(f"   Region: {region['name']}")
    print(f"   Area: {region['area_km2']:,} km²")
    print(f"   Dominant fuel: {region['dominant_fuel']}")

    # 2. Analyze Fire Weather
    print("\n2. Analyzing Fire Weather Conditions...")

    weather_stations = [
        FireWeatherObservation(
            observation_id="FW_001",
            location=(-120.5, 38.5),
            timestamp="2024-08-15T14:00:00",
            temperature_c=38.0,
            relative_humidity=12.0,
            wind_speed_kmh=35.0,
            wind_direction_deg=270,
            precipitation_mm=0.0,
        ),
        FireWeatherObservation(
            observation_id="FW_002",
            location=(-120.7, 38.7),
            timestamp="2024-08-15T14:00:00",
            temperature_c=35.0,
            relative_humidity=18.0,
            wind_speed_kmh=25.0,
            wind_direction_deg=290,
            precipitation_mm=0.0,
        ),
        FireWeatherObservation(
            observation_id="FW_003",
            location=(-120.3, 38.3),
            timestamp="2024-08-15T14:00:00",
            temperature_c=40.0,
            relative_humidity=8.0,
            wind_speed_kmh=45.0,
            wind_direction_deg=250,
            precipitation_mm=0.0,
        ),
    ]

    print("\n   Station Fire Weather Analysis:")
    print(
        f"   {'Station':<12} {'Temp':>8} {'RH':>6} {'Wind':>8} {'FWI':>8} {'Rating':>12}"
    )
    print(f"   {'-'*56}")

    fwi_results = []
    for obs in weather_stations:
        fwi = analyzer.calculate_fire_weather_index(obs)
        fwi_results.append(fwi)
        print(
            f"   {obs.observation_id:<12} {obs.temperature_c:>6.0f}°C {obs.relative_humidity:>5.0f}% "
            f"{obs.wind_speed_kmh:>6.0f}km/h {fwi['fwi']:>8.1f} {fwi['danger_rating']:>12}"
        )

    max_fwi = max(fwi_results, key=lambda x: x["fwi"])
    print(
        f"\n   Highest FWI: {max_fwi['fwi']:.1f} at station {max_fwi['observation_id']}"
    )
    print(f"   Regional Danger Rating: {max_fwi['danger_rating'].upper()}")

    # 3. Model Fire Perimeter Growth
    print("\n3. Modeling Fire Spread Scenarios...")

    scenarios = [
        {"fuel": FuelType.GRASS, "wind": 15, "slope": 5, "time": 2},
        {"fuel": FuelType.SHRUB, "wind": 25, "slope": 15, "time": 4},
        {"fuel": FuelType.TIMBER_UNDERSTORY, "wind": 35, "slope": 25, "time": 8},
    ]

    print("\n   Fire Growth Scenarios (from ignition point):")
    print(f"   {'Fuel Type':<22} {'Wind':>8} {'Slope':>8} {'Time':>8} {'Area':>10}")
    print(f"   {'-'*60}")

    for scenario in scenarios:
        perimeter = analyzer.model_fire_perimeter(
            ignition_point=(-120.5, 38.5),
            fuel_type=scenario["fuel"],
            wind_speed_kmh=scenario["wind"],
            wind_direction_deg=270,
            slope_pct=scenario["slope"],
            time_hours=scenario["time"],
        )

        print(
            f"   {scenario['fuel'].value:<22} {scenario['wind']:>6} km/h {scenario['slope']:>6}% "
            f"{scenario['time']:>6} hrs {perimeter['area_hectares']:>8.0f} ha"
        )

    # Detailed spread analysis for critical scenario
    print("\n   Detailed Spread Analysis (Critical Scenario):")
    critical = analyzer.model_fire_perimeter(
        ignition_point=(-120.5, 38.5),
        fuel_type=FuelType.SHRUB,
        wind_speed_kmh=35,
        wind_direction_deg=270,
        slope_pct=20,
        time_hours=6,
    )

    print(f"   Head fire rate: {critical['spread_rates']['head_m_per_min']:.1f} m/min")
    print(
        f"   Backing fire rate: {critical['spread_rates']['back_m_per_min']:.1f} m/min"
    )
    print(f"   Head fire run: {critical['distances']['head_m']/1000:.2f} km")
    print(f"   Area burned: {critical['area_hectares']:.0f} hectares")
    print(f"   Perimeter length: {critical['perimeter_length_km']:.1f} km")

    # 4. Plan Suppression Resources
    print("\n4. Planning Suppression Resources...")

    fire_sizes = [50, 200, 1000]

    for size in fire_sizes:
        danger = FireDangerRating.VERY_HIGH if size > 500 else FireDangerRating.HIGH

        resources = analyzer.plan_suppression_resources(
            fire_size_ha=size, danger_rating=danger, terrain_difficulty="moderate"
        )

        print(f"\n   {size}-hectare fire ({danger.value} danger):")
        print(
            f"   Personnel: {resources['personnel']['firefighters_needed']} firefighters "
            f"({resources['personnel']['crews_20_person']} crews)"
        )
        print(
            f"   Equipment: {resources['equipment']['engines']} engines, "
            f"{resources['equipment']['helicopters']} helicopters, "
            f"{resources['equipment']['airtankers']} airtankers"
        )
        print(
            f"   Est. containment: {resources['timeline']['estimated_containment_days']} days"
        )
        print(f"   Est. cost: ${resources['estimated_cost_usd']:,}")

    # 5. Calculate Evacuation Zones
    print("\n5. Calculating Evacuation Zones...")

    evac = analyzer.calculate_evacuation_zones(
        fire_location=(-120.5, 38.5), predicted_spread_km=5.0, wind_direction_deg=270
    )

    print("\n   Zone Recommendations:")
    for zone_name, zone_data in evac["zones"].items():
        print(f"\n   {zone_name.replace('_', ' ').upper()}:")
        print(f"   - Radius: {zone_data['radius_km']:.1f} km")
        print(f"   - Downwind extension: {zone_data['downwind_extension_km']:.1f} km")
        print(f"   - Priority: {zone_data['priority']}")
        print(f"   - Action: {zone_data['recommended_action']}")

    # 6. Post-Fire Damage Assessment
    print("\n6. Assessing Post-Fire Damage...")

    # Simulate pre/post NDVI
    np.random.seed(42)
    pre_ndvi = xr.DataArray(0.6 + np.random.uniform(0, 0.3, (20, 20)), dims=["y", "x"])

    # Simulate fire damage (central area burned)
    post_ndvi = pre_ndvi.copy()
    post_ndvi[5:15, 5:15] = pre_ndvi[5:15, 5:15] - np.random.uniform(0.2, 0.6, (10, 10))
    post_ndvi = xr.where(post_ndvi < 0, 0, post_ndvi)

    damage = analyzer.assess_post_fire_damage(pre_ndvi, post_ndvi)

    print("   Burn Severity Analysis:")
    print(f"   - Unburned: {damage.attrs['unburned_pct']:.1f}%")
    print(f"   - Low severity: {damage.attrs['low_severity_pct']:.1f}%")
    print(f"   - Moderate severity: {damage.attrs['moderate_severity_pct']:.1f}%")
    print(f"   - High severity: {damage.attrs['high_severity_pct']:.1f}%")
    print(f"   - Total burned: {damage.attrs['total_burned_pct']:.1f}%")

    # 7. Register Active Incidents
    print("\n7. Tracking Active Incidents...")

    incidents = [
        FireIncident(
            incident_id="CA-SRF-001",
            name="Mountain View Fire",
            location=(-120.5, 38.5),
            start_time="2024-08-15T09:30:00",
            area_hectares=450,
            containment_pct=25,
            cause="lightning",
            fuel_type=FuelType.SHRUB,
        ),
        FireIncident(
            incident_id="CA-SRF-002",
            name="Canyon Complex",
            location=(-120.8, 38.3),
            start_time="2024-08-14T14:00:00",
            area_hectares=1200,
            containment_pct=45,
            cause="power_line",
            fuel_type=FuelType.TIMBER_UNDERSTORY,
        ),
    ]

    for incident in incidents:
        analyzer.register_incident(incident)

    print("\n   Active Incidents:")
    print(f"   {'ID':<15} {'Name':<20} {'Area':>8} {'Containment':>12}")
    print(f"   {'-'*58}")

    for incident in analyzer.get_active_incidents():
        print(
            f"   {incident.incident_id:<15} {incident.name:<20} "
            f"{incident.area_hectares:>6.0f} ha {incident.containment_pct:>10.0f}%"
        )

    print("\n" + "=" * 60)
    print("Wildfire Risk Management Analysis Complete!")
    print("=" * 60)

    # Summary
    print("\nKey Findings:")
    print(f"  - Regional danger rating: {max_fwi['danger_rating'].upper()}")
    print(f"  - Critical scenario: {critical['area_hectares']:.0f} ha in 6 hours")
    print(f"  - Active incidents: {len(analyzer.get_active_incidents())}")
    print(f"  - Total area burned: {sum(i.area_hectares for i in incidents):.0f} ha")


if __name__ == "__main__":
    main()
