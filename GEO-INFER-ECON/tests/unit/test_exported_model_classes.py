"""Behavioral tests for previously untested exported ECON classes (M4-01).

Covers EndogenousGrowthModels, RegionalConvergenceAnalysis,
TechnologyDiffusionModels, EcologicalEconomicsEngine and
BioregionalMarketDesign with ctor + representative-operation tests.
"""

import math

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from geo_infer_econ.bioregional.bioregional_markets import (
    BioregionalAsset,
    BioregionalMarketDesign,
    MarketParticipant,
)
from geo_infer_econ.bioregional.ecological_economics import EcologicalEconomicsEngine
from geo_infer_econ.macroeconomics.growth_models import (
    EndogenousGrowthModels,
    RegionProfile,
    RegionalConvergenceAnalysis,
    TechnologyDiffusionModels,
)


class TestEndogenousGrowthModels:
    """AK and Romer endogenous growth behaviour."""

    def test_ctor_defaults(self) -> None:
        model = EndogenousGrowthModels()
        assert model.model_type == "ak"
        assert model.parameters == {}
        assert model.solution_cache == {}

    def test_ak_model_growth_rate_hand_computed(self) -> None:
        """AK growth rate is g = s*A - δ."""
        model = EndogenousGrowthModels(model_type="ak")
        result = model.ak_model(A=0.5, s=0.3, delta=0.1)

        assert result["growth_rate"] == pytest.approx(0.3 * 0.5 - 0.1)
        assert result["model_type"] == "AK"
        assert result["productivity"] == 0.5
        assert result["savings_rate"] == 0.3
        assert result["depreciation_rate"] == 0.1

    def test_romer_model_balanced_growth_hand_computed(self) -> None:
        """Romer: g_A = γ·s_r·L and g = g_A / (1 - α)."""
        model = EndogenousGrowthModels()
        params = {
            "alpha": 0.33,
            "gamma": 0.1,
            "s_r": 0.05,
            "L": 1000,
            "A0": 1.0,
            "time_steps": 50,
        }
        result = model.romer_model(params)

        expected_ga = 0.1 * 0.05 * 1000
        expected_g = expected_ga / (1 - 0.33)
        assert result["technology_growth"] == pytest.approx(expected_ga)
        assert result["balanced_growth_rate"] == pytest.approx(expected_g)
        assert result["model_type"] == "Romer_1990"
        assert len(result["technology_path"]) == 50
        # Knowledge stock grows monotonically along the path.
        path = result["technology_path"]
        assert path[0] == 1.0
        assert path[-1] > path[0]
        # High growth triggers the resource-constraint limiter.
        analysis = result["balanced_growth_analysis"]
        assert analysis["growth_sustainability"]["sustainability_score"] == 0.8
        assert "resource_constraints" in analysis["growth_sustainability"][
            "limiting_factors"
        ]


class TestRegionalConvergenceAnalysis:
    """Beta and sigma convergence on constructed panel data."""

    @staticmethod
    def _beta_panel() -> pd.DataFrame:
        """Two regions growing exactly along g = 0.30 - 0.02·ln(gdp)."""
        rows = []
        for region_id, gdp_init in (("poor", 100.0), ("rich", 200.0)):
            growth = 0.30 - 0.02 * math.log(gdp_init)
            rows.append(
                {"region_id": region_id, "year": 2000, "gdp_per_capita": gdp_init}
            )
            rows.append(
                {
                    "region_id": region_id,
                    "year": 2010,
                    "gdp_per_capita": gdp_init * math.exp(growth * 10),
                }
            )
        return pd.DataFrame(rows)

    def test_beta_convergence_hand_computed(self) -> None:
        analysis = RegionalConvergenceAnalysis(self._beta_panel())
        result = analysis.beta_convergence_analysis(2000, 2010)

        # Two points determine the regression exactly: β = 0.02, α = 0.30.
        assert result["beta_coefficient"] == pytest.approx(0.02, rel=1e-6)
        assert result["alpha_coefficient"] == pytest.approx(0.30, rel=1e-6)
        assert result["r_squared"] == pytest.approx(1.0, abs=1e-9)
        assert result["convergence_rate"] == pytest.approx(0.02, rel=1e-6)
        assert result["half_life_years"] == pytest.approx(
            math.log(2) / 0.02, rel=1e-6
        )
        assert result["converging"]

    def test_sigma_convergence_declining_dispersion(self) -> None:
        """Poor region grows 5%/yr, rich 1%/yr → dispersion declines."""
        rows = []
        for year in range(4):
            rows.append(
                {"region_id": "a", "year": year,
                 "gdp_per_capita": 100.0 * math.exp(0.05 * year)}
            )
            rows.append(
                {"region_id": "b", "year": year,
                 "gdp_per_capita": 200.0 * math.exp(0.01 * year)}
            )
        analysis = RegionalConvergenceAnalysis(pd.DataFrame(rows))
        result = analysis.sigma_convergence_analysis()

        cv = result["time_series"]["coefficient_of_variation"]
        assert len(cv) == 4
        # pandas .std() is ddof=1, so CV = √2·|A − B| / (A + B).
        gdp_a, gdp_b = 100.0 * math.exp(0.15), 200.0 * math.exp(0.03)
        assert cv.iloc[0] == pytest.approx(math.sqrt(2) * 100.0 / 300.0, rel=1e-6)
        assert cv.iloc[-1] == pytest.approx(
            math.sqrt(2) * (gdp_b - gdp_a) / (gdp_b + gdp_a), rel=1e-6
        )
        assert result["trend_slope"] < 0
        assert result["converging"]


