"""Package export contract for ``geo_infer_risk``.

Every name advertised in ``__all__`` must resolve to a real, non-None object.
The historical failure mode this guards against is the silent-None export: an
optional try/except import that swallows an ImportError, leaves the name bound
to ``None``, and still lists it in ``__all__`` — so ``geo_infer_risk.RiskAPI``
"exists" while being unusable.
"""

from __future__ import annotations

import geo_infer_risk

# Names once advertised through silent-None try/except imports. The backing
# packages (geo_infer_risk.models, geo_infer_risk.api) never existed and no
# module, test, or example referenced them, so they were removed rather than
# stubbed. The package must not re-introduce them as None-valued exports.
REMOVED_SILENT_NONE_EXPORTS = [
    "FloodModel",
    "EarthquakeModel",
    "HurricaneModel",
    "WildfireModel",
    "DroughtModel",
    "MultiHazardModel",
    "RiskAPI",
    "ModelRegistry",
    "ResultsFormatter",
]


def test_every_all_name_resolves_to_a_real_object() -> None:
    """Each ``__all__`` entry resolves via getattr and is not None."""
    for name in geo_infer_risk.__all__:
        assert hasattr(geo_infer_risk, name), (
            f"__all__ advertises {name!r} but the attribute does not exist"
        )
        assert getattr(geo_infer_risk, name) is not None, (
            f"__all__ advertises {name!r} but it is bound to None"
        )


def test_silent_none_exports_were_removed() -> None:
    """Removed None-valued exports stay removed (no silent reintroduction)."""
    for name in REMOVED_SILENT_NONE_EXPORTS:
        assert name not in geo_infer_risk.__all__, (
            f"{name!r} returned to __all__ without a real implementation"
        )
        assert not hasattr(geo_infer_risk, name), (
            f"{name!r} is bound on the package but not implemented"
        )
