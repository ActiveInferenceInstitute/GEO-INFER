"""
Module Integration Utilities

This module provides utilities for integrating different GEO-INFER-MATH modules
and ensuring proper cross-dependencies and data flow between components.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModuleIntegrator:
    """Helper class for integrating different GEO-INFER-MATH modules."""

    def __init__(self):
        """Initialize the module integrator."""
        self._module_cache = {}
        self._dependency_graph = self._build_dependency_graph()

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph for module relationships."""
        return {
            'spatial_statistics': ['geometry', 'linalg_tensor'],
            'interpolation': ['geometry', 'linalg_tensor', 'spatial_statistics'],
            'optimization': ['linalg_tensor', 'numerical_methods'],
            'geometry': [],
            'linalg_tensor': ['geometry'],
            'numerical_methods': ['linalg_tensor'],
            'transforms': ['geometry'],
            'graph_theory': ['geometry', 'linalg_tensor'],
            'regression': ['spatial_statistics', 'linalg_tensor'],
            'clustering': ['spatial_statistics', 'linalg_tensor']
        }

    def check_module_compatibility(self, module_name: str) -> Dict[str, Any]:
        """
        Check if a module and its dependencies are available.

        Args:
            module_name: Name of the module to check

        Returns:
            Dictionary with compatibility information
        """
        available_modules = self._get_available_modules()
        dependencies = self._dependency_graph.get(module_name, [])

        missing_deps = [dep for dep in dependencies if dep not in available_modules]

        return {
            'module_available': module_name in available_modules,
            'dependencies_available': len(missing_deps) == 0,
            'missing_dependencies': missing_deps,
            'available_modules': available_modules
        }

    def _get_available_modules(self) -> List[str]:
        """Get list of currently available modules."""
        # This would check which modules are actually importable
        available = []

        modules_to_check = [
            'geometry', 'spatial_statistics', 'interpolation', 'optimization',
            'linalg_tensor', 'numerical_methods', 'transforms', 'graph_theory',
            'regression', 'clustering'
        ]

        for module_name in modules_to_check:
            try:
                # Try to import the module
                if module_name in ['geometry', 'spatial_statistics', 'interpolation', 'optimization']:
                    __import__(f'geo_infer_math.core.{module_name}')
                    available.append(module_name)
                elif module_name in ['linalg_tensor', 'numerical_methods', 'transforms', 'graph_theory']:
                    __import__(f'geo_infer_math.core.{module_name}')
                    available.append(module_name)
                elif module_name in ['regression', 'clustering']:
                    __import__(f'geo_infer_math.models.{module_name}')
                    available.append(module_name)
            except ImportError:
                logger.debug(f"Module {module_name} not available")

        return available

    def create_integrated_analysis_pipeline(self,
                                          analysis_type: str,
                                          **kwargs) -> Callable:
        """
        Create an integrated analysis pipeline combining multiple modules.

        Args:
            analysis_type: Type of analysis ('environmental', 'urban', 'health', etc.)
            **kwargs: Parameters for the analysis

        Returns:
            Function that performs the integrated analysis
        """
        if analysis_type == 'environmental':
            return self._create_environmental_analysis_pipeline(**kwargs)
        elif analysis_type == 'urban':
            return self._create_urban_analysis_pipeline(**kwargs)
        elif analysis_type == 'health':
            return self._create_health_analysis_pipeline(**kwargs)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

    def _create_environmental_analysis_pipeline(self, **kwargs) -> Callable:
        """Create environmental analysis pipeline."""
        def environmental_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Integrated environmental analysis combining multiple modules.

            Args:
                data: Dictionary containing environmental data

            Returns:
                Comprehensive environmental analysis results
            """
            results = {}

            # 1. Spatial statistics analysis
            if 'spatial_statistics' in self._get_available_modules():
                from geo_infer_math.core.spatial_statistics import MoranI, getis_ord_g

                coords = data.get('coordinates', np.array([]))
                values = data.get('air_quality', np.array([]))

                if len(coords) > 0 and len(values) > 0:
                    from geo_infer_math.core.linalg_tensor import MatrixOperations
                    weights = MatrixOperations.spatial_weights_matrix(coords, method='inverse_distance')

                    moran = MoranI(weights)
                    results['spatial_autocorrelation'] = moran.compute(values, coords)

                    results['hotspots'] = getis_ord_g(values, weights)

            # 2. Interpolation analysis
            if 'interpolation' in self._get_available_modules():
                from geo_infer_math.core.interpolation import SpatialInterpolator

                coords = data.get('coordinates', np.array([]))
                values = data.get('temperature', np.array([]))

                if len(coords) > 0 and len(values) > 0:
                    interpolator = SpatialInterpolator(method='idw')
                    interpolator.fit(coords, values)

                    # Create prediction grid
                    x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
                    y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
                    grid_x = np.linspace(x_min, x_max, 20)
                    grid_y = np.linspace(y_min, y_max, 20)
                    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
                    grid_points = np.column_stack([grid_xx.flatten(), grid_yy.flatten()])

                    results['interpolation'] = interpolator.predict(grid_points)

            # 3. Clustering analysis
            if 'clustering' in self._get_available_modules():
                from geo_infer_math.models.clustering import spatial_clustering_analysis

                coords = data.get('coordinates', np.array([]))
                values = data.get('humidity', np.array([]))

                if len(coords) > 0 and len(values) > 0:
                    features = np.column_stack([coords, values.reshape(-1, 1)])
                    results['clustering'] = spatial_clustering_analysis(features, coords, method='kmeans')

            return results

        return environmental_analysis

    def _create_urban_analysis_pipeline(self, **kwargs) -> Callable:
        """Create urban analysis pipeline."""
        def urban_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Integrated urban analysis combining multiple modules.

            Args:
                data: Dictionary containing urban data

            Returns:
                Comprehensive urban analysis results
            """
            results = {}

            # 1. Network analysis using graph theory
            if 'graph_theory' in self._get_available_modules():
                from geo_infer_math.core.graph_theory import SpatialGraph

                # Create road network graph
                intersections = data.get('intersections', np.array([]))
                connections = data.get('connections', [])

                if len(intersections) > 0:
                    graph = SpatialGraph(directed=False)

                    # Add nodes
                    for i, coord in enumerate(intersections):
                        graph.add_node(f'intersection_{i}', coord)

                    # Add edges
                    for conn in connections:
                        if len(conn) >= 2:
                            graph.add_edge(f'intersection_{conn[0]}', f'intersection_{conn[1]}', 1.0)

                    results['network_analysis'] = graph.spatial_network_analysis()

            # 2. Spatial regression for urban planning
            if 'regression' in self._get_available_modules():
                from geo_infer_math.models.regression import spatial_regression_analysis

                coords = data.get('coordinates', np.array([]))
                features = data.get('features', np.array([]))
                target = data.get('target', np.array([]))

                if len(coords) > 0 and len(features) > 0 and len(target) > 0:
                    results['spatial_regression'] = spatial_regression_analysis(
                        features, target, coords, model_type='gwr'
                    )

            return results

        return urban_analysis

    def _create_health_analysis_pipeline(self, **kwargs) -> Callable:
        """Create health analysis pipeline."""
        def health_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Integrated health analysis combining multiple modules.

            Args:
                data: Dictionary containing health data

            Returns:
                Comprehensive health analysis results
            """
            results = {}

            # 1. Spatial statistics for disease patterns
            if 'spatial_statistics' in self._get_available_modules():
                from geo_infer_math.core.spatial_statistics import MoranI, getis_ord_g

                coords = data.get('coordinates', np.array([]))
                health_data = data.get('health_metrics', np.array([]))

                if len(coords) > 0 and len(health_data) > 0:
                    from geo_infer_math.core.linalg_tensor import MatrixOperations
                    weights = MatrixOperations.spatial_weights_matrix(coords, method='knn', k=5)

                    moran = MoranI(weights)
                    results['disease_clusters'] = moran.compute(health_data, coords)

                    results['health_hotspots'] = getis_ord_g(health_data, weights)

            # 2. Regression analysis for health outcomes
            if 'regression' in self._get_available_modules():
                from geo_infer_math.models.regression import spatial_regression_analysis

                coords = data.get('coordinates', np.array([]))
                features = data.get('socioeconomic_features', np.array([]))
                health_outcomes = data.get('health_outcomes', np.array([]))

                if len(coords) > 0 and len(features) > 0 and len(health_outcomes) > 0:
                    results['health_regression'] = spatial_regression_analysis(
                        features, health_outcomes, coords, model_type='sar'
                    )

            return results

        return health_analysis

    def validate_cross_module_data_flow(self, source_module: str, target_module: str,
                                      data: Any) -> Dict[str, Any]:
        """
        Validate data compatibility between modules.

        Args:
            source_module: Source module name
            target_module: Target module name
            data: Data to validate

        Returns:
            Validation results
        """
        validation_results = {
            'compatible': True,
            'warnings': [],
            'errors': []
        }

        # Define expected data formats for each module
        module_requirements = {
            'spatial_statistics': {
                'required_fields': ['coordinates', 'values'],
                'coordinate_format': 'numpy_array_2d',
                'values_format': 'numpy_array_1d'
            },
            'interpolation': {
                'required_fields': ['known_points', 'known_values', 'query_points'],
                'coordinate_format': 'numpy_array_2d',
                'values_format': 'numpy_array_1d'
            },
            'clustering': {
                'required_fields': ['features', 'coordinates'],
                'coordinate_format': 'numpy_array_2d',
                'features_format': 'numpy_array_2d'
            },
            'regression': {
                'required_fields': ['X', 'y', 'coordinates'],
                'coordinate_format': 'numpy_array_2d',
                'X_format': 'numpy_array_2d',
                'y_format': 'numpy_array_1d'
            }
        }

        source_reqs = module_requirements.get(source_module, {})
        target_reqs = module_requirements.get(target_module, {})

        # Check if data has required fields
        for field in target_reqs.get('required_fields', []):
            if not hasattr(data, field) and field not in data:
                validation_results['errors'].append(f"Missing required field: {field}")
                validation_results['compatible'] = False

        # Check data format compatibility
        if 'coordinates' in data and target_reqs.get('coordinate_format') == 'numpy_array_2d':
            coords = data['coordinates']
            if not isinstance(coords, np.ndarray) or coords.ndim != 2:
                validation_results['errors'].append("Coordinates must be 2D numpy array")
                validation_results['compatible'] = False

        return validation_results

def create_integrated_workflow(analysis_steps: List[Dict[str, Any]],
                            data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create and execute an integrated workflow combining multiple modules.

    Args:
        analysis_steps: List of analysis step configurations
        data: Input data dictionary

    Returns:
        Workflow results
    """
    integrator = ModuleIntegrator()
    results = {}
    current_data = data.copy()

    for step in analysis_steps:
        step_name = step.get('name', 'unnamed_step')
        module = step.get('module', 'unknown')
        function = step.get('function', None)
        parameters = step.get('parameters', {})

        logger.info(f"Executing step: {step_name} using module: {module}")

        try:
            # Validate module compatibility
            compatibility = integrator.check_module_compatibility(module)
            if not compatibility['module_available']:
                logger.warning(f"Module {module} not available, skipping step {step_name}")
                continue

            if not compatibility['dependencies_available']:
                logger.warning(f"Dependencies for module {module} not available: {compatibility['missing_dependencies']}")
                continue

            # Execute the analysis step
            if module == 'spatial_statistics':
                if function == 'moran_i':
                    from geo_infer_math.core.spatial_statistics import MoranI
                    coords = current_data.get('coordinates')
                    values = current_data.get('values')

                    if coords is not None and values is not None:
                        from geo_infer_math.core.linalg_tensor import MatrixOperations
                        weights = MatrixOperations.spatial_weights_matrix(coords, **parameters)
                        moran = MoranI(weights)
                        results[step_name] = moran.compute(values, coords)

            elif module == 'interpolation':
                if function == 'spatial_interpolation':
                    from geo_infer_math.core.interpolation import SpatialInterpolator
                    coords = current_data.get('coordinates')
                    values = current_data.get('values')
                    query_points = parameters.get('query_points')

                    if coords is not None and values is not None and query_points is not None:
                        interpolator = SpatialInterpolator(method=parameters.get('method', 'idw'))
                        interpolator.fit(coords, values)
                        results[step_name] = interpolator.predict(query_points)

            # Update current data with results
            current_data.update(results.get(step_name, {}))

        except Exception as e:
            logger.error(f"Error in step {step_name}: {e}")
            results[step_name] = {'error': str(e)}

    return results

