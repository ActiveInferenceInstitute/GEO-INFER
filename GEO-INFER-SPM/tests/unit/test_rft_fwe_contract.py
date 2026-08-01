"""Statistical-validity property tests for RFT and FDR corrections.

Addresses the 'tests assert shapes, not statistical validity' finding
(STATS-05): verify RFT corrected p-values control family-wise error under
smooth null fields (known-null FWER control), and that the FDR branch
returns genuine Benjamini-Hochberg adjusted q-values (not a threshold-only
step).

These are stochastic tests with bounded FPR assertions, run with a frozen
seed for reproducibility. The RFT first-order EC-density approximation is
expected to be close to (mildly above) the nominal level; the loose bound
documents its anti-conservatism honestly.
"""

import numpy as np
import pytest
from scipy.ndimage import gaussian_filter

from geo_infer_spm.core.rft import RandomFieldTheory


@pytest.fixture
def rft():
    shape = (40, 50)
    rng = np.random.default_rng(7)
    theory = RandomFieldTheory(shape, df=20)
    theory.estimate_smoothness(rng.normal(size=shape))
    theory.compute_search_volume()
    return theory


def test_rft_fwe_controls_familywise_error_under_null(rft):
    """Under smooth null fields, RFT-FWE p<0.05 fires on <12% of fields.

    Target is 5%; the first-order RFT EC-density with an estimated smoothness
    is mildly anti-conservative (~7% observed), so the bound is set at 12%
    to remain robust while still catching gross errors (e.g. the old
    dimensionally-invalid cluster formula, which produced much worse FPR).
    """
    rng = np.random.default_rng(123)
    nfields = 200

    def smooth_field():
        x = rng.normal(size=(40, 50))
        return gaussian_filter(x, sigma=2.0)

    rejections = 0
    for _ in range(nfields):
        fld = smooth_field()
        sd = fld.std()
        z = fld / sd if sd > 0 else fld
        p_fwe = min(1.0, rft.expected_clusters(float(np.max(z)), "Z"))
        if p_fwe < 0.05:
            rejections += 1

    fpr = rejections / nfields
    assert fpr < 0.12, f"RFT FWE FPR {fpr:.3f} exceeds conservative bound"


def test_rft_corrected_pvalues_bounded_and_below_threshold_are_one(rft):
    """Corrected p-values are in [0,1]; sub-threshold voxels are exactly 1.0."""
    rng = np.random.default_rng(0)
    stat_map = rng.normal(size=(40, 50)) * 3.0
    corrected = rft.correct_p_values(stat_map, stat_type="Z", method="peak")
    assert np.all(corrected >= 0.0)
    assert np.all(corrected <= 1.0)
    threshold = rft.peak_threshold(alpha=0.05, stat_type="Z")
    assert np.all(corrected[np.abs(stat_map) <= threshold] == 1.0)


def test_fdr_returns_true_bh_adjusted_qvalues():
    """The FDR branch returns BH-adjusted q-values (monotone, >= p, <=1).

    Verified against statsmodels when available, else by the defining
    monotonicity check. This catches the old threshold-only implementation.
    """
    import geo_infer_spm.core.rft as rft_mod

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