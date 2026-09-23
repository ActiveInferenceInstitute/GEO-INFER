"""Tests for bioregional economics modules."""


class TestEcosystemServices:
    """Tests for ecosystem services valuation."""

    def test_import_ecosystem_services(self) -> None:
        from geo_infer_econ.bioregional.ecosystem_services import (
            EcosystemServicesValuation,
        )

        esv = EcosystemServicesValuation()
        assert esv is not None

    def test_ecosystem_services_valuation_computes_values(self) -> None:
        from geo_infer_econ.bioregional.ecosystem_services import (
            EcosystemServicesValuation,
        )

        esv = EcosystemServicesValuation(
            config={
                "service_values": {"provisioning": {"food": 100.0}},
                "discount_rate": 0.05,
                "time_horizon": 10,
            }
        )

        result = esv.estimate_value(
            [{"category": "provisioning", "type": "food", "area_ha": 2.0}]
        )

        assert result["provisioning.food"] == 200.0
        assert result["total_annual"] == 200.0
        expected_npv = 200.0 * (1 - (1 + 0.05) ** -10) / 0.05
        assert abs(result["total_npv"] - expected_npv) < 0.01


class TestNaturalCapital:
    """Tests for natural capital accounting."""

    def test_import_natural_capital(self) -> None:
        from geo_infer_econ.bioregional.natural_capital import NaturalCapitalAccounting

        nca = NaturalCapitalAccounting()
        assert nca is not None


class TestCircularEconomy:
    """Tests for circular economy models."""

    def test_import_circular_economy(self) -> None:
        from geo_infer_econ.bioregional.circular_economy import CircularEconomyModels

        cem = CircularEconomyModels()
        assert cem is not None


class TestSustainabilityMetrics:
    """Tests for sustainability metrics."""

    def test_import_sustainability_metrics(self) -> None:
        from geo_infer_econ.bioregional.sustainability_metrics import (
            SustainabilityIndicators,
        )

        sm = SustainabilityIndicators()
        assert sm is not None