# Convenience functions for common workflows
def environmental_monitoring_workflow(coordinates: np.ndarray,
                                    air_quality: np.ndarray,
                                    temperature: np.ndarray,
                                    humidity: np.ndarray) -> Dict[str, Any]:
    """
    Execute a standard environmental monitoring workflow.

    Args:
        coordinates: Monitoring station coordinates
        air_quality: Air quality measurements
        temperature: Temperature measurements
        humidity: Humidity measurements

    Returns:
        Environmental analysis results
    """
    data = {
        'coordinates': coordinates,
        'air_quality': air_quality,
        'temperature': temperature,
        'humidity': humidity
    }

    analysis_steps = [
        {
            'name': 'air_quality_analysis',
            'module': 'spatial_statistics',
            'function': 'moran_i',
            'parameters': {'method': 'inverse_distance', 'k': 8}
        },
        {
            'name': 'temperature_interpolation',
            'module': 'interpolation',
            'function': 'spatial_interpolation',
            'parameters': {'method': 'idw', 'power': 2}
        }
    ]

    return create_integrated_workflow(analysis_steps, data)


def verify_with_theorem_proving(
    theorem: str,
    assumptions: Optional[List[str]] = None,
    backend: str = 'z3'
) -> Dict[str, Any]:
    """
    Verify mathematical operation using theorem proving.

    Args:
        theorem: Theorem statement
        assumptions: List of assumptions
        backend: Theorem prover backend

    Returns:
        Verification results
    """
    try:
        from geo_infer_math.core.theorem_proving import TheoremProver
        
        prover = TheoremProver(backend=backend)
        result = prover.prove(theorem, assumptions)
        
        return {
            'verified': result.status.value == 'proven',
            'status': result.status.value,
            'proof': result.proof,
            'backend': result.backend
        }
    except ImportError:
        logger.warning("Theorem proving not available")
        return {'verified': False, 'error': 'Theorem proving not available'}


