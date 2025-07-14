#!/usr/bin/env python3
"""
Radiation Surveillance Network Example

This example demonstrates how to use GEO-INFER-IOT for global radiation monitoring,
integrating multiple sensor networks (Safecast, EURDEP, etc.) with Bayesian spatial
inference for real-time background radiation surveillance.

Key features demonstrated:
- Integration with existing radiation monitoring networks
- Global-scale H3 spatial indexing
- Bayesian inference for radiation background estimation
- Real-time anomaly detection and alerting
- Integration with public radiation APIs
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

import numpy as np
import h3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("radiation_surveillance")

# Simulated radiation monitoring networks
RADIATION_NETWORKS = {
    "safecast": {
        "name": "Safecast Global Network",
        "api_url": "https://api.safecast.org/measurements",
        "variables": ["gamma_radiation"],
        "coverage": "global",
        "update_frequency": "real-time"
    },
    "eurdep": {
        "name": "European Radiological Data Exchange Platform",
        "api_url": "https://eurdep.jrc.ec.europa.eu/",
        "variables": ["gamma_dose_rate", "air_activity"],
        "coverage": "europe",
        "update_frequency": "hourly"
    },
    "ctbto": {
        "name": "Comprehensive Test Ban Treaty Organization",
        "api_url": "https://www.ctbto.org/verification-regime/monitoring/",
        "variables": ["radionuclide_activity", "particulate_activity"],
        "coverage": "global",
        "update_frequency": "daily"
    }
}

class RadiationSurveillanceSystem:
    """
    Global radiation surveillance system using IoT sensor networks.
    
    Features:
    - Integration with multiple radiation monitoring networks
    - Global H3 spatial indexing for efficient data organization
    - Bayesian spatial inference for background estimation
    - Real-time anomaly detection
    - Multi-scale analysis from local to global
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.measurements = []
        self.sensor_registry = {}
        self.global_h3_index = {}
        self.baseline_models = {}
        
        # Initialize with known monitoring networks
        self._setup_radiation_networks()
        
        logger.info("Radiation Surveillance System initialized")
    
    def _setup_radiation_networks(self):
        """Setup connections to known radiation monitoring networks."""
        for network_id, network_info in RADIATION_NETWORKS.items():
            self.sensor_registry[network_id] = {
                "network_info": network_info,
                "sensors": {},
                "last_update": None
            }
            
            logger.info(f"Configured network: {network_info['name']}")
    
    async def simulate_global_radiation_data(self, num_sensors: int = 100):
        """
        Simulate global radiation sensor data for demonstration.
        
        In a real implementation, this would connect to actual APIs
        like Safecast, EURDEP, etc.
        """
        logger.info(f"Simulating global radiation data from {num_sensors} sensors")
        
        # Generate sensors distributed globally
        for i in range(num_sensors):
            # Random global coordinates
            lat = random.uniform(-85, 85)  # Avoid polar regions
            lon = random.uniform(-180, 180)
            
            # Assign to networks based on location
            if -60 < lat < 75 and -30 < lon < 60:  # Europe
                network = "eurdep"
            elif random.random() < 0.7:  # Most others go to Safecast
                network = "safecast"
            else:
                network = "ctbto"
            
            sensor_id = f"{network}_sensor_{i:04d}"
            
            # Create H3 index for efficient spatial operations
            h3_index = h3.latlng_to_cell(lat, lon, 5)  # Global resolution
            
            # Simulate baseline radiation levels (realistic values)
            # Normal background: 0.05-0.2 μSv/h
            baseline_radiation = random.uniform(0.05, 0.2)
            
            # Add some spatial correlation (higher near certain areas)
            if 50 < lat < 55 and 30 < lon < 32:  # Chernobyl region
                baseline_radiation += random.uniform(0.1, 0.5)
            elif 35 < lat < 38 and 139 < lon < 142:  # Fukushima region
                baseline_radiation += random.uniform(0.05, 0.3)
            
            # Add temporal variation
            current_radiation = baseline_radiation * (1 + random.uniform(-0.2, 0.2))
            
            # Store sensor
            sensor_data = {
                "sensor_id": sensor_id,
                "network": network,
                "latitude": lat,
                "longitude": lon,
                "h3_index": h3_index,
                "baseline_radiation": baseline_radiation,
                "current_radiation": current_radiation,
                "last_update": datetime.now()
            }
            
            self.sensor_registry[network]["sensors"][sensor_id] = sensor_data
            
            # Create measurement
            measurement = {
                "sensor_id": sensor_id,
                "timestamp": datetime.now().isoformat(),
                "variable": "gamma_radiation",
                "value": current_radiation,
                "unit": "μSv/h",
                "latitude": lat,
                "longitude": lon,
                "h3_index": h3_index,
                "network": network,
                "quality_flags": ["validated"]
            }
            
            self.measurements.append(measurement)
            
            # Add to spatial index
            if h3_index not in self.global_h3_index:
                self.global_h3_index[h3_index] = []
            self.global_h3_index[h3_index].append(measurement)
        
        logger.info(f"Generated {len(self.measurements)} radiation measurements")
    
    def perform_bayesian_inference(self, h3_resolution: int = 4):
        """
        Perform Bayesian spatial inference on radiation data.
        
        This integrates with GEO-INFER-BAYES for sophisticated
        spatial modeling of radiation background.
        """
        logger.info("Performing Bayesian spatial inference on radiation data")
        
        # Group measurements by H3 cells at specified resolution
        h3_aggregated = {}
        
        for measurement in self.measurements:
            # Convert to target resolution
            target_h3 = h3.cell_to_parent(measurement["h3_index"], h3_resolution)
            
            if target_h3 not in h3_aggregated:
                h3_aggregated[target_h3] = []
            
            h3_aggregated[target_h3].append(measurement["value"])
        
        # Calculate statistics for each H3 cell
        h3_statistics = {}
        
        for h3_index, values in h3_aggregated.items():
            values = np.array(values)
            
            cell_stats = {
                "h3_index": h3_index,
                "mean_radiation": np.mean(values),
                "std_radiation": np.std(values),
                "min_radiation": np.min(values),
                "max_radiation": np.max(values),
                "count": len(values),
                "coordinates": h3.cell_to_latlng(h3_index)
            }
            
            # Simple anomaly detection (values > 3 sigma above mean)
            global_mean = np.mean([m["value"] for m in self.measurements])
            global_std = np.std([m["value"] for m in self.measurements])
            threshold = global_mean + 3 * global_std
            
            cell_stats["is_anomaly"] = cell_stats["max_radiation"] > threshold
            cell_stats["anomaly_score"] = max(0, (cell_stats["max_radiation"] - global_mean) / global_std)
            
            h3_statistics[h3_index] = cell_stats
        
        # In a full implementation, this would use GEO-INFER-BAYES
        # for sophisticated Gaussian Process models, uncertainty quantification, etc.
        
        self.inference_results = {
            "h3_resolution": h3_resolution,
            "cell_statistics": h3_statistics,
            "global_statistics": {
                "mean_radiation": np.mean([m["value"] for m in self.measurements]),
                "std_radiation": np.std([m["value"] for m in self.measurements]),
                "total_measurements": len(self.measurements),
                "anomalous_cells": sum(1 for stats in h3_statistics.values() if stats["is_anomaly"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Inference complete: {len(h3_statistics)} H3 cells analyzed")
        return self.inference_results
    
    def detect_radiation_anomalies(self) -> List[Dict]:
        """Detect and report radiation anomalies."""
        if not hasattr(self, 'inference_results'):
            self.perform_bayesian_inference()
        
        anomalies = []
        
        for h3_index, stats in self.inference_results["cell_statistics"].items():
            if stats["is_anomaly"]:
                lat, lon = stats["coordinates"]
                
                anomaly = {
                    "h3_index": h3_index,
                    "location": {"latitude": lat, "longitude": lon},
                    "radiation_level": stats["max_radiation"],
                    "anomaly_score": stats["anomaly_score"],
                    "sensor_count": stats["count"],
                    "timestamp": datetime.now().isoformat(),
                    "alert_level": self._classify_alert_level(stats["anomaly_score"])
                }
                
                anomalies.append(anomaly)
        
        anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
        
        logger.info(f"Detected {len(anomalies)} radiation anomalies")
        return anomalies
    
    def _classify_alert_level(self, anomaly_score: float) -> str:
        """Classify alert level based on anomaly score."""
        if anomaly_score > 5:
            return "CRITICAL"
        elif anomaly_score > 3:
            return "HIGH"
        elif anomaly_score > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_global_radiation_map(self, output_file: str = "global_radiation_map.json"):
        """Generate a global radiation map in GeoJSON format."""
        if not hasattr(self, 'inference_results'):
            self.perform_bayesian_inference()
        
        features = []
        
        for h3_index, stats in self.inference_results["cell_statistics"].items():
            # Get H3 cell boundary
            boundary = h3.cell_to_latlng_boundary(h3_index, geo_json=True)
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [boundary]
                },
                "properties": {
                    "h3_index": h3_index,
                    "mean_radiation": stats["mean_radiation"],
                    "max_radiation": stats["max_radiation"],
                    "sensor_count": stats["count"],
                    "is_anomaly": stats["is_anomaly"],
                    "anomaly_score": stats["anomaly_score"],
                    "radiation_classification": self._classify_radiation_level(stats["mean_radiation"])
                }
            }
            
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "title": "Global Background Radiation Map",
                "description": "Bayesian inference results for global radiation monitoring",
                "timestamp": self.inference_results["timestamp"],
                "h3_resolution": self.inference_results["h3_resolution"],
                "total_measurements": self.inference_results["global_statistics"]["total_measurements"]
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        logger.info(f"Global radiation map saved to {output_file}")
        return geojson
    
    def _classify_radiation_level(self, radiation: float) -> str:
        """Classify radiation level for visualization."""
        if radiation < 0.1:
            return "very_low"
        elif radiation < 0.2:
            return "low"
        elif radiation < 0.5:
            return "normal"
        elif radiation < 1.0:
            return "elevated"
        elif radiation < 2.0:
            return "high"
        else:
            return "very_high"
    
    def get_network_status(self) -> Dict:
        """Get status of all radiation monitoring networks."""
        status = {}
        
        for network_id, network_data in self.sensor_registry.items():
            sensor_count = len(network_data["sensors"])
            
            if sensor_count > 0:
                # Calculate coverage statistics
                sensors = list(network_data["sensors"].values())
                latitudes = [s["latitude"] for s in sensors]
                longitudes = [s["longitude"] for s in sensors]
                
                coverage_stats = {
                    "lat_range": [min(latitudes), max(latitudes)],
                    "lon_range": [min(longitudes), max(longitudes)],
                    "spatial_extent": (max(latitudes) - min(latitudes)) * (max(longitudes) - min(longitudes))
                }
            else:
                coverage_stats = {"lat_range": [0, 0], "lon_range": [0, 0], "spatial_extent": 0}
            
            status[network_id] = {
                "name": network_data["network_info"]["name"],
                "sensor_count": sensor_count,
                "coverage": network_data["network_info"]["coverage"],
                "update_frequency": network_data["network_info"]["update_frequency"],
                "coverage_stats": coverage_stats,
                "last_update": network_data["last_update"]
            }
        
        return status

async def main():
    """Main function to run the radiation surveillance example."""
    logger.info("Starting GEO-INFER-IOT Radiation Surveillance Example")
    
    # Initialize surveillance system
    config = {
        "h3_resolution": 5,
        "anomaly_threshold": 3.0,
        "update_interval": 3600  # 1 hour
    }
    
    surveillance = RadiationSurveillanceSystem(config)
    
    # Simulate global radiation data
    await surveillance.simulate_global_radiation_data(num_sensors=200)
    
    # Perform Bayesian spatial inference
    inference_results = surveillance.perform_bayesian_inference(h3_resolution=4)
    
    print("\n=== Global Radiation Surveillance Results ===")
    print(f"Total measurements: {inference_results['global_statistics']['total_measurements']}")
    print(f"Mean radiation: {inference_results['global_statistics']['mean_radiation']:.3f} μSv/h")
    print(f"Std radiation: {inference_results['global_statistics']['std_radiation']:.3f} μSv/h")
    print(f"Anomalous cells: {inference_results['global_statistics']['anomalous_cells']}")
    
    # Detect anomalies
    anomalies = surveillance.detect_radiation_anomalies()
    
    print(f"\n=== Radiation Anomalies Detected ===")
    for i, anomaly in enumerate(anomalies[:5]):  # Show top 5
        print(f"{i+1}. Alert Level: {anomaly['alert_level']}")
        print(f"   Location: {anomaly['location']['latitude']:.2f}, {anomaly['location']['longitude']:.2f}")
        print(f"   Radiation: {anomaly['radiation_level']:.3f} μSv/h")
        print(f"   Anomaly Score: {anomaly['anomaly_score']:.1f}")
        print(f"   Sensors: {anomaly['sensor_count']}")
        print()
    
    # Generate global map
    surveillance.generate_global_radiation_map("global_radiation_map.json")
    
    # Network status
    status = surveillance.get_network_status()
    print("=== Network Status ===")
    for network_id, info in status.items():
        print(f"{info['name']}: {info['sensor_count']} sensors ({info['coverage']} coverage)")
    
    logger.info("Radiation surveillance example completed")

if __name__ == "__main__":
    asyncio.run(main()) 