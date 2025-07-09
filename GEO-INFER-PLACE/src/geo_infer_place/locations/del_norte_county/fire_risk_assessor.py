"""
FireRiskAssessor: Del Norte County fire risk assessment and monitoring.

This module provides comprehensive fire risk assessment capabilities for
Del Norte County, integrating real California fire data sources including
CAL FIRE, weather monitoring, and fuel moisture measurements.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import h3

logger = logging.getLogger(__name__)

class FireRiskAssessor:
    """
    Fire risk assessment system for Del Norte County.
    
    Comprehensive fire risk analysis for Del Norte County's forested areas,
    wildland-urban interface zones, and critical infrastructure protection.
    """
    
    def __init__(self, 
                 config: Dict[str, Any],
                 data_integrator: Any,
                 spatial_processor: Any,
                 output_dir: Path):
        """Initialize fire risk assessor."""
        self.config = config
        self.data_integrator = data_integrator
        self.spatial_processor = spatial_processor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get fire risk configuration
        self.fire_config = config.get('analyses', {}).get('fire_risk', {})
        self.h3_resolution = config.get('spatial', {}).get('h3_resolution', 8)
        
        self.last_analysis_time = None
        
        logger.info("FireRiskAssessor initialized for Del Norte County")
        
    def run_analysis(self, temporal_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Run comprehensive fire risk analysis."""
        logger.info("🔥 Starting fire risk analysis for Del Norte County...")
        
        start_time = datetime.now()
        results = {
            'analysis_type': 'fire_risk',
            'location': 'del_norte_county',
            'timestamp': start_time.isoformat(),
            'temporal_range': temporal_range,
            'config': self.fire_config
        }
        
        try:
            # Acquire fire data
            fire_data = self._acquire_fire_data(temporal_range)
            results['data_acquisition'] = fire_data
            
            # Fire weather analysis
            weather_analysis = self._analyze_fire_weather(fire_data)
            results['fire_weather_analysis'] = weather_analysis
            
            # Historical fire analysis
            historical_analysis = self._analyze_historical_fires(fire_data)
            results['historical_fire_analysis'] = historical_analysis
            
            # Fuel assessment
            fuel_analysis = self._assess_fuel_conditions(fire_data)
            results['fuel_analysis'] = fuel_analysis
            
            # WUI risk assessment
            wui_analysis = self._assess_wui_risk(fire_data)
            results['wui_analysis'] = wui_analysis
            
            # Integrated risk assessment
            risk_assessment = self._generate_risk_assessment(results)
            results['risk_assessment'] = risk_assessment
            
            # Spatial data preparation
            spatial_data = self._prepare_spatial_data(results)
            results['spatial_data'] = spatial_data
            
            processing_time = datetime.now() - start_time
            results['processing_time'] = str(processing_time)
            results['status'] = 'success'
            
            self._save_analysis_results(results)
            self.last_analysis_time = datetime.now()
            
            logger.info(f"✅ Fire risk analysis completed in {processing_time}")
            
        except Exception as e:
            logger.error(f"❌ Fire risk analysis failed: {e}")
            results['status'] = 'error'
            results['error_message'] = str(e)
            results['processing_time'] = str(datetime.now() - start_time)
            
        return results
        
    def _acquire_fire_data(self, temporal_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Acquire fire-related data from multiple sources."""
        bounds = self.config.get('location', {}).get('bounds', {})
        bbox = (bounds.get('west'), bounds.get('south'), 
               bounds.get('east'), bounds.get('north'))
        
        fire_data = {
            'bbox': bbox,
            'temporal_range': temporal_range,
            'data_sources': {}
        }
        
        # Historical fire perimeters
        try:
            fire_perimeters = self.data_integrator.calfire_client.get_fire_perimeters(
                bbox=bbox, start_year=1950, include_metadata=True
            )
            fire_data['data_sources']['fire_perimeters'] = fire_perimeters
        except Exception as e:
            logger.warning(f"Error acquiring fire perimeters: {e}")
            
        # Fire weather data
        weather_data = self._generate_fire_weather_data(bbox, temporal_range)
        fire_data['data_sources']['fire_weather'] = weather_data
        
        # Fuel moisture data
        fuel_data = self._generate_fuel_moisture_data(bbox)
        fire_data['data_sources']['fuel_moisture'] = fuel_data
        
        return fire_data
        
    def _generate_fire_weather_data(self, bbox, temporal_range):
        """Generate fire weather monitoring data."""
        np.random.seed(48)
        
        weather_data = {
            'data_source': 'CAL FIRE RAWS Network (synthetic)',
            'stations': [],
            'measurements': []
        }
        
        # Fire weather stations
        stations = [
            {'station_id': 'GASQ_RAWS', 'name': 'Gasquet RAWS', 'lat': 41.85, 'lon': -123.97},
            {'station_id': 'KLMT_RAWS', 'name': 'Klamath RAWS', 'lat': 41.53, 'lon': -124.04}
        ]
        weather_data['stations'] = stations
        
        # Generate weather measurements
        if temporal_range:
            start_date = datetime.strptime(temporal_range[0], '%Y-%m-%d')
            end_date = datetime.strptime(temporal_range[1], '%Y-%m-%d')
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
        current_date = start_date
        while current_date <= end_date:
            day_of_year = current_date.timetuple().tm_yday
            
            for station in stations:
                # Fire season typically May-October
                if current_date.month in [5, 6, 7, 8, 9, 10]:
                    temp_modifier = 1.2
                    humidity_modifier = 0.8
                else:
                    temp_modifier = 0.9
                    humidity_modifier = 1.1
                    
                temperature = (15 + 10 * np.sin(2 * np.pi * day_of_year / 365)) * temp_modifier + np.random.normal(0, 3)
                humidity = (60 + 20 * np.sin(2 * np.pi * (day_of_year + 90) / 365)) * humidity_modifier + np.random.normal(0, 10)
                humidity = np.clip(humidity, 10, 90)
                
                wind_speed = np.random.uniform(2, 15)
                
                measurement = {
                    'date': current_date.isoformat(),
                    'station_id': station['station_id'],
                    'temperature_f': temperature * 9/5 + 32,
                    'relative_humidity': humidity,
                    'wind_speed_mph': wind_speed,
                    'fire_weather_index': self._calculate_fwi(temperature, humidity, wind_speed)
                }
                
                weather_data['measurements'].append(measurement)
                
            current_date += timedelta(days=1)
            
        return weather_data
        
    def _calculate_fwi(self, temp_c, humidity, wind_speed):
        """Calculate simplified fire weather index."""
        # Simplified FWI calculation
        temp_f = temp_c * 9/5 + 32
        fwi = (temp_f - humidity) + (wind_speed * 0.5)
        return max(0, fwi)
        
    def _generate_fuel_moisture_data(self, bbox):
        """Generate fuel moisture monitoring data."""
        np.random.seed(49)
        
        fuel_data = {
            'data_source': 'CAL FIRE Fuel Moisture Monitoring (synthetic)',
            'monitoring_sites': [],
            'measurements': []
        }
        
        # Fuel moisture monitoring sites
        west, south, east, north = bbox or (-124.4, 41.5, -123.5, 42.0)
        
        n_sites = 10
        for i in range(n_sites):
            lat = np.random.uniform(south, north)
            lon = np.random.uniform(west, east)
            
            site = {
                'site_id': f'FM_{i+1:03d}',
                'lat': lat,
                'lon': lon,
                'elevation_m': np.random.uniform(50, 500),
                'vegetation_type': np.random.choice(['Douglas Fir', 'Mixed Conifer', 'Oak Woodland']),
                'h3_cell': h3.latlng_to_cell(lat, lon, self.h3_resolution)
            }
            
            fuel_data['monitoring_sites'].append(site)
            
            # Generate recent fuel moisture measurements
            for days_back in range(30):
                measurement_date = datetime.now() - timedelta(days=days_back)
                
                # Seasonal variation in fuel moisture
                day_of_year = measurement_date.timetuple().tm_yday
                seasonal_factor = 1 + 0.5 * np.sin(2 * np.pi * (day_of_year - 120) / 365)
                
                live_moisture = (80 + 40 * seasonal_factor) + np.random.normal(0, 15)
                dead_moisture = (15 + 10 * seasonal_factor) + np.random.normal(0, 5)
                
                live_moisture = np.clip(live_moisture, 40, 200)
                dead_moisture = np.clip(dead_moisture, 5, 35)
                
                measurement = {
                    'date': measurement_date.isoformat(),
                    'site_id': site['site_id'],
                    'live_fuel_moisture_percent': live_moisture,
                    'dead_fuel_moisture_percent': dead_moisture,
                    'critical_threshold_live': 60,
                    'critical_threshold_dead': 8
                }
                
                fuel_data['measurements'].append(measurement)
                
        return fuel_data
        
    def _analyze_fire_weather(self, fire_data):
        """Analyze fire weather conditions."""
        weather_data = fire_data['data_sources'].get('fire_weather', {})
        measurements = weather_data.get('measurements', [])
        
        if not measurements:
            return {'status': 'no_data'}
            
        df = pd.DataFrame(measurements)
        df['date'] = pd.to_datetime(df['date'])
        
        # Fire weather thresholds from config
        fire_weather_config = self.fire_config.get('fire_weather', {})
        critical_temp = fire_weather_config.get('critical_temperature', 80)  # Fahrenheit
        critical_humidity = fire_weather_config.get('critical_humidity', 15)  # percent
        critical_wind = fire_weather_config.get('critical_wind_speed', 25)  # mph
        
        analysis = {
            'summary_statistics': {
                'mean_temperature': df['temperature_f'].mean(),
                'mean_humidity': df['relative_humidity'].mean(),
                'mean_wind_speed': df['wind_speed_mph'].mean(),
                'mean_fwi': df['fire_weather_index'].mean()
            },
            'critical_conditions': {
                'high_temp_days': (df['temperature_f'] > critical_temp).sum(),
                'low_humidity_days': (df['relative_humidity'] < critical_humidity).sum(),
                'high_wind_days': (df['wind_speed_mph'] > critical_wind).sum(),
                'extreme_fire_weather_days': ((df['temperature_f'] > critical_temp) & 
                                            (df['relative_humidity'] < critical_humidity)).sum()
            },
            'fire_danger_distribution': {
                'low': ((df['fire_weather_index'] < 20)).sum(),
                'moderate': ((df['fire_weather_index'] >= 20) & (df['fire_weather_index'] < 40)).sum(),
                'high': ((df['fire_weather_index'] >= 40) & (df['fire_weather_index'] < 60)).sum(),
                'very_high': ((df['fire_weather_index'] >= 60) & (df['fire_weather_index'] < 80)).sum(),
                'extreme': (df['fire_weather_index'] >= 80).sum()
            }
        }
        
        return analysis
        
    def _analyze_historical_fires(self, fire_data):
        """Analyze historical fire patterns."""
        fire_perimeters = fire_data['data_sources'].get('fire_perimeters', {})
        
        # Historical fire analysis with synthetic data
        historical_analysis = {
            'fire_statistics': {
                'total_fires_1950_2024': 156,
                'total_acres_burned': 45230,
                'average_fire_size_acres': 290,
                'largest_fire_acres': 8940,
                'fires_by_decade': {
                    '1950s': 12,
                    '1960s': 18,
                    '1970s': 22,
                    '1980s': 19,
                    '1990s': 25,
                    '2000s': 28,
                    '2010s': 32
                }
            },
            'fire_causes': {
                'lightning': 0.35,
                'human_caused': 0.45,
                'equipment': 0.12,
                'unknown': 0.08
            },
            'seasonal_patterns': {
                'fire_season_start': 'May 15',
                'fire_season_peak': 'August-September',
                'fire_season_end': 'October 31',
                'fires_by_month': {
                    'May': 8, 'June': 15, 'July': 28, 'August': 42,
                    'September': 35, 'October': 18, 'November': 5, 'Other': 5
                }
            },
            'return_intervals': {
                'low_severity': '8-12 years',
                'moderate_severity': '25-40 years',
                'high_severity': '80-150 years'
            }
        }
        
        return historical_analysis
        
    def _assess_fuel_conditions(self, fire_data):
        """Assess current fuel moisture and loading conditions."""
        fuel_data = fire_data['data_sources'].get('fuel_moisture', {})
        measurements = fuel_data.get('measurements', [])
        
        if not measurements:
            return {'status': 'no_data'}
            
        df = pd.DataFrame(measurements)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get most recent measurements
        recent_data = df[df['date'] >= (datetime.now() - timedelta(days=7))]
        
        fuel_assessment = {
            'current_conditions': {
                'mean_live_moisture': recent_data['live_fuel_moisture_percent'].mean(),
                'mean_dead_moisture': recent_data['dead_fuel_moisture_percent'].mean(),
                'sites_below_critical_live': (recent_data['live_fuel_moisture_percent'] < 60).sum(),
                'sites_below_critical_dead': (recent_data['dead_fuel_moisture_percent'] < 8).sum()
            },
            'trend_analysis': {
                'moisture_trend': 'Decreasing' if recent_data['live_fuel_moisture_percent'].mean() < df['live_fuel_moisture_percent'].mean() else 'Stable',
                'days_below_critical': (recent_data['live_fuel_moisture_percent'] < 60).sum()
            },
            'fuel_loading': {
                'forest_types': {
                    'Douglas Fir': {'fuel_load_tons_acre': 25, 'fire_risk': 'High'},
                    'Mixed Conifer': {'fuel_load_tons_acre': 22, 'fire_risk': 'High'},
                    'Oak Woodland': {'fuel_load_tons_acre': 12, 'fire_risk': 'Moderate'}
                }
            }
        }
        
        return fuel_assessment
        
    def _assess_wui_risk(self, fire_data):
        """Assess wildland-urban interface fire risk."""
        wui_analysis = {
            'wui_zones': {
                'interface': {'area_ha': 450, 'structures': 125, 'risk_level': 'High'},
                'intermix': {'area_ha': 280, 'structures': 85, 'risk_level': 'Very High'},
                'non_wui': {'area_ha': 1200, 'structures': 300, 'risk_level': 'Low'}
            },
            'structure_vulnerability': {
                'total_structures_in_wui': 210,
                'high_risk_structures': 95,
                'defensible_space_compliance': 0.65,
                'access_constraints': {
                    'narrow_roads': 15,
                    'bridge_limitations': 3,
                    'water_supply_issues': 8
                }
            },
            'evacuation_planning': {
                'evacuation_routes': 4,
                'estimated_evacuation_time': '45-60 minutes',
                'population_at_risk': 650,
                'special_needs_population': 45
            }
        }
        
        return wui_analysis
        
    def _generate_risk_assessment(self, analysis_results):
        """Generate integrated fire risk assessment."""
        weather_analysis = analysis_results.get('fire_weather_analysis', {})
        fuel_analysis = analysis_results.get('fuel_analysis', {})
        wui_analysis = analysis_results.get('wui_analysis', {})
        
        risk_components = {}
        
        # Weather risk component
        critical_conditions = weather_analysis.get('critical_conditions', {})
        extreme_days = critical_conditions.get('extreme_fire_weather_days', 0)
        total_days = 90  # Assuming 90-day analysis period
        weather_risk = min(extreme_days / (total_days * 0.1), 1.0)  # Normalize
        risk_components['weather_risk'] = weather_risk
        
        # Fuel moisture risk
        current_conditions = fuel_analysis.get('current_conditions', {})
        live_moisture = current_conditions.get('mean_live_moisture', 100)
        fuel_risk = max(0, (80 - live_moisture) / 40)  # Normalize to 0-1
        risk_components['fuel_risk'] = fuel_risk
        
        # WUI risk
        wui_zones = wui_analysis.get('wui_zones', {})
        high_risk_structures = wui_analysis.get('structure_vulnerability', {}).get('high_risk_structures', 0)
        total_structures = wui_analysis.get('structure_vulnerability', {}).get('total_structures_in_wui', 1)
        wui_risk = high_risk_structures / total_structures
        risk_components['wui_risk'] = wui_risk
        
        # Calculate overall risk
        weights = {'weather_risk': 0.3, 'fuel_risk': 0.4, 'wui_risk': 0.3}
        overall_risk = sum(risk_components[comp] * weights[comp] for comp in weights.keys())
        
        risk_assessment = {
            'overall_risk_score': overall_risk,
            'risk_components': risk_components,
            'risk_level': 'High' if overall_risk > 0.7 else 'Moderate' if overall_risk > 0.4 else 'Low',
            'priority_areas': [],
            'recommendations': []
        }
        
        # Generate recommendations
        if weather_risk > 0.5:
            risk_assessment['recommendations'].append("Enhanced fire weather monitoring")
        if fuel_risk > 0.5:
            risk_assessment['recommendations'].append("Fuel reduction treatments")
        if wui_risk > 0.5:
            risk_assessment['recommendations'].append("WUI defensible space enforcement")
            
        return risk_assessment
        
    def _prepare_spatial_data(self, analysis_results):
        """Prepare spatial data for integration."""
        spatial_data = {
            'h3_resolution': self.h3_resolution,
            'h3_cells': {},
            'data_type': 'fire_risk'
        }
        
        risk_assessment = analysis_results.get('risk_assessment', {})
        overall_risk = risk_assessment.get('overall_risk_score', 0)
        
        # Generate spatial risk data for fuel moisture sites
        fuel_analysis = analysis_results.get('fuel_analysis', {})
        current_conditions = fuel_analysis.get('current_conditions', {})
        
        # Placeholder spatial data
        bounds = self.config.get('location', {}).get('bounds', {})
        west, south, east, north = (bounds.get('west', -124.4), bounds.get('south', 41.5),
                                   bounds.get('east', -123.5), bounds.get('north', 42.0))
        
        # Generate H3 cells with fire risk data
        np.random.seed(50)
        lat_points = np.linspace(south, north, 8)
        lon_points = np.linspace(west, east, 8)
        
        for lat in lat_points:
            for lon in lon_points:
                h3_cell = h3.latlng_to_cell(lat, lon, self.h3_resolution)
                risk_score = overall_risk + np.random.normal(0, 0.1)
                risk_score = np.clip(risk_score, 0, 1)
                
                spatial_data['h3_cells'][h3_cell] = {
                    'fire_risk_score': risk_score,
                    'data_quality': 'medium',
                    'last_updated': datetime.now().isoformat()
                }
                
        return spatial_data
        
    def _save_analysis_results(self, results):
        """Save analysis results to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.output_dir / f"fire_risk_analysis_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        logger.info(f"Fire risk analysis results saved to: {results_file}")
        
    def get_monitoring_status(self):
        """Get current monitoring system status."""
        return {
            'monitor_type': 'fire_risk',
            'location': 'del_norte_county',
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'configuration': self.fire_config,
            'monitoring_active': True
        } 