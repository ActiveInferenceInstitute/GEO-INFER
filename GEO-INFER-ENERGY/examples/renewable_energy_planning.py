#!/usr/bin/env python3
"""
GEO-INFER-ENERGY Example: Renewable Energy Development Planning

This example demonstrates comprehensive renewable energy resource assessment
including site suitability, LCOE calculation, and grid integration analysis.
"""

import numpy as np
import xarray as xr

from geo_infer_ENERGY import (
    RenewableResourceAssessor,
    RenewableType,
    SuitabilityClass,
    RenewableSite
)


def main():
    print("=" * 60)
    print("GEO-INFER-ENERGY: Renewable Energy Development Planning")
    print("=" * 60)
    
    # 1. Initialize Assessor
    print("\n1. Setting Up Renewable Resource Assessment...")
    
    assessor = RenewableResourceAssessor()
    
    region = {
        'name': 'Southwest Renewable Zone',
        'states': ['California', 'Nevada', 'Arizona'],
        'area_km2': 150000,
        'target_capacity_gw': 10
    }
    
    print(f"   Region: {region['name']}")
    print(f"   Target capacity: {region['target_capacity_gw']} GW")
    
    # 2. Assess Solar Resources
    print("\n2. Assessing Solar Resources...")
    
    # Create sample irradiance data
    irradiance = xr.DataArray(
        np.random.uniform(5.5, 7.5, (10, 10)),
        dims=['lat', 'lon'],
        coords={'lat': np.linspace(33, 36, 10), 'lon': np.linspace(-117, -114, 10)}
    )
    
    slope = xr.DataArray(np.random.uniform(0, 45, (10, 10)), dims=['lat', 'lon'])
    aspect = xr.DataArray(np.random.uniform(90, 270, (10, 10)), dims=['lat', 'lon'])
    
    solar_result = assessor.assess_solar_potential(irradiance, slope, aspect)
    
    print(f"   Average GHI: {float(irradiance.mean()):.1f} kWh/m²/day")
    print(f"   Average annual potential: {float(solar_result['solar_potential'].mean()):.0f} kWh/m²")
    print(f"   Average annual energy (20% eff.): {float(solar_result['annual_energy'].mean()):.0f} kWh/m²")
    
    # 3. Assess Wind Resources
    print("\n3. Assessing Wind Resources...")
    
    wind_speed = xr.DataArray(
        np.random.uniform(6, 10, (10, 10)),
        dims=['lat', 'lon']
    )
    
    wind_result = assessor.assess_wind_potential(wind_speed)
    
    print(f"   Average wind speed: {float(wind_speed.mean()):.1f} m/s")
    print(f"   Wind power density: {float(wind_result['wind_power'].mean()):.1f} W/m²")
    
    # 4. Site Suitability Analysis
    print("\n4. Analyzing Site Suitability...")
    
    candidate_sites = [
        {'id': 'SOL_01', 'loc': (-115.5, 34.5), 'type': RenewableType.SOLAR_PV, 'resource': 7.2, 'constraints': {}},
        {'id': 'SOL_02', 'loc': (-116.0, 35.0), 'type': RenewableType.SOLAR_PV, 'resource': 6.5, 'constraints': {'steep_slope': True}},
        {'id': 'WND_01', 'loc': (-117.5, 34.0), 'type': RenewableType.ONSHORE_WIND, 'resource': 8.5, 'constraints': {}},
        {'id': 'WND_02', 'loc': (-114.5, 33.5), 'type': RenewableType.ONSHORE_WIND, 'resource': 7.0, 'constraints': {'grid_distance_km': 75}},
        {'id': 'WND_03', 'loc': (-116.5, 35.5), 'type': RenewableType.ONSHORE_WIND, 'resource': 9.0, 'constraints': {'protected_area': True}},
    ]
    
    print("\n   Site Suitability Results:")
    print(f"   {'Site':<10} {'Type':<15} {'Resource':>10} {'Suitability':>12} {'Recommended':>12}")
    print(f"   {'-'*60}")
    
    suitable_sites = []
    for site in candidate_sites:
        result = assessor.assess_site_suitability(
            location=site['loc'],
            resource_type=site['type'],
            resource_value=site['resource'],
            constraints=site['constraints']
        )
        
        rec = "✓ Yes" if result['development_recommended'] else "✗ No"
        print(f"   {site['id']:<10} {site['type'].value:<15} {site['resource']:>10.1f} "
              f"{result['suitability_class']:>12} {rec:>12}")
        
        if result['development_recommended']:
            suitable_sites.append({**site, 'score': result['final_score']})
    
    # 5. Calculate Capacity Factors
    print("\n5. Calculating Capacity Factors...")
    
    # Simulate hourly data for one year
    hours = 8760
    
    # Solar profile (daily cycle)
    hour_of_day = np.arange(hours) % 24
    solar_irradiance = np.maximum(0, 800 * np.sin(np.pi * (hour_of_day - 6) / 12))
    solar_data = xr.DataArray(solar_irradiance, dims=['time'])
    
    solar_cf = assessor.calculate_capacity_factor(
        RenewableType.SOLAR_PV, solar_data, rated_capacity_mw=100
    )
    
    # Wind profile (random with pattern)
    wind_data = xr.DataArray(np.random.weibull(2, hours) * 8, dims=['time'])
    
    wind_cf = assessor.calculate_capacity_factor(
        RenewableType.ONSHORE_WIND, wind_data, rated_capacity_mw=100
    )
    
    print("\n   Capacity Factor Analysis:")
    print(f"   {'Resource':<15} {'Capacity Factor':>18} {'Annual Gen (GWh)':>18}")
    print(f"   {'-'*53}")
    print(f"   {'Solar PV':<15} {solar_cf['capacity_factor_pct']:>17.1f}% {solar_cf['annual_generation_gwh']:>18.1f}")
    print(f"   {'Onshore Wind':<15} {wind_cf['capacity_factor_pct']:>17.1f}% {wind_cf['annual_generation_gwh']:>18.1f}")
    
    # 6. LCOE Calculations
    print("\n6. Calculating Levelized Cost of Energy...")
    
    technologies = [
        (RenewableType.SOLAR_PV, 200, 0.25),
        (RenewableType.ONSHORE_WIND, 150, 0.35),
        (RenewableType.OFFSHORE_WIND, 300, 0.45),
        (RenewableType.HYDROPOWER, 100, 0.50),
    ]
    
    print("\n   LCOE Comparison:")
    print(f"   {'Technology':<18} {'Capacity':>10} {'CF':>8} {'LCOE ($/MWh)':>14} {'Rating':>18}")
    print(f"   {'-'*70}")
    
    for tech, capacity, cf in technologies:
        lcoe = assessor.calculate_lcoe(tech, capacity, cf)
        print(f"   {tech.value:<18} {capacity:>8} MW {cf*100:>6.0f}% ${lcoe['lcoe_usd_mwh']:>12.0f} {lcoe['competitiveness']:>18}")
    
    # 7. Storage Requirements Analysis
    print("\n7. Analyzing Storage Requirements...")
    
    # Create generation and demand profiles
    gen_profile = xr.DataArray(solar_irradiance / 800 * 500 + wind_data.values * 30, dims=['time'])
    
    demand_base = 800
    demand_pattern = demand_base + 200 * np.sin(2 * np.pi * hour_of_day / 24)
    demand_profile = xr.DataArray(demand_pattern.astype(float), dims=['time'])
    
    for penetration in [0.3, 0.5, 0.7]:
        storage = assessor.analyze_storage_requirements(
            gen_profile, demand_profile, renewable_penetration=penetration
        )
        
        print(f"\n   {penetration*100:.0f}% Renewable Penetration:")
        print(f"   - Storage power needed: {storage['recommended_storage']['power_capacity_mw']:.0f} MW")
        print(f"   - Storage energy needed: {storage['recommended_storage']['energy_capacity_mwh']:.0f} MWh")
        print(f"   - Curtailment without storage: {storage['curtailment_rate_pct']:.1f}%")
    
    # 8. Build Renewable Portfolio
    print("\n8. Building Renewable Portfolio...")
    
    portfolio_sites = [
        RenewableSite('SOL_01', 'Mojave Solar', (-115.5, 34.5), RenewableType.SOLAR_PV, 500, 0.28, 1226.4),
        RenewableSite('SOL_02', 'Ivanpah Ext.', (-115.8, 35.5), RenewableType.SOLAR_PV, 300, 0.26, 683.3),
        RenewableSite('WND_01', 'High Winds', (-117.0, 34.0), RenewableType.ONSHORE_WIND, 400, 0.38, 1331.5),
        RenewableSite('WND_02', 'Desert Wind', (-116.5, 33.5), RenewableType.ONSHORE_WIND, 250, 0.35, 766.5),
    ]
    
    for site in portfolio_sites:
        assessor.register_site(site)
    
    summary = assessor.get_portfolio_summary()
    
    print("\n   Portfolio Summary:")
    print(f"   Total sites: {summary['site_count']}")
    print(f"   Total capacity: {summary['total_capacity_mw']:.0f} MW ({summary['total_capacity_mw']/1000:.2f} GW)")
    print(f"   Annual generation: {summary['total_generation_gwh']:.1f} GWh")
    print(f"   Weighted capacity factor: {summary['weighted_capacity_factor']*100:.1f}%")
    
    print("\n   By Resource Type:")
    for rtype, data in summary['by_resource_type'].items():
        print(f"   - {rtype}: {data['count']} sites, {data['capacity_mw']:.0f} MW, {data['generation_gwh']:.1f} GWh")
    
    print("\n" + "=" * 60)
    print("Renewable Energy Planning Complete!")
    print("=" * 60)
    
    # Summary
    print("\nKey Findings:")
    print(f"  - Suitable sites identified: {len(suitable_sites)}")
    print(f"  - Solar PV capacity factor: {solar_cf['capacity_factor_pct']:.1f}%")
    print(f"  - Wind capacity factor: {wind_cf['capacity_factor_pct']:.1f}%")
    print(f"  - Portfolio capacity: {summary['total_capacity_mw']/1000:.2f} GW")
    print(f"  - Annual generation: {summary['total_generation_gwh']:.0f} GWh")


if __name__ == "__main__":
    main()
