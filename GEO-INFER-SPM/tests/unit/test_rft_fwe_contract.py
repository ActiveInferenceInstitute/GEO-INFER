"""Mathematical and known-null validity tests for RFT and FDR correction."""

import numpy as np
import pytest
from geo_infer_spm.core.rft import RandomFieldTheory
from scipy import ndimage
from scipy.special import gamma
from scipy.stats import binom, norm


@pytest.fixture
def rft() -> RandomFieldTheory:
    theory = RandomFieldTheory((20, 30), smoothness=np.array([2.0, 3.0]))
    theory.compute_resel_counts()
    return theory


def test_resel_counts_include_every_boundary_dimension(
    rft: RandomFieldTheory,
) -> None:
    """A 10-by-10-resel rectangle has R=(1, 20, 100)."""
    np.testing.assert_allclose(rft.resel_counts, np.array([1.0, 20.0, 100.0]))
    assert rft.search_volume == pytest.approx(100.0)

    theory_3d = RandomFieldTheory((10, 12, 14), smoothness=np.array([2.0, 3.0, 4.0]))
    counts = theory_3d.compute_resel_counts()
    edges = np.array([5.0, 4.0, 3.5])
    expected = np.array(
        [
            1.0,
            np.sum(edges),
            edges[0] * edges[1] + edges[0] * edges[2] + edges[1] * edges[2],
            np.prod(edges),
        ]
    )
    np.testing.assert_allclose(counts, expected)


def test_expected_ec_matches_closed_form_gaussian_densities(
    rft: RandomFieldTheory,
) -> None:
    """The full expected EC is the dot product of all resels and densities."""
    threshold = 3.0
    exponential = np.exp(-(threshold**2) / 2)
    expected_densities = np.array(
        [
            norm.sf(threshold),
            np.sqrt(4 * np.log(2)) * exponential / (2 * np.pi),
            4 * np.log(2) * threshold * exponential / (2 * np.pi) ** (3 / 2),
        ]
    )
    np.testing.assert_allclose(rft.ec_densities(threshold), expected_densities, rtol=1e-13)
    expected_ec = float(np.dot(np.array([1.0, 20.0, 100.0]), expected_densities))
    assert rft.expected_euler_characteristic(threshold) == pytest.approx(expected_ec, rel=1e-13)
    # Full EC must include the point and boundary terms, not only R_D rho_D.
    assert expected_ec > 100.0 * expected_densities[-1]


def test_three_dimensional_ec_uses_gaussian_hermite_polynomial() -> None:
    """The 3D top density contains H_2(u)=u^2-1, plus all boundaries."""
    theory = RandomFieldTheory((10, 12, 14), smoothness=np.array([2.0, 3.0, 4.0]))
    resels = theory.compute_resel_counts()
    threshold = 3.0
    exponential = np.exp(-(threshold**2) / 2)
    expected_densities = np.array(
        [
            norm.sf(threshold),
            np.sqrt(4 * np.log(2)) * exponential / (2 * np.pi),
            4 * np.log(2) * threshold * exponential / (2 * np.pi) ** (3 / 2),
            (4 * np.log(2)) ** (3 / 2) * (threshold**2 - 1) * exponential / (2 * np.pi) ** 2,
        ]
    )
    np.testing.assert_allclose(theory.ec_densities(threshold), expected_densities, rtol=1e-13)
    assert theory.expected_euler_characteristic(threshold) == pytest.approx(
        float(np.dot(resels, expected_densities)), rel=1e-13
    )


def test_cluster_extent_probabilities_match_poisson_clumping_formula(
    rft: RandomFieldTheory,
) -> None:
    """Single-cluster survival and search-volume FWE match their definitions."""
    forming_threshold = 2.5
    extents = np.array([0.0, 0.5, 1.5])
    expected_clusters = rft.expected_euler_characteristic(forming_threshold)
    expected_volume = rft.search_volume * norm.sf(forming_threshold)
    mean_extent = expected_volume / expected_clusters
    beta = (gamma(rft.ndim / 2 + 1) / mean_extent) ** (2 / rft.ndim)
    expected_survival = np.exp(-beta * extents ** (2 / rft.ndim))

    survival = rft.cluster_extent_probability(extents, forming_threshold)
    np.testing.assert_allclose(survival, expected_survival, rtol=1e-13)

    expected_fwe = -np.expm1(-2 * expected_clusters * expected_survival)
    corrected = rft.cluster_extent_p_value(extents, forming_threshold, two_sided=True)
    np.testing.assert_allclose(corrected, expected_fwe, rtol=1e-13)
    assert np.all(np.diff(corrected) < 0)


def test_cluster_extent_threshold_inverts_fwe_probability(
    rft: RandomFieldTheory,
) -> None:
    forming_threshold = 2.5
    extent = rft.cluster_extent_threshold(0.05, forming_threshold, two_sided=True)
    assert rft.cluster_extent_p_value(extent, forming_threshold, two_sided=True) == pytest.approx(
        0.05, abs=1e-12
    )
    assert rft.cluster_extent_p_value(extent * 1.1, forming_threshold, two_sided=True) < 0.05


