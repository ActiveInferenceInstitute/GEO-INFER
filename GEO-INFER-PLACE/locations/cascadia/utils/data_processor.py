#!/usr/bin/env python3
"""
Data Processor for Cascadia Agricultural Analysis

This module handles all data processing operations including module initialization,
data validation, and export operations.
"""

import logging
import json
import time
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# Import the necessary components
try:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
    PLACE_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: PLACE backend not available: {e}")
    PLACE_BACKEND_AVAILABLE = False
    CascadianAgriculturalH3Backend = None

try:
    from geo_infer_space.core.unified_backend import NumpyEncoder
    SPACE_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: SPACE backend not available: {e}")
    SPACE_BACKEND_AVAILABLE = False
    import numpy as np
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NumpyEncoder, self).default(obj)

def initialize_modules(active_modules: List[str], shared_backend, osc_repo_path: str) -> Dict[str, Any]:
    """Initialize all available modules using the shared backend"""
    logger = logging.getLogger(__name__)
    modules = {}
    
    # Import all the specialized modules from the 'cascadia' location
    try:
        from zoning.geo_infer_zoning import GeoInferZoning
        ZONING_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Zoning module not available: {e}")
        ZONING_AVAILABLE = False
        GeoInferZoning = None

    try:
        from current_use.geo_infer_current_use import GeoInferCurrentUse
        CURRENT_USE_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Current use module not available: {e}")
        CURRENT_USE_AVAILABLE = False
        GeoInferCurrentUse = None

    try:
        from ownership.geo_infer_ownership import GeoInferOwnership
        OWNERSHIP_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Ownership module not available: {e}")
        OWNERSHIP_AVAILABLE = False
        GeoInferOwnership = None

    try:
        from improvements.geo_infer_improvements import GeoInferImprovements
        IMPROVEMENTS_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"Improvements module not available: {e}")
        IMPROVEMENTS_AVAILABLE = False
        GeoInferImprovements = None
    
    # Initialize available modules using the shared backend
    if 'zoning' in active_modules and ZONING_AVAILABLE:
        try:
            modules['zoning'] = GeoInferZoning(shared_backend)
            logger.info("✅ Zoning module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize zoning module: {e}")
    
    if 'current_use' in active_modules and CURRENT_USE_AVAILABLE:
        try:
            modules['current_use'] = GeoInferCurrentUse(shared_backend)
            logger.info("✅ Current use module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize current use module: {e}")
    
    # Add other modules as they become available
    if 'ownership' in active_modules and OWNERSHIP_AVAILABLE:
        try:
            modules['ownership'] = GeoInferOwnership(shared_backend)
            logger.info("✅ Ownership module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ownership module: {e}")
    
    if 'improvements' in active_modules and IMPROVEMENTS_AVAILABLE:
        try:
            modules['improvements'] = GeoInferImprovements(shared_backend)
            logger.info("✅ Improvements module initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize improvements module: {e}")
    
    if not modules:
        logger.error("❌ No modules could be initialized.")
        return {}
    
    # Update the shared backend with initialized modules
    shared_backend.modules = modules
    logger.info(f"✅ Updated shared backend with {len(modules)} active modules")
    
    return modules

