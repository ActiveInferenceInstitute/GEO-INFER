# H3 Module Configuration Guide

## 🎯 Overview

This guide provides step-by-step instructions for configuring GEO-INFER modules to integrate with H3 spatial indexing systems. It includes configuration schemas, setup procedures, and validation tools to ensure seamless H3 connectivity across the ecosystem.

## 📋 Configuration Schema Templates

### 1. Basic Module Configuration

Create a configuration file `h3_config.yaml` in your module's config directory:

```yaml
# GEO-INFER Module H3 Configuration Template
module_info:
  name: "GEO-INFER-{MODULE_NAME}"
  version: "1.0.0"
  description: "Description of module's spatial capabilities"
  maintainer: "module-team@geo-infer.org"

h3_configuration:
  # Default H3 resolution for the module (0-15)
  default_resolution: 8
  
  # List of supported H3 resolutions
  supported_resolutions: [6, 7, 8, 9, 10]
  
  # Types of data the module provides/consumes
  data_types:
    - "spatial_points"
    - "spatial_polygons"
    - "temporal_series"
    - "raster_data"
  
  # Supported aggregation methods
  aggregation_methods:
    - "sum"
    - "mean"
    - "median"
    - "max"
    - "min"
    - "count"
    - "density"
    - "weighted_average"
  
  # Data update frequency
  update_frequency: "daily"  # real-time, hourly, daily, weekly, monthly, on-demand
  
  # Maximum number of cells to process in a single operation
  max_cells_per_operation: 100000
  
  # Cache configuration
  cache_settings:
    enabled: true
    ttl_seconds: 3600
    max_cache_size: 10000

# API Configuration
api_endpoints:
  base_url: "https://api.geo-infer.space/h3/v1"
  module_endpoints:
    data_provider:
      path: "/provide-data"
      method: "POST"
      description: "Provide spatial data to H3 system"
    data_consumer:
      path: "/consume-data"
      method: "GET"
      description: "Consume H3 spatial data"
    status:
      path: "/status"
      method: "GET"
      description: "Module health and status"
  
  authentication:
    type: "api_key"  # api_key, jwt, oauth2
    header_name: "X-API-Key"
    
  rate_limiting:
    requests_per_minute: 1000
    burst_limit: 100

# Data Schema Configuration
data_schemas:
  input_schema:
    type: "object"
    properties:
      coordinates:
        type: "array"
        items:
          type: "object"
          properties:
            lat: {"type": "number", "minimum": -90, "maximum": 90}
            lng: {"type": "number", "minimum": -180, "maximum": 180}
      properties:
        type: "object"
        additionalProperties: true
      timestamp:
        type: "string"
        format: "date-time"
  
  output_schema:
    type: "object"
    properties:
      h3_cells:
        type: "array"
        items:
          type: "object"
          properties:
            h3_cell: {"type": "string", "pattern": "^[0-9a-f]{15}$"}
            resolution: {"type": "integer", "minimum": 0, "maximum": 15}
            properties: {"type": "object"}

# Integration Settings
integration:
  # OSC (OS Climate) integration
  osc_integration:
    enabled: true
    h3grid_service_url: "http://localhost:8080"
    h3grid_srv_path: "./repo/osc-geo-h3grid-srv"  # Fork from docxology
    h3loader_cli_path: "./repo/osc-geo-h3loader-cli"  # Fork from docxology
  
  # Database connections
  database:
    spatial_db:
      type: "postgresql"
      host: "localhost"
      port: 5432
      database: "geo_infer_spatial"
      schema: "h3_data"
    
    cache_db:
      type: "redis"
      host: "localhost"
      port: 6379
      database: 0

# Performance and Monitoring
performance:
  # Parallel processing settings
  max_workers: 4
  batch_size: 1000
  
  # Memory limits
  max_memory_mb: 2048
  
  # Monitoring
  metrics:
    enabled: true
    export_port: 9090
    export_path: "/metrics"
  
  logging:
    level: "INFO"
    format: "json"
    destination: "file"
    file_path: "./logs/h3_integration.log"

# Security Configuration
security:
  # Access control
  access_control:
    enabled: true
    default_permissions: "read"
    admin_users: ["admin@geo-infer.org"]
  
  # Data encryption
  encryption:
    at_rest: true
    in_transit: true
    algorithm: "AES-256"
  
  # Audit logging
  audit:
    enabled: true
    log_all_operations: true
    retention_days: 90
```

