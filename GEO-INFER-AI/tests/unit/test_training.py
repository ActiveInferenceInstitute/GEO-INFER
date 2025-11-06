"""
Unit tests for model training functionality.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from geo_infer_ai.core.training import ModelTrainer, TrainingConfig


class TestTrainingConfig:
    """Test TrainingConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = TrainingConfig()
        assert config.batch_size == 32
        assert config.epochs == 100
        assert config.learning_rate == 0.001
        assert config.validation_split == 0.2

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        with pytest.raises(ValueError, match="batch_size must be positive"):
            TrainingConfig(batch_size=-1)

        with pytest.raises(ValueError, match="epochs must be positive"):
            TrainingConfig(epochs=0)

        with pytest.raises(ValueError, match="learning_rate must be between"):
            TrainingConfig(learning_rate=2.0)

        with pytest.raises(ValueError, match="validation_split must be between"):
            TrainingConfig(validation_split=1.5)


class TestModelTrainer:
    """Test ModelTrainer class."""

    @pytest.fixture
    def trainer(self) -> ModelTrainer:
        """Create a trainer instance."""
        config = TrainingConfig(validation_split=0.2, save_best_model=False)
        return ModelTrainer(config)

    @pytest.fixture
    def classification_data(self) -> tuple:
        """Create classification test data."""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randint(0, 3, 100)
        return X, y

    @pytest.fixture
    def regression_data(self) -> tuple:
        """Create regression test data."""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randn(100)
        return X, y

    def test_train_classifier(self, trainer: ModelTrainer, classification_data: tuple) -> None:
        """Test classifier training."""
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)

        results = trainer.train_classifier(model, X, y)

        assert "accuracy" in results
        assert "classification_report" in results
        assert "model" in results
        assert results["accuracy"] >= 0.0
        assert results["accuracy"] <= 1.0

    def test_train_regressor(self, trainer: ModelTrainer, regression_data: tuple) -> None:
        """Test regressor training."""
        X, y = regression_data
        model = RandomForestRegressor(n_estimators=10, random_state=42)

        results = trainer.train_regressor(model, X, y)

        assert "mse" in results
        assert "mae" in results
        assert "rmse" in results
        assert "r2" in results
        assert "model" in results
        assert results["r2"] <= 1.0

    def test_evaluate_classifier(self, trainer: ModelTrainer, classification_data: tuple) -> None:
        """Test classifier evaluation."""
        X, y = classification_data
        X_train, X_test = X[:80], X[80:]
        y_train, y_test = y[:80], y[80:]

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        results = trainer.evaluate_model(model, X_test, y_test, task_type="classification")

        assert "accuracy" in results
        assert "classification_report" in results
        assert "predictions" in results
        assert len(results["predictions"]) == len(y_test)

    def test_evaluate_regressor(self, trainer: ModelTrainer, regression_data: tuple) -> None:
        """Test regressor evaluation."""
        X, y = regression_data
        X_train, X_test = X[:80], X[80:]
        y_train, y_test = y[:80], y[80:]

        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        results = trainer.evaluate_model(model, X_test, y_test, task_type="regression")

        assert "mse" in results
        assert "mae" in results
        assert "rmse" in results
        assert "r2" in results
        assert "predictions" in results
        assert len(results["predictions"]) == len(y_test)

    def test_save_and_load_model(self, trainer: ModelTrainer, classification_data: tuple, tmp_path) -> None:
        """Test model saving and loading."""
        X, y = classification_data
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        model_path = tmp_path / "test_model.pkl"
        trainer._save_model(model, model_path)

        assert model_path.exists()

        loaded_model = trainer.load_model(model_path)
        assert loaded_model is not None
        assert hasattr(loaded_model, "predict")


