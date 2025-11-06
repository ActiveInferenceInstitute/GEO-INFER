"""
Unit tests for image classifier.
"""

import numpy as np
import pytest

from geo_infer_ai.models.cv.image_classifier import ImageClassifier


class TestImageClassifier:
    """Test ImageClassifier class."""

    @pytest.fixture
    def image_data_2d(self) -> tuple:
        """Create 2D image test data (already flattened)."""
        np.random.seed(42)
        X = np.random.randn(50, 100)  # 50 samples, 100 features
        y = np.random.randint(0, 3, 50)
        return X, y

    @pytest.fixture
    def image_data_3d(self) -> tuple:
        """Create 3D image test data (grayscale)."""
        np.random.seed(42)
        X = np.random.randn(50, 10, 10)  # 50 samples, 10x10 images
        y = np.random.randint(0, 3, 50)
        return X, y

    @pytest.fixture
    def image_data_4d(self) -> tuple:
        """Create 4D image test data (RGB)."""
        np.random.seed(42)
        X = np.random.randn(50, 10, 10, 3)  # 50 samples, 10x10x3 images
        y = np.random.randint(0, 3, 50)
        return X, y

    def test_init_random_forest(self) -> None:
        """Test initialization with Random Forest."""
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        assert classifier.model_type == "random_forest"
        assert classifier.model is not None

    def test_init_neural_network(self) -> None:
        """Test initialization with Neural Network."""
        classifier = ImageClassifier(model_type="neural_network", n_classes=3)
        assert classifier.model_type == "neural_network"
        assert classifier.model is not None

    def test_init_invalid_type(self) -> None:
        """Test initialization with invalid model type."""
        with pytest.raises(ValueError, match="Unknown model_type"):
            ImageClassifier(model_type="invalid")

    def test_fit_predict_2d(self, image_data_2d: tuple) -> None:
        """Test fit and predict with 2D data."""
        X, y = image_data_2d
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        predictions = classifier.predict(X)
        assert len(predictions) == len(y)
        assert all(pred in [0, 1, 2] for pred in predictions)

    def test_fit_predict_3d(self, image_data_3d: tuple) -> None:
        """Test fit and predict with 3D data (grayscale images)."""
        X, y = image_data_3d
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        predictions = classifier.predict(X)
        assert len(predictions) == len(y)

    def test_fit_predict_4d(self, image_data_4d: tuple) -> None:
        """Test fit and predict with 4D data (RGB images)."""
        X, y = image_data_4d
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        predictions = classifier.predict(X)
        assert len(predictions) == len(y)

    def test_predict_proba(self, image_data_2d: tuple) -> None:
        """Test probability predictions."""
        X, y = image_data_2d
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        probabilities = classifier.predict_proba(X)
        assert probabilities.shape == (len(X), 3)
        assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6)

    def test_predict_proba_neural_network(self, image_data_2d: tuple) -> None:
        """Test probability predictions with neural network."""
        X, y = image_data_2d
        classifier = ImageClassifier(model_type="neural_network", n_classes=3)
        classifier.fit(X, y)

        probabilities = classifier.predict_proba(X)
        assert probabilities.shape == (len(X), 3)
        assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6)

    def test_feature_importance(self, image_data_2d: tuple) -> None:
        """Test feature importance extraction."""
        X, y = image_data_2d
        classifier = ImageClassifier(model_type="random_forest", n_classes=3)
        classifier.fit(X, y)

        importance = classifier.get_feature_importance()
        assert importance is not None
        assert len(importance) == X.shape[1]
        assert all(imp >= 0 for imp in importance)

    def test_predict_before_fit(self, image_data_2d: tuple) -> None:
        """Test that prediction fails before training."""
        from sklearn.exceptions import NotFittedError
        
        X, y = image_data_2d
        classifier = ImageClassifier(model_type="random_forest")

        # sklearn raises NotFittedError, which our code converts to ValueError
        with pytest.raises((ValueError, NotFittedError)):
            classifier.predict(X)