### 2. Module-Specific Configuration Examples

#### GEO-INFER-DATA Configuration
```yaml
# GEO-INFER-DATA specific H3 configuration
module_info:
  name: "GEO-INFER-DATA"
  specialization: "spatial_data_management"

h3_configuration:
  default_resolution: 9  # Higher resolution for data storage
  data_types:
    - "geospatial_datasets"
    - "point_collections"
    - "polygon_collections"
    - "raster_collections"
    - "temporal_datasets"
  
  # Data ingestion settings
  ingestion:
    supported_formats:
      - "geojson"
      - "shapefile"
      - "csv"
      - "geotiff"
      - "netcdf"
    
    validation:
      coordinate_validation: true
      geometry_validation: true
      attribute_validation: true
    
    transformation:
      auto_projection: true
      coordinate_system: "WGS84"

# Storage configuration
storage:
  primary:
    type: "postgresql_postgis"
    partitioning: "h3_resolution"
    indexing: "h3_spatial_index"
  
  archive:
    type: "s3_compatible"
    bucket: "geo-infer-h3-archive"
    compression: "gzip"
```

#### GEO-INFER-AI Configuration
```yaml
# GEO-INFER-AI specific H3 configuration
module_info:
  name: "GEO-INFER-AI"
  specialization: "spatial_machine_learning"

h3_configuration:
  default_resolution: 8
  data_types:
    - "training_datasets"
    - "prediction_grids"
    - "model_outputs"
  
  # AI/ML specific settings
  ml_settings:
    feature_extraction:
      spatial_features: true
      temporal_features: true
      neighborhood_features: true
      
    model_types:
      - "spatial_regression"
      - "spatial_classification"
      - "spatial_clustering"
      - "temporal_forecasting"
    
    training:
      cross_validation: "spatial_cv"
      test_split_method: "spatial_block"
      
# Model storage
model_storage:
  type: "mlflow"
  tracking_uri: "http://localhost:5000"
  artifact_location: "./models/h3_models"
```

#### GEO-INFER-AGENT Configuration
```yaml
# GEO-INFER-AGENT specific H3 configuration
module_info:
  name: "GEO-INFER-AGENT"
  specialization: "agent_based_modeling"

h3_configuration:
  default_resolution: 10  # High resolution for agent positioning
  data_types:
    - "agent_positions"
    - "movement_trajectories"
    - "interaction_networks"
    - "environment_states"
  
  # Agent simulation settings
  simulation:
    agent_types:
      - "mobile_agents"
      - "stationary_agents"
      - "resource_agents"
    
    movement_models:
      - "random_walk"
      - "directed_movement"
      - "social_movement"
    
    interaction_rules:
      - "spatial_proximity"
      - "resource_competition"
      - "information_sharing"

# Simulation engine
simulation_engine:
  type: "mesa"  # or "abm_framework"
  parallelization: true
  batch_processing: true
  real_time_visualization: true
```

### 3. Domain-Specific Configurations

#### Agriculture (GEO-INFER-AG)
```yaml
module_info:
  name: "GEO-INFER-AG"
  domain: "agriculture"

h3_configuration:
  default_resolution: 10  # Field-level resolution
  data_types:
    - "field_boundaries"
    - "crop_monitoring"
    - "soil_data"
    - "weather_data"
    - "yield_predictions"

# Agricultural specific settings
agriculture:
  crop_types:
    - "wheat"
    - "corn"
    - "soybeans"
    - "rice"
    - "cotton"
  
  monitoring_parameters:
    - "ndvi"
    - "soil_moisture"
    - "temperature"
    - "precipitation"
    - "growth_stage"
  
  analysis_methods:
    - "yield_prediction"
    - "pest_detection"
    - "irrigation_optimization"
    - "harvest_timing"
```

