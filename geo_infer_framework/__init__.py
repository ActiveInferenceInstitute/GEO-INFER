"""
GEO-INFER Framework - Main Entry Point

This is the main entry point for the GEO-INFER framework, providing
easy access to all modules and utilities.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"

class GEOINFERFramework:
    """Main framework class that provides access to all GEO-INFER modules."""
    
    def __init__(self):
        self.modules = {}
        self._load_modules()
    
    def _load_modules(self):
        """Load all available GEO-INFER modules."""
        try:
            # Import the path manager
            from .geo_infer_paths import get_path_manager
            path_manager = get_path_manager()
            
            # Add all module paths
            path_manager.add_all_paths()
            
            # Try to import each module
            available_modules = path_manager.list_available_modules()
            
            for module_name in available_modules:
                try:
                    module = path_manager.import_module(module_name)
                    if module:
                        self.modules[module_name] = module
                        logger.debug(f"Loaded module: {module_name}")
                except Exception as e:
                    logger.warning(f"Failed to load module {module_name}: {e}")
            
            logger.info(f"Loaded {len(self.modules)} modules")
            
        except Exception as e:
            logger.error(f"Failed to initialize framework: {e}")
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a specific module by name."""
        return self.modules.get(module_name)
    
    def list_modules(self) -> List[str]:
        """List all available modules."""
        return list(self.modules.keys())
    
    def get_module_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all modules."""
        info = {}
        for name, module in self.modules.items():
            try:
                info[name] = {
                    'version': getattr(module, '__version__', 'unknown'),
                    'description': getattr(module, '__doc__', 'No description available'),
                    'author': getattr(module, '__author__', 'Unknown'),
                }
            except Exception as e:
                info[name] = {
                    'version': 'unknown',
                    'description': f'Error loading info: {e}',
                    'author': 'Unknown',
                }
        return info
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run diagnostics on the framework."""
        diagnostics = {
            'framework_version': __version__,
            'python_version': sys.version,
            'loaded_modules': len(self.modules),
            'module_list': self.list_modules(),
            'module_info': self.get_module_info(),
        }
        
        # Test some common imports
        import_tests = {
            'geo_infer_space': 'SPACE module',
            'geo_infer_place': 'PLACE module', 
            'geo_infer_iot': 'IOT module',
            'geo_infer_bayes': 'BAYES module',
        }
        
        import_results = {}
        for module_name, description in import_tests.items():
            try:
                module = self.get_module(module_name)
                if module:
                    import_results[module_name] = {
                        'status': 'loaded',
                        'description': description
                    }
                else:
                    import_results[module_name] = {
                        'status': 'not_found',
                        'description': description
                    }
            except Exception as e:
                import_results[module_name] = {
                    'status': 'error',
                    'description': description,
                    'error': str(e)
                }
        
        diagnostics['import_tests'] = import_results
        return diagnostics

# Global framework instance
_framework = None

def get_framework() -> GEOINFERFramework:
    """Get the global framework instance."""
    global _framework
    if _framework is None:
        _framework = GEOINFERFramework()
    return _framework

def list_modules() -> List[str]:
    """List all available modules."""
    return get_framework().list_modules()

def get_module(module_name: str) -> Optional[Any]:
    """Get a specific module."""
    return get_framework().get_module(module_name)

def run_diagnostics() -> Dict[str, Any]:
    """Run framework diagnostics."""
    return get_framework().run_diagnostics()

# Convenience imports for commonly used modules
def _import_common_modules():
    """Import commonly used modules for convenience."""
    try:
        # Import path manager
        from .geo_infer_paths import add_all_paths, import_from_module
        
        # Add all paths
        add_all_paths()
        
        # Try to import common modules
        common_imports = {
            'PlaceAnalyzer': ('geo_infer_place', 'PlaceAnalyzer'),
            'setup_osc_geo': ('geo_infer_space', 'setup_osc_geo'),
            'IoTDataIngestion': ('geo_infer_iot', 'IoTDataIngestion'),
            'GaussianProcess': ('geo_infer_bayes', 'GaussianProcess'),
        }
        
        for name, (module_name, item_name) in common_imports.items():
            try:
                item = import_from_module(module_name, item_name)
                if item:
                    globals()[name] = item
            except Exception as e:
                logger.debug(f"Could not import {name}: {e}")
                
    except Exception as e:
        logger.warning(f"Could not import common modules: {e}")

# Try to import common modules
_import_common_modules()

# Export main framework components
__all__ = [
    'GEOINFERFramework',
    'get_framework',
    'list_modules', 
    'get_module',
    'run_diagnostics',
    '__version__',
    '__author__',
    '__email__',
] 