"""
API endpoints for SPM analysis

This module provides REST API endpoints for performing SPM analysis
through web services, enabling integration with web applications
and distributed computing environments.
"""

from typing import Dict, List, Optional, Any
import json

from ..models.data_models import SPMData, SPMResult, ContrastResult
from ..core.glm import fit_glm
from ..core.contrasts import contrast
from ..core.rft import compute_spm


class SPMAPI:
    """
    REST API interface for SPM analysis.

    Provides endpoints for data upload, model fitting, statistical testing,
    and result retrieval in a web service format.
    """

    def __init__(self):
        self.datasets = {}  # Store uploaded datasets
        self.results = {}   # Store analysis results
        self.next_id = 1

    def upload_data(self, data: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
        """
        Upload geospatial data for analysis.

        Args:
            data: Data dictionary containing coordinates and values
            format: Data format ('json', 'csv', 'geojson')

        Returns:
            Response with dataset ID
        """
        try:
            dataset_id = f"dataset_{self.next_id}"
            self.next_id += 1

            # Convert to SPMData
            if format == 'json':
                spm_data = self._json_to_spmdata(data)
            elif format == 'csv':
                spm_data = self._csv_to_spmdata(data)
            else:
                raise ValueError(f"Unsupported format: {format}")

            self.datasets[dataset_id] = spm_data

            return {
                'status': 'success',
                'dataset_id': dataset_id,
                'n_points': spm_data.n_points,
                'has_temporal': spm_data.has_temporal
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def fit_model(self, dataset_id: str, design_spec: Dict[str, Any],
                 method: str = 'OLS') -> Dict[str, Any]:
        """
        Fit GLM to uploaded dataset.

        Args:
            dataset_id: ID of uploaded dataset
            design_spec: Design matrix specification
            method: Fitting method

        Returns:
            Response with model fit results
        """
        try:
            if dataset_id not in self.datasets:
                raise ValueError(f"Dataset {dataset_id} not found")

            data = self.datasets[dataset_id]

            # Create design matrix from specification
            design_matrix = self._create_design_from_spec(design_spec, data)

            # Fit model
            result = fit_glm(data, design_matrix, method=method)

            result_id = f"result_{self.next_id}"
            self.next_id += 1
            self.results[result_id] = result

            return {
                'status': 'success',
                'result_id': result_id,
                'r_squared': result.model_diagnostics.get('r_squared', 0),
                'n_regressors': design_matrix.n_regressors
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def run_contrast(self, result_id: str, contrast_spec: Dict[str, Any],
                    correction: str = 'uncorrected') -> Dict[str, Any]:
        """
        Run statistical contrast on fitted model.

        Args:
            result_id: ID of fitted model results
            contrast_spec: Contrast specification
            correction: Multiple comparison correction method

        Returns:
            Response with contrast results
        """
        try:
            if result_id not in self.results:
                raise ValueError(f"Result {result_id} not found")

            model_result = self.results[result_id]

            # Create contrast
            if 'vector' in contrast_spec:
                contrast_obj = contrast(model_result, contrast_spec['vector'])
            elif 'string' in contrast_spec:
                contrast_obj = contrast(model_result, contrast_spec['string'])
            else:
                raise ValueError("Contrast specification must include 'vector' or 'string'")

            # Apply correction
            spm_result = compute_spm(model_result, contrast_obj, correction=correction)

            # Store updated result
            self.results[result_id] = model_result

            return {
                'status': 'success',
                'result_id': result_id,
                'contrast_name': contrast_obj.name if hasattr(contrast_obj, 'name') else 'unnamed',
                'correction_method': correction,
                'n_significant': spm_result.n_significant,
                'threshold': spm_result.threshold
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_results(self, result_id: str, format: str = 'summary') -> Dict[str, Any]:
        """
        Retrieve analysis results.

        Args:
            result_id: ID of analysis results
            format: Result format ('summary', 'full', 'visualization')

        Returns:
            Response with results
        """
        try:
            if result_id not in self.results:
                raise ValueError(f"Result {result_id} not found")

            result = self.results[result_id]

            if format == 'summary':
                return self._format_summary(result)
            elif format == 'full':
                return self._format_full(result)
            elif format == 'visualization':
                return self._format_visualization(result)
            else:
                raise ValueError(f"Unknown format: {format}")

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def list_datasets(self) -> Dict[str, Any]:
        """List all uploaded datasets."""
        return {
            'status': 'success',
            'datasets': list(self.datasets.keys()),
            'count': len(self.datasets)
        }

    def list_results(self) -> Dict[str, Any]:
        """List all analysis results."""
        return {
            'status': 'success',
            'results': list(self.results.keys()),
            'count': len(self.results)
        }

    def _json_to_spmdata(self, data: Dict[str, Any]) -> SPMData:
        """Convert JSON data to SPMData object."""
        from ..models.data_models import SPMData

        coordinates = np.array(data['coordinates'])
        data_values = np.array(data.get('data', []))

        return SPMData(
            data=data_values,
            coordinates=coordinates,
            time=data.get('time'),
            covariates=data.get('covariates', {}),
            metadata=data.get('metadata', {}),
            crs=data.get('crs', 'EPSG:4326')
        )

    def _csv_to_spmdata(self, data: Dict[str, Any]) -> SPMData:
        """Convert CSV-like data to SPMData object."""
        # Simplified CSV conversion
        from ..utils.data_io import load_csv_with_coords

        # Assume data is dictionary with CSV-like structure
        # This would need proper CSV parsing in real implementation
        raise NotImplementedError("CSV upload not implemented")

    def _create_design_from_spec(self, design_spec: Dict[str, Any], data: SPMData):
        """Create design matrix from API specification."""
        from ..utils.helpers import create_design_matrix

        return create_design_matrix(
            data,
            covariates=design_spec.get('covariates', []),
            factors=design_spec.get('factors', {}),
            intercept=design_spec.get('intercept', True)
        )

    def _format_summary(self, result: SPMResult) -> Dict[str, Any]:
        """Format results as summary."""
        return {
            'status': 'success',
            'result_type': 'SPMResult',
            'n_points': result.spm_data.n_points,
            'n_regressors': result.design_matrix.n_regressors,
            'r_squared': result.r_squared,
            'log_likelihood': result.log_likelihood,
            'n_contrasts': len(result.contrasts),
            'significant_contrasts': sum(1 for c in result.contrasts if c.n_significant > 0)
        }

    def _format_full(self, result: SPMResult) -> Dict[str, Any]:
        """Format full results."""
        return {
            'status': 'success',
            'result': {
                'beta_coefficients': result.beta_coefficients.tolist(),
                'residuals': result.residuals.tolist(),
                'model_diagnostics': result.model_diagnostics,
                'processing_metadata': result.processing_metadata,
                'contrasts': [
                    {
                        'name': getattr(c, 'name', 'unnamed'),
                        'n_significant': c.n_significant,
                        'correction_method': c.correction_method
                    } for c in result.contrasts
                ]
            }
        }

    def _format_visualization(self, result: SPMResult) -> Dict[str, Any]:
        """Format results for visualization."""
        # This would create visualization data structures
        # For now, return basic structure
        return {
            'status': 'success',
            'visualization_data': {
                'coordinates': result.spm_data.coordinates.tolist(),
                'beta_map': result.beta_coefficients.tolist() if result.beta_coefficients.ndim == 1
                           else result.beta_coefficients[:, 0].tolist(),
                'residuals': result.residuals.tolist()
            }
        }