#### Health (GEO-INFER-HEALTH)
```yaml
module_info:
  name: "GEO-INFER-HEALTH"
  domain: "public_health"

h3_configuration:
  default_resolution: 9  # Neighborhood-level resolution
  data_types:
    - "disease_surveillance"
    - "healthcare_facilities"
    - "population_health"
    - "environmental_health"

# Health specific settings
health:
  surveillance_types:
    - "infectious_disease"
    - "chronic_disease"
    - "environmental_exposure"
    - "healthcare_access"
  
  privacy_settings:
    anonymization: true
    aggregation_threshold: 5
    differential_privacy: true
  
  integration:
    who_standards: true
    hl7_fhir: true
    icd_coding: true
```

## 🛠️ Implementation Guide

### 1. Module Setup Script

Create `setup_h3_integration.py` in your module:

```python
#!/usr/bin/env python3
"""
H3 Integration Setup Script for GEO-INFER Modules
"""

import os
import yaml
import logging
import importlib.util
from typing import Dict, Any, Optional
from pathlib import Path

class H3ModuleSetup:
    """Setup H3 integration for GEO-INFER modules"""
    
    def __init__(self, module_name: str, config_path: Optional[str] = None):
        self.module_name = module_name
        self.config_path = config_path or f"./config/h3_config.yaml"
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the setup process"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(f"H3Setup-{self.module_name}")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load H3 configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            self.logger.info(f"Loaded configuration from {self.config_path}")
            return config
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate H3 configuration against schema"""
        
        required_sections = [
            'module_info',
            'h3_configuration',
            'api_endpoints'
        ]
        
        for section in required_sections:
            if section not in config:
                self.logger.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate H3 specific settings
        h3_config = config['h3_configuration']
        
        # Check resolution settings
        default_res = h3_config.get('default_resolution')
        if not isinstance(default_res, int) or not (0 <= default_res <= 15):
            self.logger.error("Invalid default_resolution. Must be integer 0-15")
            return False
        
        supported_res = h3_config.get('supported_resolutions', [])
        if not all(isinstance(r, int) and 0 <= r <= 15 for r in supported_res):
            self.logger.error("Invalid supported_resolutions. Must be list of integers 0-15")
            return False
        
        if default_res not in supported_res:
            self.logger.error("default_resolution must be in supported_resolutions")
            return False
        
        self.logger.info("Configuration validation passed")
        return True
    
    def setup_database_connections(self, config: Dict[str, Any]) -> bool:
        """Setup database connections for H3 data"""
        
        if 'database' not in config.get('integration', {}):
            self.logger.warning("No database configuration found")
            return True
        
        db_config = config['integration']['database']
        
        # Setup spatial database
        if 'spatial_db' in db_config:
            spatial_config = db_config['spatial_db']
            success = self._setup_spatial_db(spatial_config)
            if not success:
                return False
        
        # Setup cache database
        if 'cache_db' in db_config:
            cache_config = db_config['cache_db']
            success = self._setup_cache_db(cache_config)
            if not success:
                return False
        
        return True
    
    def _setup_spatial_db(self, config: Dict[str, Any]) -> bool:
        """Setup spatial database for H3 data storage"""
        
        try:
            # Test database connection
            if config['type'] == 'postgresql':
                import psycopg2
                
                conn_params = {
                    'host': config['host'],
                    'port': config['port'],
                    'database': config['database'],
                    'user': config.get('user', os.getenv('DB_USER')),
                    'password': config.get('password', os.getenv('DB_PASSWORD'))
                }
                
                conn = psycopg2.connect(**conn_params)
                cursor = conn.cursor()
                
                # Check for PostGIS extension
                cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'postgis';")
                if not cursor.fetchone():
                    self.logger.warning("PostGIS extension not found. H3 spatial operations may be limited.")
                
                # Create H3 schema if needed
                schema = config.get('schema', 'h3_data')
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
                conn.commit()
                
                cursor.close()
                conn.close()
                
                self.logger.info("Spatial database connection successful")
                
        except Exception as e:
            self.logger.error(f"Failed to setup spatial database: {e}")
            return False
        
        return True
    
    def _setup_cache_db(self, config: Dict[str, Any]) -> bool:
        """Setup cache database for H3 operations"""
        
        try:
            if config['type'] == 'redis':
                import redis
                
                r = redis.Redis(
                    host=config['host'],
                    port=config['port'],
                    db=config['database']
                )
                
                # Test connection
                r.ping()
                
                self.logger.info("Cache database connection successful")
                
        except Exception as e:
            self.logger.error(f"Failed to setup cache database: {e}")
            return False
        
        return True
    
    def setup_osc_integration(self, config: Dict[str, Any]) -> bool:
        """Setup OSC (OS Climate) integration"""
        
        osc_config = config.get('integration', {}).get('osc_integration', {})
        
        if not osc_config.get('enabled', False):
            self.logger.info("OSC integration disabled")
            return True
        
        # Check for OSC tools
        h3grid_url = osc_config.get('h3grid_service_url')
        h3loader_path = osc_config.get('h3loader_cli_path')
        
        if h3grid_url:
            # Test H3 grid service
            try:
                import requests
                response = requests.get(f"{h3grid_url}/health", timeout=5)
                if response.status_code == 200:
                    self.logger.info("H3 grid service is accessible")
                else:
                    self.logger.warning(f"H3 grid service returned status {response.status_code}")
            except Exception as e:
                self.logger.warning(f"Could not connect to H3 grid service: {e}")
        
        if h3loader_path:
            # Check for H3 loader CLI
            if os.path.exists(h3loader_path):
                self.logger.info("H3 loader CLI found")
            else:
                self.logger.warning(f"H3 loader CLI not found at {h3loader_path}")
        
        return True
    
    def generate_integration_code(self, config: Dict[str, Any]) -> str:
        """Generate Python integration code for the module"""
        
        module_name = config['module_info']['name']
        h3_config = config['h3_configuration']
        
        code_template = f'''
# Auto-generated H3 integration code for {module_name}
# Generated by H3ModuleSetup

import h3
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class {module_name.replace('-', '')}H3Integration:
    """H3 integration for {module_name}"""
    
    def __init__(self):
        self.default_resolution = {h3_config['default_resolution']}
        self.supported_resolutions = {h3_config['supported_resolutions']}
        self.data_types = {h3_config['data_types']}
        self.aggregation_methods = {h3_config['aggregation_methods']}
    
    async def convert_points_to_h3(self, 
                                  points: List[Dict[str, Any]], 
                                  resolution: Optional[int] = None) -> List[str]:
        """Convert geographic points to H3 cells"""
        
        resolution = resolution or self.default_resolution
        
        if resolution not in self.supported_resolutions:
            raise ValueError(f"Resolution {{resolution}} not supported. Use one of {{self.supported_resolutions}}")
        
        h3_cells = []
        for point in points:
            if 'lat' in point and 'lng' in point:
                h3_cell = h3.latlng_to_cell(point['lat'], point['lng'], resolution)
                h3_cells.append(h3_cell)
        
        return h3_cells
    
    async def aggregate_data_to_h3(self, 
                                  data: List[Dict[str, Any]], 
                                  aggregation_method: str = 'mean') -> Dict[str, Any]:
        """Aggregate data to H3 cells"""
        
        if aggregation_method not in self.aggregation_methods:
            raise ValueError(f"Aggregation method {{aggregation_method}} not supported")
        
        # Implementation specific to {module_name}
        # TODO: Implement aggregation logic
        
        return {{"status": "success", "method": aggregation_method}}
    
    async def query_h3_data(self, 
                           h3_cells: List[str], 
                           properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Query data for specific H3 cells"""
        
        # Implementation specific to {module_name}
        # TODO: Implement query logic
        
        return {{"h3_cells": h3_cells, "properties": properties}}

# Module integration instance
h3_integration = {module_name.replace('-', '')}H3Integration()
'''
        
        return code_template
    
    def create_integration_files(self, config: Dict[str, Any]):
        """Create integration files for the module"""
        
        # Create integration directory
        integration_dir = Path("./src") / config['module_info']['name'].lower().replace('-', '_') / "h3_integration"
        integration_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate and save integration code
        integration_code = self.generate_integration_code(config)
        
        init_file = integration_dir / "__init__.py"
        with open(init_file, 'w') as f:
            f.write(integration_code)
        
        # Create configuration validation module
        validation_code = '''
import jsonschema
from typing import Dict, Any

H3_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["module_info", "h3_configuration"],
    "properties": {
        "module_info": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "pattern": "^GEO-INFER-[A-Z]+$"}
            }
        },
        "h3_configuration": {
            "type": "object",
            "required": ["default_resolution", "supported_resolutions", "data_types"],
            "properties": {
                "default_resolution": {"type": "integer", "minimum": 0, "maximum": 15},
                "supported_resolutions": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 0, "maximum": 15}
                },
                "data_types": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}

def validate_h3_config(config: Dict[str, Any]) -> bool:
    """Validate H3 configuration against schema"""
    try:
        jsonschema.validate(config, H3_CONFIG_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False
'''
        
        validation_file = integration_dir / "validation.py"
        with open(validation_file, 'w') as f:
            f.write(validation_code)
        
        self.logger.info(f"Created integration files in {integration_dir}")
    
    def run_setup(self) -> bool:
        """Run the complete H3 integration setup"""
        
        self.logger.info(f"Starting H3 integration setup for {self.module_name}")
        
        try:
            # Load configuration
            config = self.load_configuration()
            
            # Validate configuration
            if not self.validate_configuration(config):
                return False
            
            # Setup database connections
            if not self.setup_database_connections(config):
                return False
            
            # Setup OSC integration
            if not self.setup_osc_integration(config):
                return False
            
            # Create integration files
            self.create_integration_files(config)
            
            self.logger.info("H3 integration setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False

def main():
    """Main setup function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python setup_h3_integration.py <MODULE_NAME>")
        sys.exit(1)
    
    module_name = sys.argv[1]
    setup = H3ModuleSetup(module_name)
    
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### 2. Configuration Validation Tool

Create `validate_h3_config.py`:

```python
#!/usr/bin/env python3
"""
H3 Configuration Validation Tool
"""

