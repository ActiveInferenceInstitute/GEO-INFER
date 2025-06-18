"""
GEO-INFER-EXAMPLES: Comprehensive demonstration framework for the GEO-INFER ecosystem.

This module serves as the primary entry point for exploring the power and capabilities 
of the GEO-INFER framework through real-world, cross-module integration examples.

Core Philosophy:
- Demonstrate cross-module integration, not novel functionality
- Showcase the synergistic power of combining GEO-INFER modules
- Provide clear learning pathways for users of all levels
- Focus on orchestrating existing module capabilities

Key Features:
- Cross-module integration examples
- Comprehensive documentation and tutorials
- Real-world application scenarios
- Best practices demonstration
- Minimal utilities focused on orchestration
"""

__version__ = "0.1.0"

# Import core components for example orchestration
from . import api
from . import core
from . import models
from . import utils

# Import key example orchestration components
from .core.example_runner import ExampleRunner
from .core.config_manager import ConfigManager
from .core.module_connector import ModuleConnector
from .models.example_metadata import ExampleMetadata
from .models.execution_result import ExecutionResult
from .utils.dependency_checker import DependencyChecker
from .utils.logging_helper import LoggingHelper

# Export public API focused on example orchestration
__all__ = [
    # Core orchestration components
    "ExampleRunner",
    "ConfigManager", 
    "ModuleConnector",
    
    # Example models
    "ExampleMetadata",
    "ExecutionResult",
    
    # Utilities for examples
    "DependencyChecker",
    "LoggingHelper",
    
    # Submodules
    "api",
    "core", 
    "models",
    "utils"
]

# Package metadata
__author__ = "GEO-INFER Team"
__email__ = "info@geo-infer.org"
__license__ = "MIT"
__description__ = "Comprehensive demonstration framework showcasing cross-module integration for the GEO-INFER ecosystem"
__keywords__ = ["geospatial", "examples", "integration", "demonstrations", "tutorials"]

# Example categories for easy navigation
EXAMPLE_CATEGORIES = {
    "health_integration": "Health & Epidemiology Integration Examples",
    "agriculture_integration": "Agricultural Intelligence Examples", 
    "urban_integration": "Smart Cities & Urban Planning Examples",
    "climate_integration": "Climate & Environmental Systems Examples",
    "research_integration": "Research & Analytics Workflows Examples",
    "getting_started": "Getting Started Tutorials"
}

# Integration patterns demonstrated
INTEGRATION_PATTERNS = {
    "sequential": "Sequential Processing Pattern (DATA → SPACE → TIME → AI → RESULTS)",
    "parallel": "Parallel Analysis Pattern (DATA → [SPACE + TIME + AI] → INTEGRATION → RESULTS)",
    "feedback": "Feedback Loop Pattern (DATA → SPACE → SIM → ACT → [UPDATE] → SPACE)",
    "multi_domain": "Multi-Domain Integration Pattern ([AG + HEALTH] → SPACE → TIME → [RISK + ECON] → POLICY)",
    "community_driven": "Community-Driven Pattern (CIV → [SPACE + APP] → [NORMS + ORG] → CONSENSUS)"
}

def get_available_examples():
    """
    Get a list of all available examples with their metadata.
    
    Returns:
        dict: Dictionary of available examples organized by category
    """
    from .utils.example_discovery import discover_examples
    return discover_examples()

def validate_example_environment(example_name):
    """
    Validate that the environment has all required modules for an example.
    
    Args:
        example_name (str): Name of the example to validate
        
    Returns:
        dict: Validation results with missing dependencies and recommendations
    """
    checker = DependencyChecker()
    return checker.validate_example_dependencies(example_name)

def run_example(example_name, config_overrides=None):
    """
    Run a specific example with optional configuration overrides.
    
    Args:
        example_name (str): Name of the example to run
        config_overrides (dict, optional): Configuration overrides
        
    Returns:
        ExecutionResult: Results of the example execution
    """
    runner = ExampleRunner()
    return runner.execute_example(example_name, config_overrides)

# Convenience functions for common use cases
def list_examples_by_modules(module_list):
    """
    Find examples that use a specific combination of modules.
    
    Args:
        module_list (list): List of module names to search for
        
    Returns:
        list: Examples that use the specified modules
    """
    examples = get_available_examples()
    matching_examples = []
    
    for category, category_examples in examples.items():
        for example in category_examples:
            if all(module in example.get('modules', []) for module in module_list):
                matching_examples.append(example)
    
    return matching_examples

def get_learning_pathway(user_level="beginner"):
    """
    Get a recommended learning pathway based on user level.
    
    Args:
        user_level (str): User experience level (beginner, intermediate, advanced, expert)
        
    Returns:
        list: Ordered list of recommended examples
    """
    pathways = {
        "beginner": [
            "getting_started/basic_integration_demo",
            "getting_started/first_analysis_workflow",
            "health_integration/disease_surveillance_pipeline",
            "agriculture_integration/precision_farming_system"
        ],
        "intermediate": [
            "urban_integration/participatory_planning",
            "climate_integration/ecosystem_monitoring",
            "health_integration/environmental_health_assessment",
            "agriculture_integration/supply_chain_optimization"
        ],
        "advanced": [
            "climate_integration/carbon_accounting",
            "urban_integration/environmental_justice",
            "research_integration/statistical_field_mapping",
            "health_integration/health_disparities_mapping"
        ],
        "expert": [
            "research_integration/active_inference_spatial",
            "research_integration/cognitive_geospatial_modeling",
            "research_integration/complex_systems_analysis"
        ]
    }
    
    return pathways.get(user_level, pathways["beginner"])

# Module constraints and guidelines for contributors
DESIGN_CONSTRAINTS = {
    "no_novel_algorithms": "Examples should not implement novel algorithms - use existing module functionality",
    "cross_module_focus": "Every example must demonstrate meaningful integration of 2+ modules",
    "comprehensive_docs": "Each example must include complete documentation following the standard template",
    "real_world_problems": "Examples should solve actual problems, not toy scenarios",
    "minimal_utilities": "Utilities should only orchestrate existing capabilities, not duplicate functionality"
} 