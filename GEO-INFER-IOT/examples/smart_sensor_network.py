#!/usr/bin/env python3
"""
GEO-INFER-IOT Example: Smart Sensor Network Management

This example demonstrates IoT sensor network deployment, data ingestion,
quality control, and real-time geospatial analytics.
"""

from datetime import datetime, timedelta
import numpy as np

from geo_infer_iot import (
    SensorNetwork,
    DataIngestionEngine,
    QualityController,
    StreamProcessor,
    AlertManager
)


def main():
    print("=" * 60)
    print("GEO-INFER-IOT: Smart Sensor Network Management")
    print("=" * 60)
    
    # 1. Define Sensor Network
    print("\n1. Setting Up Sensor Network...")
    
    network = SensorNetwork(
        network_id='SMART_CITY_001',
        name='Downtown Environmental Monitoring',
        protocol='mqtt'
    )
    
    # Define sensor locations
    sensors = [
        {'id': 'AQ_001', 'type': 'air_quality', 'lat': 34.05, 'lon': -118.25, 'parameters': ['pm25', 'pm10', 'o3', 'no2']},
        {'id': 'AQ_002', 'type': 'air_quality', 'lat': 34.06, 'lon': -118.26, 'parameters': ['pm25', 'pm10', 'o3', 'no2']},
        {'id': 'WX_001', 'type': 'weather', 'lat': 34.05, 'lon': -118.24, 'parameters': ['temperature', 'humidity', 'pressure', 'wind']},
        {'id': 'WX_002', 'type': 'weather', 'lat': 34.07, 'lon': -118.25, 'parameters': ['temperature', 'humidity', 'pressure', 'wind']},
        {'id': 'NZ_001', 'type': 'noise', 'lat': 34.055, 'lon': -118.255, 'parameters': ['db_level', 'frequency']},
        {'id': 'TR_001', 'type': 'traffic', 'lat': 34.05, 'lon': -118.26, 'parameters': ['vehicle_count', 'avg_speed']},
        {'id': 'TR_002', 'type': 'traffic', 'lat': 34.06, 'lon': -118.24, 'parameters': ['vehicle_count', 'avg_speed']},
        {'id': 'FL_001', 'type': 'flood', 'lat': 34.04, 'lon': -118.25, 'parameters': ['water_level', 'flow_rate']},
    ]
    
    for sensor in sensors:
        network.add_sensor(**sensor)
    
    status = network.get_network_status()
    print(f"   Network: {network.name}")
    print(f"   Sensors deployed: {status['sensor_count']}")
    print(f"   Sensor types: {', '.join(status.get('sensor_types', []))}")
    
    # 2. Initialize Data Ingestion
    print("\n2. Configuring Data Ingestion...")
    
    ingestion = DataIngestionEngine(
        buffer_size=1000,
        batch_interval_seconds=60,
        protocols=['mqtt', 'http', 'coap']
    )
    
    ingestion.configure(
        network_id=network.network_id,
        storage_backend='timeseries_db',
        compression='lz4',
        retention_days=90
    )
    
    print(f"   Buffer size: {ingestion.buffer_size} messages")
    print(f"   Batch interval: {ingestion.batch_interval_seconds}s")
    print(f"   Retention: 90 days")
    
    # 3. Simulate Sensor Data
    print("\n3. Simulating Sensor Readings...")
    
    # Generate simulated readings for last hour
    now = datetime.now()
    readings = []
    
    for minute in range(60):
        timestamp = now - timedelta(minutes=60-minute)
        
        for sensor in sensors:
            reading = {
                'sensor_id': sensor['id'],
                'timestamp': timestamp.isoformat(),
                'location': {'lat': sensor['lat'], 'lon': sensor['lon']},
                'values': {}
            }
            
            # Generate parameter values based on sensor type
            if sensor['type'] == 'air_quality':
                reading['values'] = {
                    'pm25': np.random.uniform(5, 35) + np.sin(minute/10) * 5,
                    'pm10': np.random.uniform(10, 50) + np.sin(minute/10) * 8,
                    'o3': np.random.uniform(20, 60),
                    'no2': np.random.uniform(10, 40)
                }
            elif sensor['type'] == 'weather':
                reading['values'] = {
                    'temperature': 22 + np.sin(minute/30) * 5 + np.random.normal(0, 0.5),
                    'humidity': 55 + np.random.uniform(-10, 10),
                    'pressure': 1013 + np.random.uniform(-2, 2),
                    'wind_speed': np.random.uniform(0, 15)
                }
            elif sensor['type'] == 'noise':
                # Higher noise during "rush hours"
                base_noise = 50 if 10 < minute < 50 else 65
                reading['values'] = {
                    'db_level': base_noise + np.random.uniform(-5, 10)
                }
            elif sensor['type'] == 'traffic':
                reading['values'] = {
                    'vehicle_count': int(np.random.uniform(10, 100)),
                    'avg_speed': np.random.uniform(20, 50)
                }
            elif sensor['type'] == 'flood':
                reading['values'] = {
                    'water_level': np.random.uniform(0.1, 0.5),
                    'flow_rate': np.random.uniform(0.5, 2.0)
                }
            
            readings.append(reading)
    
    # Ingest data
    ingestion_result = ingestion.ingest_batch(readings)
    
    print(f"   Readings generated: {len(readings)}")
    print(f"   Readings ingested: {ingestion_result['ingested']}")
    print(f"   Time range: 1 hour")
    
    # 4. Quality Control
    print("\n4. Performing Quality Control...")
    
    qc = QualityController(
        methods=['range_check', 'spike_detection', 'persistence_check', 'spatial_consistency']
    )
    
    # Define valid ranges for parameters
    qc.set_parameter_bounds({
        'pm25': {'min': 0, 'max': 500},
        'pm10': {'min': 0, 'max': 600},
        'temperature': {'min': -40, 'max': 60},
        'humidity': {'min': 0, 'max': 100},
        'db_level': {'min': 20, 'max': 140},
        'water_level': {'min': 0, 'max': 10}
    })
    
    # Run quality checks
    qc_results = qc.check_batch(readings)
    
    print("   Quality Control Results:")
    print(f"   - Valid readings: {qc_results['valid_count']} ({100*qc_results['valid_count']/len(readings):.1f}%)")
    print(f"   - Flagged readings: {qc_results['flagged_count']}")
    print("   - Issues by type:")
    for issue_type, count in qc_results.get('issues_by_type', {}).items():
        print(f"     • {issue_type}: {count}")
    
    # 5. Stream Processing
    print("\n5. Processing Data Streams...")
    
    processor = StreamProcessor(
        window_size_seconds=300,
        aggregation_methods=['mean', 'max', 'min', 'std']
    )
    
    # Calculate aggregations for air quality sensors
    aq_readings = [r for r in readings if r['sensor_id'].startswith('AQ_')]
    
    aggregations = processor.aggregate(
        readings=aq_readings,
        parameters=['pm25', 'pm10'],
        group_by='sensor_id'
    )
    
    print("\n   5-Minute Aggregations (Air Quality):")
    print(f"   {'Sensor':<10} {'PM2.5 Mean':>12} {'PM2.5 Max':>12} {'PM10 Mean':>12}")
    print(f"   {'-'*48}")
    for sensor_id, agg in list(aggregations.items())[:3]:
        pm25_mean = agg.get('pm25', {}).get('mean', 0)
        pm25_max = agg.get('pm25', {}).get('max', 0)
        pm10_mean = agg.get('pm10', {}).get('mean', 0)
        print(f"   {sensor_id:<10} {pm25_mean:>12.1f} {pm25_max:>12.1f} {pm10_mean:>12.1f}")
    
    # 6. Alert Management
    print("\n6. Configuring Alert System...")
    
    alert_manager = AlertManager(
        notification_channels=['email', 'sms', 'webhook'],
        alert_levels=['info', 'warning', 'critical']
    )
    
    # Define alert rules
    alert_manager.add_rule(
        name='High PM2.5',
        condition={'parameter': 'pm25', 'operator': '>', 'threshold': 35},
        level='warning',
        message='PM2.5 level exceeds EPA 24-hour standard'
    )
    
    alert_manager.add_rule(
        name='Critical PM2.5',
        condition={'parameter': 'pm25', 'operator': '>', 'threshold': 55},
        level='critical',
        message='PM2.5 level in unhealthy range'
    )
    
    alert_manager.add_rule(
        name='High Temperature',
        condition={'parameter': 'temperature', 'operator': '>', 'threshold': 35},
        level='warning',
        message='High temperature detected'
    )
    
    alert_manager.add_rule(
        name='Flood Warning',
        condition={'parameter': 'water_level', 'operator': '>', 'threshold': 2.0},
        level='critical',
        message='Flood threshold exceeded'
    )
    
    # Check for alerts
    alerts = alert_manager.evaluate(readings[-100:])  # Check recent readings
    
    print(f"   Alert rules configured: {alert_manager.rule_count}")
    print(f"   Alerts triggered: {len(alerts)}")
    
    if alerts:
        print("\n   Recent Alerts:")
        for alert in alerts[:5]:
            print(f"   [{alert['level'].upper()}] {alert['sensor_id']}: {alert['message']}")
    
    # 7. Spatial Analysis
    print("\n7. Computing Spatial Statistics...")
    
    # Calculate spatial statistics for PM2.5
    pm25_values = []
    pm25_locations = []
    
    for reading in readings:
        if 'pm25' in reading.get('values', {}):
            pm25_values.append(reading['values']['pm25'])
            pm25_locations.append((reading['location']['lat'], reading['location']['lon']))
    
    spatial_stats = {
        'mean': np.mean(pm25_values),
        'std': np.std(pm25_values),
        'max': np.max(pm25_values),
        'min': np.min(pm25_values),
        'hotspot_count': sum(1 for v in pm25_values if v > 35)
    }
    
    print(f"   PM2.5 Spatial Statistics:")
    print(f"   - Mean: {spatial_stats['mean']:.1f} µg/m³")
    print(f"   - Std Dev: {spatial_stats['std']:.1f} µg/m³")
    print(f"   - Range: {spatial_stats['min']:.1f} - {spatial_stats['max']:.1f} µg/m³")
    print(f"   - Exceedance points: {spatial_stats['hotspot_count']}")
    
    print("\n" + "=" * 60)
    print("IoT Sensor Network Analysis Complete!")
    print("=" * 60)
    
    # Summary
    print("\nNetwork Summary:")
    print(f"  - Active sensors: {status['sensor_count']}")
    print(f"  - Readings processed: {len(readings)}")
    print(f"  - Data quality: {100*qc_results['valid_count']/len(readings):.1f}%")
    print(f"  - Active alerts: {len(alerts)}")


if __name__ == "__main__":
    main()