import yaml
import jsonschema
import argparse
import sys
from typing import Dict, Any

def load_schema() -> Dict[str, Any]:
    """Load the H3 configuration JSON schema"""
    
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "GEO-INFER H3 Module Configuration Schema",
        "type": "object",
        "required": ["module_info", "h3_configuration", "api_endpoints"],
        "properties": {
            "module_info": {
                "type": "object",
                "required": ["name", "version"],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^GEO-INFER-[A-Z]+$"
                    },
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "maintainer": {"type": "string"}
                }
            },
            "h3_configuration": {
                "type": "object",
                "required": ["default_resolution", "supported_resolutions", "data_types"],
                "properties": {
                    "default_resolution": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 15
                    },
                    "supported_resolutions": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 15
                        }
                    },
                    "data_types": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "aggregation_methods": {
                        "type": "array",
                        "items": {
                            "enum": ["sum", "mean", "median", "max", "min", "count", "density", "weighted_average"]
                        }
                    },
                    "update_frequency": {
                        "enum": ["real-time", "hourly", "daily", "weekly", "monthly", "on-demand"]
                    }
                }
            },
            "api_endpoints": {
                "type": "object",
                "required": ["base_url"],
                "properties": {
                    "base_url": {
                        "type": "string",
                        "format": "uri"
                    }
                }
            }
        }
    }
    
    return schema

