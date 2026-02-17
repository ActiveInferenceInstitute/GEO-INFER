"""Tests for delivery module."""

import pytest
from geo_infer_log.core.delivery import (
    LastMileRouter,
    DeliveryScheduler,
    ServiceAreaAnalyzer,
)


class TestLastMileRouter:
    """Tests for last-mile routing."""

    def test_import(self) -> None:
        assert LastMileRouter is not None

    def test_initialization(self) -> None:
        router = LastMileRouter()
        assert router is not None


class TestDeliveryScheduler:
    """Tests for delivery scheduling."""

    def test_import(self) -> None:
        assert DeliveryScheduler is not None

    def test_initialization(self) -> None:
        router = LastMileRouter()
        scheduler = DeliveryScheduler(router=router)
        assert scheduler is not None
        assert scheduler.router is router


class TestServiceAreaAnalyzer:
    """Tests for service area analysis."""

    def test_import(self) -> None:
        assert ServiceAreaAnalyzer is not None

    def test_initialization(self) -> None:
        analyzer = ServiceAreaAnalyzer()
        assert analyzer is not None
