"""
Unit tests for cross-validation and hyperparameter search.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from geo_infer_ai.core.training import ModelTrainer, TrainingConfig


class TestCrossValidation:
    """Test cross-validation functionality."""

    @pytest.fixture
    def trainer(self) -> ModelTrainer:
        return ModelTrainer(TrainingConfig(save_best_model=False))

    @pytest.fixture
    def classification_data(self) -> tuple:
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        return X, y

    @pytest.fixture
    def regression_data(self) -> tuple:
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = 2.0 * X[:, 0] + X[:, 1] + np.random.randn(100) * 0.3
        return X, y

    def test_cross_validate_classification(
        self, trainer: ModelTrainer, classification_data: tuple
    ) -> None:
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        result = trainer.cross_validate(model, X, y, n_splits=3, task_type="classification")

        assert result['n_splits'] == 3
        assert result['task_type'] == 'classification'
        assert len(result['fold_results']) == 3
        assert 'accuracy_mean' in result['aggregate']
        assert 'accuracy_std' in result['aggregate']
        assert 0.0 <= result['aggregate']['accuracy_mean'] <= 1.0

    def test_cross_validate_regression(
        self, trainer: ModelTrainer, regression_data: tuple
    ) -> None:
        X, y = regression_data
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        result = trainer.cross_validate(model, X, y, n_splits=5, task_type="regression")

        assert result['n_splits'] == 5
        assert len(result['fold_results']) == 5
        assert 'r2_mean' in result['aggregate']
        assert 'rmse_mean' in result['aggregate']

    def test_cross_validate_stratified(
        self, trainer: ModelTrainer, classification_data: tuple
    ) -> None:
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        result = trainer.cross_validate(
            model, X, y, n_splits=3, task_type="classification", stratified=True
        )

        assert len(result['fold_results']) == 3
        for fold in result['fold_results']:
            assert 'accuracy' in fold

    def test_hyperparameter_search(
        self, trainer: ModelTrainer, classification_data: tuple
    ) -> None:
        X, y = classification_data
        param_grid = {
            'n_estimators': [5, 10],
            'max_depth': [3, 5],
        }
        result = trainer.hyperparameter_search(
            RandomForestClassifier, param_grid, X, y,
            task_type="classification", n_splits=2,
        )

        assert 'best_params' in result
        assert 'best_score' in result
        assert 'all_results' in result
        assert result['n_combinations'] == 4
        assert result['best_params']['n_estimators'] in [5, 10]
        assert 0.0 <= result['best_score'] <= 1.0

    def test_split_data_basic(self, trainer: ModelTrainer) -> None:
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randn(100)

        splits = trainer.split_data(X, y, test_size=0.2, val_size=0.1)

        assert 'X_train' in splits
        assert 'X_val' in splits
        assert 'X_test' in splits
        assert 'y_train' in splits
        assert 'y_val' in splits
        assert 'y_test' in splits
        assert len(splits['X_test']) == 20
        total = len(splits['X_train']) + len(splits['X_val']) + len(splits['X_test'])
        assert total == 100

    def test_split_data_no_validation(self, trainer: ModelTrainer) -> None:
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = np.random.randn(50)

        splits = trainer.split_data(X, y, test_size=0.2, val_size=0.0)

        assert len(splits['X_test']) == 10
        assert len(splits['X_val']) == 0
        assert len(splits['X_train']) == 40