def validate_config_file(config_path: str) -> bool:
    """Validate H3 configuration file"""
    
    try:
        # Load configuration
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Load schema
        schema = load_schema()
        
        # Validate against schema
        jsonschema.validate(config, schema)
        
        # Additional validations
        h3_config = config['h3_configuration']
        
        # Check that default_resolution is in supported_resolutions
        default_res = h3_config['default_resolution']
        supported_res = h3_config['supported_resolutions']
        
        if default_res not in supported_res:
            raise ValueError("default_resolution must be in supported_resolutions list")
        
        print(f"✅ Configuration file {config_path} is valid")
        return True
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False
        
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False
        
    except jsonschema.ValidationError as e:
        print(f"❌ Configuration validation error: {e.message}")
        print(f"   Path: {' -> '.join(str(x) for x in e.path)}")
        return False
        
    except ValueError as e:
        print(f"❌ Configuration logic error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main validation function"""
    
    parser = argparse.ArgumentParser(description="Validate H3 module configuration")
    parser.add_argument("config_file", help="Path to H3 configuration YAML file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Validating configuration file: {args.config_file}")
    
    success = validate_config_file(args.config_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 🚀 Quick Start Instructions

### 1. For New Modules

```bash
# 1. Copy configuration template
cp docs/h3_config_template.yaml config/h3_config.yaml

# 2. Edit configuration for your module
nano config/h3_config.yaml

# 3. Validate configuration
python validate_h3_config.py config/h3_config.yaml

# 4. Run setup
python setup_h3_integration.py GEO-INFER-YOUR-MODULE

# 5. Test integration
python -c "from src.geo_infer_your_module.h3_integration import h3_integration; print('✅ Integration loaded successfully')"
```

### 2. For Existing Modules

```bash
# 1. Create H3 configuration
mkdir -p config
cp docs/h3_config_template.yaml config/h3_config.yaml

# 2. Customize configuration
# Edit config/h3_config.yaml with your module's specific settings

# 3. Install dependencies
pip install h3 pyyaml jsonschema

# 4. Run integration setup
python setup_h3_integration.py YOUR-MODULE-NAME

# 5. Verify setup
python validate_h3_config.py config/h3_config.yaml
```

## 🔧 Testing and Validation

### Integration Test Template

Create `test_h3_integration.py`:

```python
import pytest
import asyncio
from src.your_module.h3_integration import h3_integration

class TestH3Integration:
    """Test H3 integration functionality"""
    
    @pytest.mark.asyncio
    async def test_point_conversion(self):
        """Test converting points to H3 cells"""
        
        points = [
            {'lat': 40.7128, 'lng': -74.0060},  # New York
            {'lat': 51.5074, 'lng': -0.1278}    # London
        ]
        
        h3_cells = await h3_integration.convert_points_to_h3(points)
        
        assert len(h3_cells) == 2
        assert all(isinstance(cell, str) for cell in h3_cells)
        assert all(len(cell) == 15 for cell in h3_cells)
    
    @pytest.mark.asyncio
    async def test_data_aggregation(self):
        """Test data aggregation to H3 cells"""
        
        data = [
            {'lat': 40.7128, 'lng': -74.0060, 'value': 10},
            {'lat': 40.7129, 'lng': -74.0061, 'value': 20}
        ]
        
        result = await h3_integration.aggregate_data_to_h3(data, 'mean')
        
        assert result['status'] == 'success'
        assert result['method'] == 'mean'
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        
        assert h3_integration.default_resolution in h3_integration.supported_resolutions
        assert len(h3_integration.data_types) > 0
        assert len(h3_integration.aggregation_methods) > 0

if __name__ == "__main__":
    pytest.main([__file__])
```

## 📚 Best Practices

1. **Configuration Management**
   - Use environment-specific configurations
   - Validate configurations on startup
   - Version your configuration schemas

2. **Error Handling**
   - Implement comprehensive error handling
   - Log errors with sufficient context
   - Provide fallback mechanisms

3. **Performance**
   - Use batch processing for large datasets
   - Implement caching strategies
   - Monitor resource usage

4. **Security**
   - Encrypt sensitive configuration data
   - Implement proper access controls
   - Audit all H3 operations

5. **Testing**
   - Write comprehensive integration tests
   - Test with realistic data volumes
   - Validate configuration schemas

This configuration guide provides everything needed to successfully integrate any GEO-INFER module with H3 spatial indexing systems.