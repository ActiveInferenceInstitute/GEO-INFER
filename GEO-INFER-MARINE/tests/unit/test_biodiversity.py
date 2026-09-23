"""Unit tests for the shared biodiversity index util (M6-04).

All expected values are hand-computed standard alpha-diversity metrics:
Shannon entropy, Gini-Simpson index and Pielou evenness.
"""

import math

import pytest

from geo_infer_marine.utils.biodiversity import biodiversity_metrics


class TestHandComputedDistributions:
    """Distributions with analytically known index values."""

    def test_equal_three_species(self) -> None:
        metrics = biodiversity_metrics({"cod": 10, "herring": 10, "pollock": 10})

        assert metrics["species_richness"] == 3
        assert metrics["total_abundance"] == 30
        # Shannon of a uniform 3-species distribution is ln(3).
        assert metrics["shannon"] == pytest.approx(math.log(3), rel=1e-9)
        # Simpson = 1 - sum(p_i^2) = 1 - 3*(1/9) = 2/3.
        assert metrics["simpson"] == pytest.approx(2.0 / 3.0, rel=1e-9)
        # Even community → Pielou evenness exactly 1.
        assert metrics["evenness"] == pytest.approx(1.0, rel=1e-9)

    def test_uneven_two_species_60_40(self) -> None:
        metrics = biodiversity_metrics({"cod": 60, "herring": 40})

        # H = -(0.6 ln 0.6 + 0.4 ln 0.4) = 0.67301...
        expected_shannon = -(0.6 * math.log(0.6) + 0.4 * math.log(0.4))
        assert metrics["shannon"] == pytest.approx(expected_shannon, rel=1e-9)
        # Simpson = 1 - (0.36 + 0.16) = 0.48.
        assert metrics["simpson"] == pytest.approx(0.48, rel=1e-9)
        # Pielou J = H / ln(2).
        assert metrics["evenness"] == pytest.approx(
            expected_shannon / math.log(2), rel=1e-9
        )
        assert metrics["species_richness"] == 2
        assert metrics["total_abundance"] == 100

    def test_dominated_community_has_low_indices(self) -> None:
        # 99% dominance: hand-computed Shannon 0.06629..., Simpson 0.01986...
        metrics = biodiversity_metrics(
            {"dominant": 990, "rare_1": 5, "rare_2": 3, "rare_3": 2}
        )

        expected_shannon = -(
            0.99 * math.log(0.99)
            + 0.005 * math.log(0.005)
            + 0.003 * math.log(0.003)
            + 0.002 * math.log(0.002)
        )
        assert metrics["shannon"] == pytest.approx(expected_shannon, rel=1e-6)
        assert metrics["simpson"] == pytest.approx(0.019862, rel=1e-4)
        assert metrics["evenness"] == pytest.approx(
            expected_shannon / math.log(4), rel=1e-4
        )
        assert metrics["evenness"] < 0.05  # heavily dominated community

    def test_monoculture_collapses_to_zero_diversity(self) -> None:
        """A single species has zero Shannon, Simpson and evenness."""
        metrics = biodiversity_metrics({"herring": 10})

        assert metrics["species_richness"] == 1
        assert metrics["total_abundance"] == 10
        # Shannon of a degenerate distribution is ~0 (log-smoothing only).
        assert abs(metrics["shannon"]) < 1e-8
        assert metrics["simpson"] == 0.0
        assert abs(metrics["evenness"]) < 1e-8


class TestDegenerateInputs:
    """Edge cases: empty and all-zero inputs."""

    def test_empty_input_yields_all_zeros(self) -> None:
        metrics = biodiversity_metrics({})

        assert metrics == {
            "species_richness": 0,
            "total_abundance": 0,
            "shannon": 0.0,
            "simpson": 0.0,
            "evenness": 0.0,
        }

    def test_all_zero_species_counts_pin_current_nan_semantics(self) -> None:
        """Every species absent (all counts 0) yields NaN indices.

        Pinned current behaviour: richness and total abundance are still
        reported, but the proportional metrics degenerate to NaN because
        proportions are 0/0. A RuntimeWarning is emitted under the strict
        warning policy.
        """
        with pytest.warns(RuntimeWarning):
            metrics = biodiversity_metrics({"cod": 0, "herring": 0})

        assert metrics["species_richness"] == 2
        assert metrics["total_abundance"] == 0
        assert math.isnan(metrics["shannon"])
        assert math.isnan(metrics["simpson"])
        assert math.isnan(metrics["evenness"])
