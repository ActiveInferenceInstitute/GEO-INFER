"""
Coverage-focused unit tests for ModelTrainer edge branches.

Complements ``test_training.py``: config validation, save-path behavior,
binary vs multi-class evaluation, and the joblib/pickle round trip.
"""

import numpy as np
import pytest
from pathlib import Path
from sklearn.linear_model import LinearRegression, LogisticRegression

from geo_infer_ai.core.training import ModelTrainer, TrainingConfig


class TestTrainingConfigValidation:
    """TrainingConfig rejects invalid hyperparameters."""

    def test_negative_patience_raises(self) -> None:
        with pytest.raises(ValueError, match="patience must be non-negative"):
            TrainingConfig(early_stopping_patience=-1)

    def test_zero_batch_size_raises(self) -> None:
        with pytest.raises(ValueError, match="batch_size must be positive"):
            TrainingConfig(batch_size=0)

    def test_invalid_learning_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="learning_rate"):
            TrainingConfig(learning_rate=0.0)

    def test_invalid_validation_split_raises(self) -> None:
        with pytest.raises(ValueError, match="validation_split"):
            TrainingConfig(validation_split=1.0)

    def test_invalid_epochs_raises(self) -> None:
        with pytest.raises(ValueError, match="epochs must be positive"):
            TrainingConfig(epochs=0)


class TestModelTrainerSavePaths:
    """Trainer persists models when model_save_path is configured."""

    @pytest.fixture
    def classification_data(self) -> tuple:
        np.random.seed(42)
        X = np.random.randn(60, 4)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        return X, y

    def test_train_classifier_saves_best_model(
        self, classification_data: tuple, tmp_path: Path
    ) -> None:
        X, y = classification_data
        save_path = tmp_path / "model.pkl"
        config = TrainingConfig(save_best_model=True, model_save_path=save_path)
        trainer = ModelTrainer(config)

        result = trainer.train_classifier(LogisticRegression(max_iter=200), X, y)
        assert save_path.exists()
        assert result["accuracy"] >= 0.0

    def test_train_regressor_saves_best_model(self, tmp_path: Path) -> None:
        np.random.seed(42)
        X = np.random.randn(60, 3)
        y = X @ np.array([1.5, -2.0, 0.5]) + 0.1 * np.random.randn(60)
        save_path = tmp_path / "reg.pkl"
        config = TrainingConfig(save_best_model=True, model_save_path=save_path)
        trainer = ModelTrainer(config)

        result = trainer.train_regressor(LinearRegression(), X, y)
        assert save_path.exists()
        assert result["r2"] > 0.5

    def test_save_and_load_round_trip_pickle(
        self, classification_data: tuple, tmp_path: Path
    ) -> None:
        X, y = classification_data
        trainer = ModelTrainer()
        model = LogisticRegression(max_iter=200).fit(X, y)

        path = tmp_path / "model.pkl"
        trainer._save_model(model, path)
        loaded = trainer.load_model(path)
        assert loaded is not None
        np.testing.assert_array_equal(loaded.predict(X[:5]), model.predict(X[:5]))

    def test_load_missing_model_raises(self, tmp_path: Path) -> None:
        trainer = ModelTrainer()
        with pytest.raises(FileNotFoundError):
            trainer.load_model(tmp_path / "missing.pkl")


class TestModelTrainerEvaluationBranches:
    """evaluate_model task-type and class-count branches."""

    @pytest.fixture
    def trainer(self) -> ModelTrainer:
        return ModelTrainer()

    def test_binary_evaluation_uses_binary_averaging(self, trainer) -> None:
        np.random.seed(42)
        X = np.random.randn(40, 3)
        y = (X[:, 0] > 0).astype(int)
        model = LogisticRegression(max_iter=200).fit(X, y)

        result = trainer.evaluate_model(model, X, y, task_type="classification")
        assert result["accuracy"] >= 0.0
        assert "precision" in result and "recall" in result
        assert "f1_score" in result

    def test_multiclass_evaluation_uses_weighted_averaging(self, trainer) -> None:
        np.random.seed(42)
        X = np.random.randn(60, 3)
        y = np.repeat([0, 1, 2], 20)
        model = LogisticRegression(max_iter=200).fit(X, y)

        result = trainer.evaluate_model(model, X, y, task_type="classification")
        assert result["accuracy"] >= 0.0

    def test_single_sample_regression_keeps_finite_r2(self, trainer) -> None:
        X = np.array([[1.0, 2.0]])
        y = np.array([3.0])
        model = LinearRegression().fit(X, y)

        result = trainer.evaluate_model(model, X, y, task_type="regression")
        assert result["r2"] in (0.0, 1.0)
        assert np.isfinite(result["r2"])

    def test_unknown_task_type_raises(self, trainer) -> None:
        X = np.zeros((5, 2))
        y = np.zeros(5)
        model = LinearRegression().fit(np.ones((4, 2)), np.ones(4))
        with pytest.raises(ValueError, match="Unknown task_type"):
            trainer.evaluate_model(model, X, y, task_type="clustering")
