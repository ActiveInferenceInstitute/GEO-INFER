"""
Feature engineering for geospatial machine learning.

This module provides specialized preprocessing and feature engineering
for geospatial data, including handling spatial autocorrelation, creating
spatial features, and data augmentation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class GeospatialFeatureEngineer:
    """
    Feature engineering for geospatial ML datasets.

    Provides methods for creating spatial features, handling spatial
    autocorrelation, and preparing geospatial data for ML models.
    """

    def __init__(self, normalize: bool = True, handle_spatial_autocorr: bool = True) -> None:
        """
        Initialize the feature engineer.

        Args:
            normalize: Whether to normalize features
            handle_spatial_autocorr: Whether to account for spatial autocorrelation
        """
        self.normalize = normalize
        self.handle_spatial_autocorr = handle_spatial_autocorr
        self.scaler: Optional[StandardScaler] = None
        self.feature_names_: Optional[List[str]] = None

    def create_spatial_features(
        self,
        coordinates: np.ndarray,
        include_distances: bool = True,
        include_angles: bool = False,
    ) -> pd.DataFrame:
        """
        Create spatial features from coordinates.

        Args:
            coordinates: Spatial coordinates (n_samples, 2) [lon, lat]
            include_distances: Whether to include distance-based features
            include_angles: Whether to include angular features

        Returns:
            DataFrame with spatial features
        """
        logger.info(f"Creating spatial features for {len(coordinates)} samples")

        lon = coordinates[:, 0]
        lat = coordinates[:, 1]

        features: Dict[str, np.ndarray] = {
            "longitude": lon,
            "latitude": lat,
        }

        if include_distances:
            # Distance from centroid
            centroid_lon = np.mean(lon)
            centroid_lat = np.mean(lat)
            features["distance_from_centroid"] = np.sqrt(
                (lon - centroid_lon) ** 2 + (lat - centroid_lat) ** 2
            )

            # Distance from origin
            features["distance_from_origin"] = np.sqrt(lon ** 2 + lat ** 2)

        if include_angles:
            # Angle from centroid
            centroid_lon = np.mean(lon)
            centroid_lat = np.mean(lat)
            features["angle_from_centroid"] = np.arctan2(
                lat - centroid_lat, lon - centroid_lon
            )

        df = pd.DataFrame(features)
        return df

    def create_temporal_features(
        self, timestamps: Union[np.ndarray, pd.Series, List]
    ) -> pd.DataFrame:
        """
        Create temporal features from timestamps.

        Args:
            timestamps: Timestamp data

        Returns:
            DataFrame with temporal features
        """
        logger.info(f"Creating temporal features for {len(timestamps)} samples")

        if not isinstance(timestamps, pd.Series):
            timestamps = pd.Series(timestamps)

        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(timestamps):
            timestamps = pd.to_datetime(timestamps)

        features = pd.DataFrame(
            {
                "year": timestamps.dt.year,
                "month": timestamps.dt.month,
                "day": timestamps.dt.day,
                "dayofweek": timestamps.dt.dayofweek,
                "dayofyear": timestamps.dt.dayofyear,
                "quarter": timestamps.dt.quarter,
                "is_weekend": (timestamps.dt.dayofweek >= 5).astype(int),
            }
        )

        # Cyclical encoding for periodic features
        features["month_sin"] = np.sin(2 * np.pi * features["month"] / 12)
        features["month_cos"] = np.cos(2 * np.pi * features["month"] / 12)
        features["dayofweek_sin"] = np.sin(2 * np.pi * features["dayofweek"] / 7)
        features["dayofweek_cos"] = np.cos(2 * np.pi * features["dayofweek"] / 7)

        return features

    def fit_transform(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        coordinates: Optional[np.ndarray] = None,
        timestamps: Optional[Union[np.ndarray, pd.Series, List]] = None,
    ) -> np.ndarray:
        """
        Fit the feature engineer and transform data.

        Args:
            X: Input features
            coordinates: Optional spatial coordinates
            timestamps: Optional temporal data

        Returns:
            Transformed feature matrix
        """
        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X)
        else:
            X_df = X.copy()

        # Reset index to ensure alignment
        X_df = X_df.reset_index(drop=True)

        # Add spatial features
        if coordinates is not None:
            spatial_features = self.create_spatial_features(coordinates)
            # Reset index to ensure alignment
            spatial_features = spatial_features.reset_index(drop=True)
            X_df = pd.concat([X_df, spatial_features], axis=1, ignore_index=False)

        # Add temporal features
        if timestamps is not None:
            temporal_features = self.create_temporal_features(timestamps)
            # Reset index to ensure alignment
            temporal_features = temporal_features.reset_index(drop=True)
            X_df = pd.concat([X_df, temporal_features], axis=1, ignore_index=False)

        # Convert all column names to strings for sklearn compatibility
        X_df.columns = X_df.columns.astype(str)

        # Store feature names
        self.feature_names_ = list(X_df.columns)

        # Normalize if requested
        if self.normalize:
            self.scaler = StandardScaler()
            X_transformed = self.scaler.fit_transform(X_df)
        else:
            X_transformed = X_df.values

        logger.info(
            f"Feature engineering completed. "
            f"Original features: {X.shape[1] if hasattr(X, 'shape') else len(X.columns)}, "
            f"Final features: {X_transformed.shape[1]}"
        )

        return X_transformed

    def transform(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        coordinates: Optional[np.ndarray] = None,
        timestamps: Optional[Union[np.ndarray, pd.Series, List]] = None,
    ) -> np.ndarray:
        """
        Transform data using fitted feature engineer.

        Args:
            X: Input features
            coordinates: Optional spatial coordinates
            timestamps: Optional temporal data

        Returns:
            Transformed feature matrix
        """
        if self.scaler is None and self.normalize:
            raise ValueError(
                "Feature engineer must be fitted before transform. Use fit_transform first."
            )

        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X)
        else:
            X_df = X.copy()

        # Reset index to ensure alignment
        X_df = X_df.reset_index(drop=True)

        # Add spatial features
        if coordinates is not None:
            spatial_features = self.create_spatial_features(coordinates)
            # Reset index to ensure alignment
            spatial_features = spatial_features.reset_index(drop=True)
            X_df = pd.concat([X_df, spatial_features], axis=1, ignore_index=False)

        # Add temporal features
        if timestamps is not None:
            temporal_features = self.create_temporal_features(timestamps)
            # Reset index to ensure alignment
            temporal_features = temporal_features.reset_index(drop=True)
            X_df = pd.concat([X_df, temporal_features], axis=1, ignore_index=False)

        # Convert all column names to strings for sklearn compatibility
        X_df.columns = X_df.columns.astype(str)

        # Normalize if fitted
        if self.normalize and self.scaler is not None:
            X_transformed = self.scaler.transform(X_df)
        else:
            X_transformed = X_df.values

        return X_transformed

    def get_feature_names(self) -> Optional[List[str]]:
        """
        Get feature names.

        Returns:
            List of feature names or None
        """
        return self.feature_names_

