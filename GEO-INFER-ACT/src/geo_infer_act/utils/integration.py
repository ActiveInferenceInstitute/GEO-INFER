"""
Integration utilities for connecting with other GEO-INFER modules.
"""
from typing import Dict, Any, Optional, Union
import importlib
import logging
import os
import sys
import warnings

from geo_infer_act.utils.config import get_config_value


def initialize_logger():
    """Initialize module logger."""
    logger = logging.getLogger("geo_infer_act.integration")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = initialize_logger()


def integrate_space(config: Dict[str, Any], 
                   data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Integrate with GEO-INFER-SPACE module.
    
    Args:
        config: Configuration dictionary
        data: Optional data to pass to the space module
        
    Returns:
        Results from space module integration
    """
    # Check if integration is enabled
    is_enabled = get_config_value(
        config, 'integration.space_module.enabled', False
    )
    
    if not is_enabled:
        logger.info("Space module integration is disabled in config")
        return {}
    
    # Get API endpoint from config
    api_endpoint = get_config_value(
        config, 'integration.space_module.api_endpoint', None
    )
    
    if not api_endpoint:
        logger.warning("Space module API endpoint not configured")
        return {}
    
    try:
        # Import the space module API
        module_path, api_class = api_endpoint.rsplit('.', 1)
        space_module = importlib.import_module(module_path)
        api_cls = getattr(space_module, api_class)
        
        # Initialize API
        space_api = api_cls()
        
        # Call API methods based on the provided data
        if data is None:
            data = {}
            
        if 'action' not in data:
            logger.warning("No action specified for space module integration")
            return {}
            
        action = data['action']
        action_params = data.get('params', {})
        
        if hasattr(space_api, action):
            action_method = getattr(space_api, action)
            result = action_method(**action_params)
            return {'status': 'success', 'result': result}
        else:
            logger.warning(f"Action {action} not found in space module API")
            return {'status': 'error', 'message': f"Action {action} not supported"}
            
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import space module: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logger.error(f"Error in space module integration: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def integrate_time(config: Dict[str, Any], 
                  data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Integrate with GEO-INFER-TIME module.
    
    Args:
        config: Configuration dictionary
        data: Optional data to pass to the time module
        
    Returns:
        Results from time module integration
    """
    # Implementation similar to integrate_space
    is_enabled = get_config_value(
        config, 'integration.time_module.enabled', False
    )
    
    if not is_enabled:
        logger.info("Time module integration is disabled in config")
        return {}
    
    api_endpoint = get_config_value(
        config, 'integration.time_module.api_endpoint', None
    )
    
    if not api_endpoint:
        logger.warning("Time module API endpoint not configured")
        return {}
    
    try:
        # Import the time module API
        module_path, api_class = api_endpoint.rsplit('.', 1)
        time_module = importlib.import_module(module_path)
        api_cls = getattr(time_module, api_class)
        
        # Initialize API
        time_api = api_cls()
        
        # Call API methods based on the provided data
        if data is None:
            data = {}
            
        if 'action' not in data:
            logger.warning("No action specified for time module integration")
            return {}
            
        action = data['action']
        action_params = data.get('params', {})
        
        if hasattr(time_api, action):
            action_method = getattr(time_api, action)
            result = action_method(**action_params)
            return {'status': 'success', 'result': result}
        else:
            logger.warning(f"Action {action} not found in time module API")
            return {'status': 'error', 'message': f"Action {action} not supported"}
            
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import time module: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logger.error(f"Error in time module integration: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def integrate_sim(config: Dict[str, Any], 
                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Integrate with GEO-INFER-SIM module.
    
    Args:
        config: Configuration dictionary
        data: Optional data to pass to the simulation module
        
    Returns:
        Results from simulation module integration
    """
    # Implementation similar to integrate_space
    is_enabled = get_config_value(
        config, 'integration.sim_module.enabled', False
    )
    
    if not is_enabled:
        logger.info("Simulation module integration is disabled in config")
        return {}
    
    api_endpoint = get_config_value(
        config, 'integration.sim_module.api_endpoint', None
    )
    
    if not api_endpoint:
        logger.warning("Simulation module API endpoint not configured")
        return {}
    
    try:
        # Import the simulation module API
        module_path, api_class = api_endpoint.rsplit('.', 1)
        sim_module = importlib.import_module(module_path)
        api_cls = getattr(sim_module, api_class)
        
        # Initialize API
        sim_api = api_cls()
        
        # Call API methods based on the provided data
        if data is None:
            data = {}
            
        if 'action' not in data:
            logger.warning("No action specified for simulation module integration")
            return {}
            
        action = data['action']
        action_params = data.get('params', {})
        
        if hasattr(sim_api, action):
            action_method = getattr(sim_api, action)
            result = action_method(**action_params)
            return {'status': 'success', 'result': result}
        else:
            logger.warning(f"Action {action} not found in simulation module API")
            return {'status': 'error', 'message': f"Action {action} not supported"}
            
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import simulation module: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logger.error(f"Error in simulation module integration: {str(e)}")
        return {'status': 'error', 'message': str(e)} 