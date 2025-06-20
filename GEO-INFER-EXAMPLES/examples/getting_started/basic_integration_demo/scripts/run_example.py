#!/usr/bin/env python3
"""
Basic Integration Demo - GEO-INFER Examples
Demonstrates: DATA → SPACE → TIME → API integration pattern
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    return logging.getLogger('basic_demo')

class BasicIntegrationDemo:
    def __init__(self):
        self.logger = setup_logging()
        np.random.seed(42)  # Reproducible results
    
    def run_demo(self):
        """Run the complete 4-module integration demonstration."""
        self.logger.info("🚀 Starting Basic Integration Demo")
        self.logger.info("Pattern: DATA → SPACE → TIME → API")
        
        start_time = time.time()
        
        # Step 1: DATA Module - Generate sample data
        self.logger.info("\n📥 STEP 1: DATA Module - Data Ingestion")
        data = self._generate_sample_data()
        self.logger.info(f"✅ Generated {len(data['locations'])} data points")
        
        # Step 2: SPACE Module - Spatial analysis
        self.logger.info("\n🗺️ STEP 2: SPACE Module - Spatial Analysis")
        spatial_results = self._analyze_spatial_patterns(data)
        self.logger.info(f"✅ Identified {len(spatial_results['clusters'])} spatial clusters")
        
        # Step 3: TIME Module - Temporal analysis
        self.logger.info("\n⏰ STEP 3: TIME Module - Temporal Analysis")
        temporal_results = self._analyze_temporal_patterns(data)
        self.logger.info(f"✅ Detected {len(temporal_results['trends'])} trends, {len(temporal_results['anomalies'])} anomalies")
        
        # Step 4: API Module - Integration results
        self.logger.info("\n🔌 STEP 4: API Module - Results Integration")
        final_results = self._generate_integration_results(data, spatial_results, temporal_results)
        
        execution_time = time.time() - start_time
        self.logger.info(f"\n✅ Demo completed in {execution_time:.2f} seconds")
        
        self._display_summary(final_results, execution_time)
        self._save_results(final_results, execution_time)
        
        return final_results
    
    def _generate_sample_data(self):
        """Generate sample geospatial data."""
        n_points = 50
        center_lat, center_lon = 37.7749, -122.4194  # San Francisco
        
        locations = []
        for i in range(n_points):
            locations.append({
                'id': f'loc_{i:03d}',
                'latitude': center_lat + np.random.uniform(-0.05, 0.05),
                'longitude': center_lon + np.random.uniform(-0.05, 0.05),
                'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 48)),
                'value': np.random.normal(50, 15),
                'category': np.random.choice(['residential', 'commercial', 'industrial'])
            })
        
        return {
            'locations': locations,
            'metadata': {
                'source': 'demo_data',
                'region': 'san_francisco',
                'quality_score': 0.95
            }
        }
    
    def _analyze_spatial_patterns(self, data):
        """Simulate spatial analysis."""
        locations = data['locations']
        
        # Simple clustering simulation
        n_clusters = 3
        clusters = []
        
        for i in range(n_clusters):
            cluster_size = len(locations) // n_clusters
            start_idx = i * cluster_size
            end_idx = start_idx + cluster_size if i < n_clusters - 1 else len(locations)
            
            cluster_locs = locations[start_idx:end_idx]
            lats = [loc['latitude'] for loc in cluster_locs]
            lons = [loc['longitude'] for loc in cluster_locs]
            
            clusters.append({
                'id': f'cluster_{i}',
                'center_lat': np.mean(lats),
                'center_lon': np.mean(lons),
                'size': len(cluster_locs),
                'avg_value': np.mean([loc['value'] for loc in cluster_locs])
            })
        
        return {
            'clusters': clusters,
            'total_area_km2': 25.0,
            'spatial_distribution': 'clustered'
        }
    
    def _analyze_temporal_patterns(self, data):
        """Simulate temporal analysis."""
        locations = data['locations']
        values = [loc['value'] for loc in locations]
        
        # Detect trends (simplified)
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        trends = [
            {
                'type': 'daily_pattern',
                'direction': 'increasing' if np.random.random() > 0.5 else 'stable',
                'confidence': 0.85
            }
        ]
        
        # Detect anomalies
        anomalies = []
        for loc in locations:
            if abs(loc['value'] - mean_val) > 2 * std_val:
                anomalies.append({
                    'location_id': loc['id'],
                    'value': loc['value'],
                    'expected_range': [mean_val - 2*std_val, mean_val + 2*std_val],
                    'severity': 'high' if abs(loc['value'] - mean_val) > 3 * std_val else 'medium'
                })
        
        return {
            'trends': trends,
            'anomalies': anomalies,
            'time_span_hours': 48,
            'observation_frequency': len(locations) / 48
        }
    
    def _generate_integration_results(self, data, spatial, temporal):
        """Generate final integrated results."""
        return {
            'summary': {
                'total_locations': len(data['locations']),
                'spatial_clusters': len(spatial['clusters']),
                'temporal_trends': len(temporal['trends']),
                'anomalies_detected': len(temporal['anomalies']),
                'data_quality': data['metadata']['quality_score']
            },
            'insights': [
                f"Identified {len(spatial['clusters'])} distinct spatial clusters",
                f"Detected {len(temporal['anomalies'])} temporal anomalies requiring attention",
                f"Overall data quality is excellent ({data['metadata']['quality_score']:.1%})"
            ],
            'recommendations': [
                "Consider zone-based analysis for spatial clusters",
                "Investigate temporal anomalies for data quality issues",
                "Expand analysis with additional modules (AI, RISK)"
            ],
            'api_endpoints': [
                {'method': 'GET', 'path': '/api/v1/results/spatial', 'description': 'Spatial analysis results'},
                {'method': 'GET', 'path': '/api/v1/results/temporal', 'description': 'Temporal analysis results'}
            ]
        }
    
    def _display_summary(self, results, execution_time):
        """Display results summary."""
        print("\n" + "="*60)
        print("🎯 INTEGRATION DEMO RESULTS")
        print("="*60)
        
        summary = results['summary']
        print(f"📊 Summary:")
        print(f"  ├─ Locations: {summary['total_locations']}")
        print(f"  ├─ Clusters: {summary['spatial_clusters']}")
        print(f"  ├─ Trends: {summary['temporal_trends']}")
        print(f"  ├─ Anomalies: {summary['anomalies_detected']}")
        print(f"  └─ Quality: {summary['data_quality']:.1%}")
        
        print(f"\n💡 Key Insights:")
        for i, insight in enumerate(results['insights'], 1):
            print(f"  {i}. {insight}")
        
        print(f"\n🎯 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n⚡ Performance:")
        print(f"  ├─ Execution Time: {execution_time:.2f} seconds")
        print(f"  ├─ Modules Used: DATA, SPACE, TIME, API")
        print(f"  └─ Pattern: Linear Pipeline")
        
        print("\n✨ This demonstrates the basic 4-module integration pattern!")
        print("🚀 Try more complex examples in health_integration/ or agriculture_integration/")
        print("="*60)
    
    def _save_results(self, results, execution_time):
        """Save results to file."""
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'demo_results_{timestamp}.json'
        
        full_results = {
            'demo_results': results,
            'execution_metadata': {
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'modules_used': ['DATA', 'SPACE', 'TIME', 'API'],
                'integration_pattern': 'linear_pipeline'
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(full_results, f, indent=2, default=str)
        
        print(f"📁 Results saved to: {output_file.name}")

def main():
    """Main function."""
    print("🌟 GEO-INFER Basic Integration Demo")
    print("Demonstrating: DATA → SPACE → TIME → API")
    
    try:
        demo = BasicIntegrationDemo()
        demo.run_demo()
        return 0
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 