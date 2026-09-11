"""Regression tests for silent-fabrication fixes (GS-082, GS-083 ACT side)."""

import unittest
from unittest import mock

import numpy as np

from geo_infer_act.utils.math import matrix_log_det
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer


class TestMatrixLogDet(unittest.TestCase):
    """matrix_log_det must not silently report a positive log-det when det <= 0."""

    def test_indefinite_swap_matrix_returns_minus_inf(self):
        # det = -1
        result = matrix_log_det(np.array([[0.0, 1.0], [1.0, 0.0]]))
        self.assertEqual(result, -np.inf)

    def test_singular_matrix_returns_minus_inf(self):
        result = matrix_log_det(np.array([[1.0, 2.0], [2.0, 4.0]]))
        self.assertEqual(result, -np.inf)

    def test_positive_definite_is_correct_log_det(self):
        matrix = np.array([[2.0, 0.0], [0.0, 8.0]])
        self.assertAlmostEqual(matrix_log_det(matrix), np.log(16.0))


class TestObsBeliefCorrelationContract(unittest.TestCase):
    """Correlation dict must stay float-valued; no error sentinel."""

    def _analyzer(self):
        import tempfile

        return ActiveInferenceAnalyzer(tempfile.mkdtemp())

    def test_compute_failure_returns_empty_float_valued_dict(self):
        analyzer = self._analyzer()
        beliefs = np.random.default_rng(0).random((10, 2))
        observations = np.random.default_rng(1).random((10, 2))

        import geo_infer_act.utils.analysis as analysis_module

        with mock.patch.object(
            analysis_module.np, "corrcoef", side_effect=RuntimeError("boom")
        ):
            result = (
                analysis_module.ActiveInferenceAnalyzer._compute_obs_belief_correlation(
                    analyzer, beliefs, observations
                )
            )
        self.assertEqual(result, {})

    def test_happy_path_all_floats_no_nan(self):
        analyzer = self._analyzer()
        beliefs = np.random.default_rng(0).random((10, 2))
        observations = np.random.default_rng(1).random((10, 2))
        result = analyzer._compute_obs_belief_correlation(beliefs, observations)
        self.assertTrue(result)
        for value in result.values():
            self.assertIsInstance(value, float)
            self.assertFalse(np.isnan(value))


if __name__ == "__main__":
    unittest.main()