def _diffusion_region(region_id: str, population: float) -> RegionProfile:
    return RegionProfile(
        region_id=region_id,
        initial_capital=100.0,
        initial_output=50.0,
        population=population,
        technology_level=1.0,
        location=(40.0, -95.0),
        institutions={"quality": 0.5},
        natural_resources={"arable_land": 0.5},
        connectivity={"roads": 0.5},
    )


class TestTechnologyDiffusionModels:
    """Spatial Bass diffusion behaviour."""

    def test_ctor_defaults(self) -> None:
        model = TechnologyDiffusionModels()
        assert model.diffusion_parameters == {}

    def test_bass_diffusion_spreads_and_stays_within_population(self) -> None:
        regions = [
            _diffusion_region("north", population=1000.0),
            _diffusion_region("south", population=500.0),
        ]
        weights = np.array([[0.0, 0.2], [0.2, 0.0]])

        model = TechnologyDiffusionModels()
        result = model.bass_diffusion_spatial(
            regions,
            {"p": 0.03, "q": 0.38, "spatial_q": 0.1},
            weights,
        )

        assert result["regions"] == ["north", "south"]
        paths = result["adoption_paths"]
        assert paths.shape == (2, 41)  # 20 periods, 41 evaluation points
        # Initial adoption is 1% of each region's population.
        assert paths[0, 0] == pytest.approx(10.0)
        assert paths[1, 0] == pytest.approx(5.0)
        # Diffusion happens: adoption grows and stays below the market size.
        assert paths[:, -1].max() > paths[:, 0].max()
        assert np.all(paths[0] <= 1000.0)
        assert np.all(paths[1] <= 500.0)
        # Adoption is monotonically increasing in every region.
        assert np.all(np.diff(paths, axis=1) > 0)


class TestEcologicalEconomicsEngine:
    """Engine dispatch into carrying-capacity analysis."""

    def test_ctor_composes_submodels(self) -> None:
        engine = EcologicalEconomicsEngine()
        assert engine.config.discount_rate == 0.05
        assert engine.biophysical is not None
        assert engine.carrying_capacity is not None

    def test_carrying_capacity_analysis_hand_computed(self) -> None:
        engine = EcologicalEconomicsEngine()
        result = engine.run_analysis(
            "carrying_capacity",
            {
                "resources": [
                    {"name": "water", "available": 1000.0, "per_capita_requirement": 5.0},
                    {"name": "food", "available": 2000.0, "per_capita_requirement": 4.0},
                ],
                "current_population": 80.0,
                "safety_margin": 0.2,
            },
        )

        # water: 1000 * 0.8 / 5 = 160; food: 2000 * 0.8 / 4 = 400.
        assert result["per_resource_capacity"] == {"water": 160.0, "food": 400.0}
        assert result["carrying_capacity"] == 160.0
        assert result["binding_resource"] == "water"
        assert result["utilisation_ratio"] == pytest.approx(0.5)
        assert result["status"] == "within_capacity"

    def test_carrying_capacity_flags_overuse(self) -> None:
        engine = EcologicalEconomicsEngine()
        result = engine.run_analysis(
            "carrying_capacity",
            {
                "resources": [
                    {"name": "grazing", "available": 100.0,
                     "per_capita_requirement": 10.0}
                ],
                "current_population": 15.0,  # capacity is 8 with 20% margin
                "safety_margin": 0.2,
            },
        )
        assert result["carrying_capacity"] == 8.0
        assert result["utilisation_ratio"] == pytest.approx(15.0 / 8.0)
        assert result["status"] == "over_capacity"

    def test_unknown_analysis_type_raises(self) -> None:
        engine = EcologicalEconomicsEngine()
        with pytest.raises(ValueError, match="Unknown analysis type"):
            engine.run_analysis("astrology", {})