def information_theory_analysis(
    coordinates: np.ndarray,
    values: np.ndarray,
    analysis_type: str = 'entropy'
) -> Dict[str, Any]:
    """
    Perform information theory analysis on spatial data.

    Args:
        coordinates: Spatial coordinates
        values: Values at locations
        analysis_type: Type of analysis ('entropy', 'mutual_information', 'kl_divergence')

    Returns:
        Analysis results
    """
    try:
        from geo_infer_math.core.information_theory import (
            spatial_entropy,
            EntropyCalculator
        )
        
        if analysis_type == 'entropy':
            entropy = spatial_entropy(coordinates, values)
            return {'entropy': entropy, 'type': 'spatial_entropy'}
        else:
            return {'error': f'Analysis type {analysis_type} not yet implemented'}
    except ImportError:
        logger.warning("Information theory not available")
        return {'error': 'Information theory not available'}

def urban_planning_workflow(intersections: np.ndarray,
                          connections: List[Tuple[int, int]],
                          land_use: np.ndarray,
                          population_density: np.ndarray) -> Dict[str, Any]:
    """
    Execute a standard urban planning workflow.

    Args:
        intersections: Road intersection coordinates
        connections: Road connections between intersections
        land_use: Land use classifications
        population_density: Population density data

    Returns:
        Urban planning analysis results
    """
    data = {
        'intersections': intersections,
        'connections': connections,
        'land_use': land_use,
        'population_density': population_density
    }

    analysis_steps = [
        {
            'name': 'network_analysis',
            'module': 'graph_theory',
            'function': 'network_analysis',
            'parameters': {}
        },
        {
            'name': 'spatial_regression',
            'module': 'regression',
            'function': 'spatial_regression',
            'parameters': {'model_type': 'gwr'}
        }
    ]

    return create_integrated_workflow(analysis_steps, data)


