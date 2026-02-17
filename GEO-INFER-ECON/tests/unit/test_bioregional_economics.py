"""Tests for bioregional economics modules."""

import numpy as np
import pytest


class TestEcosystemServices:
    """Tests for ecosystem services valuation."""

    def test_import_ecosystem_services(self) -> None:
        from geo_infer_econ.bioregional.ecosystem_services import (
            EcosystemServicesValuation,
        )
        esv = EcosystemServicesValuation()
        assert esv is not None

    def test_ecosystem_services_valuation_has_methods(self) -> None:
        from geo_infer_econ.bioregional.ecosystem_services import (
            EcosystemServicesValuation,
        )
        esv = EcosystemServicesValuation()
        assert hasattr(esv, "calculate_ecosystem_value") or hasattr(
            esv, "estimate_value"
        )


class TestNaturalCapital:
    """Tests for natural capital accounting."""

    def test_import_natural_capital(self) -> None:
        from geo_infer_econ.bioregional.natural_capital import NaturalCapitalAccounting
        nca = NaturalCapitalAccounting()
        assert nca is not None


class TestCircularEconomy:
    """Tests for circular economy models."""

    def test_import_circular_economy(self) -> None:
        from geo_infer_econ.bioregional.circular_economy import CircularEconomyModel
        cem = CircularEconomyModel()
        assert cem is not None


class TestSustainabilityMetrics:
    """Tests for sustainability metrics."""

    def test_import_sustainability_metrics(self) -> None:
        from geo_infer_econ.bioregional.sustainability_metrics import (
            SustainabilityMetrics,
        )
        sm = SustainabilityMetrics()
        assert sm is not None
