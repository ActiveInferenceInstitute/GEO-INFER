"""
Coverage-focused unit tests for GeospatialModelEvaluator edge branches.

Complements ``test_model_evaluation.py`` with the confusion-matrix
normalization modes, multi-class ROC-AUC, and classification spatial CV.
"""

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression, Ridge

from geo_infer_ai.core.model_evaluation import GeospatialModelEvaluator


class TestConfusionMatrixNormalizationModes:
    """compute_confusion_matrix normalization modes."""

    def setup_method(self) -> None:
        self.evaluator = GeospatialModelEvaluator()
        self.y_true = np.array([0, 0, 0, 1, 1, 1, 2, 2])
        self.y_pred = np.array([0, 1, 0, 1, 1, 2, 2, 2])

    def test_normalize_pred_columns_sum_to_one(self) -> None:
        result = self.evaluator.compute_confusion_matrix(
            self.y_true, self.y_pred, normalize="pred"
        )
        cm_norm = np.array(result["confusion_matrix_normalized"])
        col_sums = cm_norm.sum(axis=0)
        assert all(abs(s - 1.0) < 1e-6 or s == 0.0 for s in col_sums)

    def test_normalize_all_totals_sum_to_one(self) -> None:
        result = self.evaluator.compute_confusion_matrix(
            self.y_true, self.y_pred, normalize="all"
        )
        cm_norm = np.array(result["confusion_matrix_normalized"])
        assert abs(cm_norm.sum() - 1.0) < 1e-6

    def test_normalize_none_omits_normalized_matrix(self) -> None:
        result = self.evaluator.compute_confusion_matrix(self.y_true, self.y_pred)
        assert "confusion_matrix_normalized" not in result

    def test_per_class_statistics_are_consistent(self) -> None:
        result = self.evaluator.compute_confusion_matrix(self.y_true, self.y_pred)
        per_class = result["per_class"]
        assert set(per_class.keys()) == {"0", "1", "2"}
        for stats in per_class.values():
            tp = stats["true_positive"]
            fp = stats["false_positive"]
            expected_precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            assert stats["precision"] == pytest.approx(expected_precision)


class TestRocAucMultiClass:
    """compute_roc_auc multi-class and degenerate branches."""

    def setup_method(self) -> None:
        self.evaluator = GeospatialModelEvaluator()

    def test_binary_2d_scores_use_positive_column(self) -> None:
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_score = np.column_stack([np.linspace(0.9, 0.4, 6), np.linspace(0.1, 0.6, 6)])
        result = self.evaluator.compute_roc_auc(y_true, y_score)
        assert result["n_classes"] == 2
        assert result["roc_auc"] == pytest.approx(1.0)

    def test_multi_class_with_2d_scores(self) -> None:
        y_true = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        y_score = np.array(
            [
                [0.8, 0.1, 0.1],
                [0.7, 0.2, 0.1],
                [0.6, 0.2, 0.2],
                [0.1, 0.8, 0.1],
                [0.2, 0.7, 0.1],
                [0.1, 0.9, 0.0],
                [0.1, 0.1, 0.8],
                [0.0, 0.2, 0.8],
                [0.2, 0.1, 0.7],
            ]
        )
        result = self.evaluator.compute_roc_auc(y_true, y_score, multi_class="ovr")
        assert result["multi_class_strategy"] == "ovr"
        assert 0.0 <= result["roc_auc"] <= 1.0
        assert set(result["per_class_auc"].keys()) == {"0", "1", "2"}

    def test_multi_class_1d_scores_raise(self) -> None:
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_score = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        with pytest.raises(ValueError, match="must be 2D"):
            self.evaluator.compute_roc_auc(y_true, y_score)

    def test_single_class_returns_nan_with_error(self) -> None:
        y_true = np.array([1, 1, 1])
        y_score = np.array([0.5, 0.6, 0.7])
        result = self.evaluator.compute_roc_auc(y_true, y_score)
        assert np.isnan(result["roc_auc"])
        assert "Only one class" in result["error"]


class TestSpatialCrossValidation:
    """cross_validate_spatial classification branch and validation."""

    def test_classification_uses_accuracy(self) -> None:
        np.random.seed(7)
        centers = np.array([[0.0, 0.0], [500.0, 0.0], [1000.0, 0.0]])
        coords = np.vstack([c + np.random.randn(10, 2) for c in centers])
        # Labels tile across blocks so every fold's training set sees all
        # three classes; features are linearly separable from the label.
        y = np.tile([0, 1, 2], 10)
        X = y[:, None] + np.random.randn(30, 1) * 0.1

        model = LogisticRegression(max_iter=200)
        result = GeospatialModelEvaluator().cross_validate_spatial(
            model, X, y, coords, n_splits=3
        )
        assert len(result["scores"]) == 3
        # Separable features: every held-out block is predicted correctly
        assert all(score == 1.0 for score in result["scores"])
        assert 0.0 <= result["mean_score"] <= 1.0

    def test_n_splits_below_two_raises(self) -> None:
        X = np.zeros((5, 2))
        with pytest.raises(ValueError, match="at least 2"):
            GeospatialModelEvaluator().cross_validate_spatial(
                Ridge(), X, np.zeros(5), np.zeros((5, 2)), n_splits=1
            )

    def test_n_splits_above_sample_count_raises(self) -> None:
        X = np.zeros((4, 2))
        with pytest.raises(ValueError, match="cannot exceed"):
            GeospatialModelEvaluator().cross_validate_spatial(
                Ridge(), X, np.zeros(4), np.zeros((4, 2)), n_splits=5
            )
