"""
Integration tests for ML pipelines.
"""

import numpy as np
import pytest

from geo_infer_ai.core.training import ModelTrainer, TrainingConfig
from geo_infer_ai.models.cv.image_classifier import ImageClassifier
from geo_infer_ai.models.predictive.spatial_predictor import SpatialPredictor
from geo_infer_ai.pipelines.mlflow_integration import MLflowPipeline
from geo_infer_ai.preprocessing.feature_engineering import GeospatialFeatureEngineer


class TestEndToEndPipeline:
    """Test end-to-end ML pipelines."""

    @pytest.fixture
    def classification_data(self) -> tuple:
        """Create classification test data."""
        np.random.seed(42)
        X = np.random.randn(100, 20)
        y = np.random.randint(0, 3, 100)
        return X, y

    @pytest.fixture
    def regression_data(self) -> tuple:
        """Create regression test data."""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randn(100)
        coordinates = np.random.randn(100, 2)
        return X, y, coordinates

    def test_classification_pipeline(self, classification_data: tuple) -> None:
        """Test complete classification pipeline."""
        X, y = classification_data

        # Feature engineering
        engineer = GeospatialFeatureEngineer(normalize=True)
        X_processed = engineer.fit_transform(X)

        # Model training
        config = TrainingConfig(validation_split=0.2, save_best_model=False)
        trainer = ModelTrainer(config)

        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        results = trainer.train_classifier(classifier, X_processed, y)

        assert "accuracy" in results
        assert results["accuracy"] >= 0.0

    def test_regression_pipeline(self, regression_data: tuple) -> None:
        """Test complete regression pipeline."""
        X, y, coordinates = regression_data

        # Feature engineering with spatial features
        engineer = GeospatialFeatureEngineer(normalize=True)
        X_processed = engineer.fit_transform(X, coordinates=coordinates)

        # Model training
        config = TrainingConfig(validation_split=0.2, save_best_model=False)
        trainer = ModelTrainer(config)

        predictor = SpatialPredictor(
            model_type="random_forest", include_spatial_features=False
        )
        results = trainer.train_regressor(predictor, X_processed, y)

        assert "r2" in results
        assert "rmse" in results

    def test_mlflow_pipeline_disabled(self, classification_data: tuple) -> None:
        """Test MLflow pipeline when disabled."""
        X, y = classification_data

        pipeline = MLflowPipeline(enabled=False)
        pipeline.start_run(run_name="test_run")

        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        # Should not raise errors even if MLflow is not available
        pipeline.log_model(classifier, "model")
        pipeline.end_run()

    def test_feature_engineering_integration(self, regression_data: tuple) -> None:
        """Test feature engineering integration with models."""
        X, y, coordinates = regression_data

        # Create features
        engineer = GeospatialFeatureEngineer(normalize=True)
        X_processed = engineer.fit_transform(X, coordinates=coordinates)

        # Train model
        predictor = SpatialPredictor(
            model_type="random_forest", include_spatial_features=False
        )
        predictor.fit(X_processed, y)

        # Make predictions
        X_test = X[:10]
        coords_test = coordinates[:10]
        X_test_processed = engineer.transform(X_test, coordinates=coords_test)
        predictions = predictor.predict(X_test_processed)

        assert len(predictions) == len(X_test)
        assert all(np.isfinite(pred) for pred in predictions)