class TestBioregionalMarketDesign:
    """Credit issuance on registered bioregional assets."""

    @pytest.fixture
    def market(self) -> BioregionalMarketDesign:
        boundary = gpd.GeoDataFrame(
            {"name": ["test-bioregion"]},
            geometry=[box(0.0, 0.0, 1.0, 1.0)],
            crs="EPSG:4326",
        )
        market = BioregionalMarketDesign(boundary)
        market.register_asset(
            BioregionalAsset(
                asset_id="forest-01",
                asset_type="forest",
                location=(40.0, -120.0),
                area_hectares=250.0,
                ecological_attributes={
                    "biodiversity_index": 0.8,
                    "carbon_storage": 500.0,
                    "water_filtration": 0.5,
                    "recreation_value": 200.0,
                },
                economic_attributes={"market_value": 1000.0},
                ownership_type="community",
                management_regime="conservation",
                ecosystem_services={"provisioning": 0.5},
            )
        )
        return market

    def test_register_asset_and_participant(self, market) -> None:
        assert "forest-01" in market.assets
        assert market.register_participant(
            MarketParticipant(
                participant_id="co-op-1",
                participant_type="landowner",
                location=(40.0, -120.0),
                assets_owned=["forest-01"],
                market_preferences={"carbon": 0.8},
                budget_constraints={"max_spend": 5000.0},
                sustainability_goals={"additionality": 1.0},
            )
        )
        assert "co-op-1" in market.participants

    def test_credit_pricing_high_quality_hand_computed(self, market) -> None:
        quality = {
            "additionality": 1.0,
            "permanence": 1.0,
            "measurability": 1.0,
            "leakage_risk": 1.0,
            "co_benefits": 1.0,
        }
        credit = market.create_ecosystem_service_credit(
            "forest-01", "carbon", quantity=100.0, quality_parameters=quality
        )

        # Score = 1.0 → high tier; carbon base price 50, location multiplier 1.0.
        assert credit.quality_tier == "high"
        assert credit.price_per_unit == pytest.approx(50.0)
        assert credit.quantity == 100.0
        assert credit.verification_status == "pending"
        assert credit.temporal_profile == "permanent"
        assert credit.location == (40.0, -120.0)
        # Carbon credits carry biodiversity/water co-benefits from the asset.
        assert credit.co_benefits["biodiversity"] == pytest.approx(0.8 * 0.5)
        assert credit.co_benefits["water_quality"] == pytest.approx(0.5 * 0.3)
        # The credit is registered on the market.
        assert credit.credit_id in market.credits

    def test_credit_pricing_default_quality_is_low_tier(self, market) -> None:
        credit = market.create_ecosystem_service_credit(
            "forest-01", "carbon", quantity=10.0, quality_parameters={}
        )

        # All-default factors score 0.5 → not > 0.5 → low tier → base 15.
        assert credit.quality_tier == "low"
        assert credit.price_per_unit == pytest.approx(15.0)

    def test_biodiversity_credit_co_benefits_hand_computed(self, market) -> None:
        credit = market.create_ecosystem_service_credit(
            "forest-01",
            "biodiversity",
            quantity=5.0,
            quality_parameters={
                "additionality": 1.0,
                "permanence": 1.0,
                "measurability": 1.0,
                "leakage_risk": 1.0,
                "co_benefits": 1.0,
            },
        )

        # Biodiversity base price 100, urban multiplier 0.8*1 + 0.2 = 1.0.
        assert credit.price_per_unit == pytest.approx(100.0)
        assert credit.co_benefits["carbon"] == pytest.approx(500.0 * 0.4)
        assert credit.co_benefits["recreation"] == pytest.approx(200.0 * 0.6)