def test_cluster_correction_assigns_component_extent_pvalues() -> None:
    theory = RandomFieldTheory((20, 20), smoothness=np.array([3.0, 3.0]))
    theory.compute_search_volume()
    field = np.zeros((20, 20))
    field[1:4, 1:4] = 3.0
    field[10:15, 10:15] = 3.0

    corrected = theory.correct_p_values(
        field,
        stat_type="Z",
        method="cluster",
        cluster_forming_threshold=2.5,
        two_sided=False,
    )
    small_p = theory.cluster_extent_p_value(9, 2.5, extent_in_resels=False)
    large_p = theory.cluster_extent_p_value(25, 2.5, extent_in_resels=False)
    np.testing.assert_allclose(corrected[1:4, 1:4], small_p)
    np.testing.assert_allclose(corrected[10:15, 10:15], large_p)
    assert large_p < small_p
    assert np.all(corrected[field == 0] == 1.0)


def test_peak_threshold_inverts_full_ec_fwe(rft: RandomFieldTheory) -> None:
    threshold = rft.peak_threshold(0.05, "Z", two_sided=True)
    assert rft.peak_fwe_p_value(threshold, "Z", two_sided=True) == pytest.approx(0.05, abs=1e-12)
    assert rft.peak_threshold(0.01, "Z", two_sided=True) > threshold


def test_peak_corrected_pvalues_are_bounded_monotone_and_thresholded(
    rft: RandomFieldTheory,
) -> None:
    """Peak p-values retain information and agree with the FWE threshold."""
    rng = np.random.default_rng(0)
    stat_map = rng.normal(size=(20, 30)) * 3.0
    corrected = rft.correct_p_values(stat_map, stat_type="Z", method="peak")
    assert np.all(corrected >= 0.0)
    assert np.all(corrected <= 1.0)
    order = np.argsort(np.abs(stat_map), axis=None)
    assert np.all(np.diff(corrected.ravel()[order]) <= 1e-12)
    threshold = rft.peak_threshold(0.05, "Z", two_sided=True)
    assert np.all(corrected[np.abs(stat_map) < threshold] >= 0.05 - 1e-12)
    assert np.all(corrected[np.abs(stat_map) > threshold] <= 0.05 + 1e-12)


def test_peak_and_cluster_fwe_are_calibrated_under_smooth_gaussian_null() -> None:
    """Both full-EC peak and cluster extent inference control known-null FWE."""
    shape = (64, 64)
    padding = 12
    sigma = 2.0
    fwhm = np.full(2, np.sqrt(8 * np.log(2)) * sigma)
    theory = RandomFieldTheory(shape, smoothness=fwhm)
    theory.compute_search_volume()

    padded_shape = tuple(size + 2 * padding for size in shape)
    impulse = np.zeros(padded_shape)
    impulse[tuple(size // 2 for size in padded_shape)] = 1.0
    kernel = ndimage.gaussian_filter(impulse, sigma=sigma, mode="constant")
    null_standard_deviation = np.sqrt(np.sum(kernel**2))

    rng = np.random.default_rng(20260819)
    simulations = 500
    forming_threshold = 3.09
    peak_threshold = theory.peak_threshold(0.05, "Z", two_sided=True)
    peak_rejections = 0
    cluster_rejections = 0
    positive_cluster_count = 0

    for _ in range(simulations):
        padded = ndimage.gaussian_filter(
            rng.normal(size=padded_shape), sigma=sigma, mode="constant"
        )
        field = (
            padded[
                padding : padding + shape[0],
                padding : padding + shape[1],
            ]
            / null_standard_deviation
        )
        peak_rejections += int(np.max(np.abs(field)) >= peak_threshold)
        cluster_p = theory.correct_p_values(
            field,
            stat_type="Z",
            method="cluster",
            cluster_forming_threshold=forming_threshold,
            two_sided=True,
        )
        cluster_rejections += int(np.any(cluster_p < 0.05))
        positive_cluster_count += ndimage.label(field >= forming_threshold)[1]

    # A two-sided 99% binomial acceptance interval around nominal FWE catches
    # both anti-conservative and vacuously over-conservative implementations.
    lower = int(binom.ppf(0.005, simulations, 0.05))
    upper = int(binom.ppf(0.995, simulations, 0.05))
    assert lower <= peak_rejections <= upper
    assert lower <= cluster_rejections <= upper

    empirical_expected_clusters = positive_cluster_count / simulations
    analytic_expected_ec = theory.expected_euler_characteristic(forming_threshold)
    assert empirical_expected_clusters == pytest.approx(analytic_expected_ec, rel=0.25)


def test_fdr_returns_true_bh_adjusted_qvalues():
    """The FDR branch returns BH-adjusted q-values (monotone, >= p, <=1).

    Verified against statsmodels when available, else by the defining
    monotonicity check. This catches the old threshold-only implementation.
    """
    rng = np.random.default_rng(5)
    p_flat = rng.uniform(0.001, 0.5, size=40)

    # Reuse the BH routine through compute_spm's FDR branch.
    from geo_infer_spm.core.rft import compute_spm

    class _Contrast:
        def __init__(self, p):
            self.p_values = np.asarray(p)
            self.t_statistic = np.zeros_like(p)

    c = _Contrast(p_flat)
    compute_spm(None, c, correction="FDR", alpha=0.05)

    q = c.corrected_p_values
    assert np.all(q >= 0.0) and np.all(q <= 1.0)
    # BH q-values dominate the corresponding p-values (q >= p).
    assert np.all(q >= p_flat - 1e-12)
    # Monotonicity: sorted q has the same order as sorted p.
    assert np.all(np.diff(q[np.argsort(p_flat)]) >= -1e-12)

    try:
        from statsmodels.stats.multitest import multipletests

        sm_q = multipletests(p_flat, method="fdr_bh")[1]
        assert np.allclose(q, sm_q, atol=1e-12)
    except ImportError:
        pass  # statsmodels optional; monotonicity checks above still hold