def create_shared_backend(resolution: int, target_counties: Dict, output_dir: Path, osc_repo_path: str) -> CascadianAgriculturalH3Backend:
    """Create a single shared backend for all modules"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creating shared backend for all modules...")
    
    try:
        shared_backend = CascadianAgriculturalH3Backend(
            modules={},  # Start with empty modules, will be populated
            resolution=resolution,
            bioregion='Cascadia',
            target_counties=target_counties,
            base_data_dir=output_dir / 'data',
            osc_repo_dir=osc_repo_path
        )
        logger.info(f"✅ Shared backend created with {len(shared_backend.target_hexagons)} target hexagons")
        return shared_backend
    except Exception as e:
        logger.error(f"❌ Failed to create shared backend: {e}")
        raise

def export_results(backend, redevelopment_scores: Dict, summary: Dict,
                  output_dir: Path, timestamp: str, bioregion_lower: str, 
                  export_format: str = 'geojson') -> Dict[str, str]:
    """
    Export analysis results with enhanced visualization options.
    
    Args:
        backend: Unified backend with processed data
        redevelopment_scores: Redevelopment potential scores
        summary: Analysis summary
        output_dir: Output directory
        timestamp: Timestamp for file naming
        bioregion_lower: Lowercase bioregion name
        export_format: Export format (geojson, csv, json)
        
    Returns:
        Dictionary with paths to exported files
    """
    logger = logging.getLogger(__name__)
    logger.info("Step 4: Exporting analysis results...")
    
    export_start = time.time()
    export_paths = {}
    
    try:
        # Export unified data
        unified_path = output_dir / f"{bioregion_lower}_unified_data_{timestamp}.{export_format}"
        backend.export_unified_data(str(unified_path), export_format)
        export_paths['unified_data'] = str(unified_path)
        logger.info(f"✅ Successfully exported enhanced unified data to {unified_path}")
        
        # Export redevelopment scores
        redevelopment_path = output_dir / f"{bioregion_lower}_redevelopment_scores_{timestamp}.json"
        with open(redevelopment_path, 'w') as f:
            json.dump(redevelopment_scores, f, indent=2, cls=NumpyEncoder)
        export_paths['redevelopment_scores'] = str(redevelopment_path)
        logger.info(f"Exported redevelopment scores to {redevelopment_path}")
        
        # Export summary
        summary_path = output_dir / f"{bioregion_lower}_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, cls=NumpyEncoder)
        export_paths['summary'] = str(summary_path)
        logger.info(f"Exported summary to {summary_path}")
        
        # Create efficient visualizations
        logger.info("Creating efficient visualization alternatives...")
        
        # Option 1: Datashader visualization (recommended for large datasets)
        try:
            from utils.datashader_visualization import create_datashader_visualization
            datashader_results = create_datashader_visualization(backend, output_dir)
            export_paths.update(datashader_results)
            logger.info("✅ Datashader visualizations created successfully")
        except ImportError as e:
            logger.warning(f"Datashader not available: {e}")
        except Exception as e:
            logger.error(f"Failed to create Datashader visualizations: {e}")
        
        # Option 2: Deepscatter visualization (lightweight web-based)
        try:
            from utils.deepscatter_visualization import create_deepscatter_visualization
            deepscatter_results = create_deepscatter_visualization(backend, output_dir)
            export_paths.update(deepscatter_results)
            logger.info("✅ Deepscatter visualizations created successfully")
        except ImportError as e:
            logger.warning(f"Deepscatter dependencies not available: {e}")
        except Exception as e:
            logger.error(f"Failed to create Deepscatter visualizations: {e}")
        
        # Option 3: Lightweight static plots (fallback)
        try:
            from utils.static_visualization import create_static_plots
            static_results = create_static_plots(backend, output_dir)
            export_paths.update(static_results)
            logger.info("✅ Static plots created successfully")
        except Exception as e:
            logger.error(f"Failed to create static plots: {e}")
        
        export_time = time.time() - export_start
        logger.info(f"📊 Data export completed in {export_time:.1f} seconds")
        
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        export_paths['error'] = str(e)
    
    return export_paths

def validate_data_acquisition(modules: Dict) -> Dict[str, int]:
    """Validate data acquisition for each module"""
    logger = logging.getLogger(__name__)
    data_acquisition_summary = {}
    
    logger.info("🔍 Starting comprehensive data acquisition and processing tracking...")
    
    # Track data acquisition for each module
    for module_name, module in modules.items():
        logger.info(f"🔍 Pre-analysis data check for {module_name} module...")
        try:
            # Check if module has real data
            data_path = module.data_dir
            if data_path.exists():
                data_files = list(data_path.glob("*.geojson"))
                logger.info(f"  📁 {module_name}: Found {len(data_files)} data files")
                for file in data_files:
                    logger.info(f"    📄 {file.name}")
            else:
                logger.warning(f"  ⚠️ {module_name}: No data directory found")
        except Exception as e:
            logger.error(f"  ❌ {module_name}: Error checking data: {e}")
            
        logger.info(f"🔍 Post-analysis data check for {module_name} module...")
        try:
            data_path = module.data_dir
            if data_path.exists():
                data_files = list(data_path.glob("*.geojson"))
                processed_count = len([f for f in data_files if f.stat().st_size > 100])  # Files with real content
                logger.info(f"  ✅ {module_name}: {processed_count} processed data files")
                data_acquisition_summary[module_name] = processed_count
            else:
                logger.warning(f"  ⚠️ {module_name}: No data directory after analysis")
                data_acquisition_summary[module_name] = 0
        except Exception as e:
            logger.error(f"  ❌ {module_name}: Error in post-analysis check: {e}")
            data_acquisition_summary[module_name] = 0
    
    logger.info("✅ Data acquisition validation complete")
    return data_acquisition_summary 