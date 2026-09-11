"""Regression tests for honest package-level exports (GS-131).

The package __init__ must import analysis classes directly so that an import
failure surfaces as an honest ImportError at package import time, instead of
being swallowed into a None sentinel that only explodes later as a TypeError
at call time.
"""

import geo_infer_spm


def test_analysis_classes_are_real_imports_not_none_sentinels():
    """Guarded try/except-None fallbacks are dead code next to unguarded
    sibling imports; the exports must be actual classes."""
    assert geo_infer_spm.SpatialAnalyzer is not None
    assert geo_infer_spm.TemporalAnalyzer is not None
    assert geo_infer_spm.BayesianSPM is not None
    assert isinstance(geo_infer_spm.SpatialAnalyzer, type)
    assert isinstance(geo_infer_spm.TemporalAnalyzer, type)
    assert isinstance(geo_infer_spm.BayesianSPM, type)


def test_package_api_surface_intact():
    """The flat-export API contract survives the guard removal."""
    for name in (
        "SPMAPI",
        "SPMData",
        "SPMResult",
        "ContrastResult",
        "load_data",
        "save_spm",
        "create_design_matrix",
        "generate_synthetic_data",
        "create_statistical_map",
        "MixedEffectsSPM",
        "NonparametricSPM",
        "ModelValidator",
        "SpatialRegression",
    ):
        assert hasattr(geo_infer_spm, name), name
