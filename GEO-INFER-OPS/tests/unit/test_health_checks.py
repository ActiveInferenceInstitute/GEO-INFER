"""
Unit tests for health check functionality.
"""

import pytest
import asyncio
from geo_infer_ops.health.checks import HealthChecker, HealthStatus, HealthCheck


class TestHealthChecker:
    """Test HealthChecker class."""

    @pytest.fixture
    def health_checker(self) -> HealthChecker:
        """Create a health checker instance."""
        return HealthChecker(
            check_interval_seconds=60,
            timeout_seconds=5,
            enable_system_checks=True,
        )

    @pytest.mark.asyncio
    async def test_check_system_resources(self, health_checker: HealthChecker) -> None:
        """Test system resource checking."""
        check = await health_checker.check_system_resources()

        assert check.name == "system_resources"
        assert check.status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        ]
        assert "cpu_percent" in check.details
        assert "memory_percent" in check.details

    @pytest.mark.asyncio
    async def test_check_service(self, health_checker: HealthChecker) -> None:
        """Test service health checking."""
        def healthy_service():
            return True

        check = await health_checker.check_service("test_service", healthy_service)

        assert check.name == "service_test_service"
        assert check.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_register_check(self, health_checker: HealthChecker) -> None:
        """Test registering custom health checks."""
        def custom_check():
            return {"status": HealthStatus.HEALTHY, "message": "OK"}

        health_checker.register_check("custom", custom_check)

        assert "custom" in health_checker.custom_checks

    @pytest.mark.asyncio
    async def test_run_all_checks(self, health_checker: HealthChecker) -> None:
        """Test running all health checks."""
        def healthy_check():
            return True

        health_checker.register_check("test_check", healthy_check)

        results = await health_checker.run_all_checks()

        assert "status" in results
        assert "checks" in results
        assert "summary" in results
        assert results["summary"]["total"] >= 1

    def test_get_health_status(self, health_checker: HealthChecker) -> None:
        """Test synchronous health status retrieval."""
        def healthy_check():
            return True

        health_checker.register_check("test_check", healthy_check)

        status = health_checker.get_health_status()

        assert "status" in status
        assert "checks" in status