def verify_with_theorem_proving(
    theorem: str,
    assumptions: Optional[List[str]] = None,
    backend: str = 'z3'
) -> Dict[str, Any]:
    """
    Verify mathematical operation using theorem proving.

    Args:
        theorem: Theorem statement
        assumptions: List of assumptions
        backend: Theorem prover backend

    Returns:
        Verification results
    """
    try:
        from geo_infer_math.core.theorem_proving import TheoremProver
        
        prover = TheoremProver(backend=backend)
        result = prover.prove(theorem, assumptions)
        
        return {
            'verified': result.status.value == 'proven',
            'status': result.status.value,
            'proof': result.proof,
            'backend': result.backend
        }
    except ImportError:
        logger.warning("Theorem proving not available")
        return {'verified': False, 'error': 'Theorem proving not available'}


def information_theory_analysis(
    coordinates: np.ndarray,
    values: np.ndarray,
    analysis_type: str = 'entropy'
) -> Dict[str, Any]:
    """
    Perform information theory analysis on spatial data.

    Args:
        coordinates: Spatial coordinates
        values: Values at locations
        analysis_type: Type of analysis ('entropy', 'mutual_information', 'kl_divergence')

    Returns:
        Analysis results
    """
    try:
        from geo_infer_math.core.information_theory import (
            spatial_entropy,
            EntropyCalculator
        )
        
        if analysis_type == 'entropy':
            entropy = spatial_entropy(coordinates, values)
            return {'entropy': entropy, 'type': 'spatial_entropy'}
        else:
            return {'error': f'Analysis type {analysis_type} not yet implemented'}
    except ImportError:
        logger.warning("Information theory not available")
        return {'error': 'Information theory not available'}

def public_health_workflow(neighborhood_coords: np.ndarray,
                         health_metrics: np.ndarray,
                         socioeconomic_features: np.ndarray) -> Dict[str, Any]:
    """
    Execute a standard public health workflow.

    Args:
        neighborhood_coords: Neighborhood coordinates
        health_metrics: Health outcome measurements
        socioeconomic_features: Socioeconomic indicator features

    Returns:
        Public health analysis results
    """
    data = {
        'coordinates': neighborhood_coords,
        'health_metrics': health_metrics,
        'socioeconomic_features': socioeconomic_features
    }

    analysis_steps = [
        {
            'name': 'health_clusters',
            'module': 'spatial_statistics',
            'function': 'moran_i',
            'parameters': {'method': 'knn', 'k': 5}
        },
        {
            'name': 'health_regression',
            'module': 'regression',
            'function': 'spatial_regression',
            'parameters': {'model_type': 'sar'}
        }
    ]

    return create_integrated_workflow(analysis_steps, data)
