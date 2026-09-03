"""Import smoke tests for GEO-INFER-ECON.

Guards the package contract: ``geo_infer_econ`` and every required submodule
``__init__`` must import cleanly, and every name advertised in ``__all__``
must resolve via ``getattr`` — no phantom exports like the historical
``ConsumerTheoryModels`` entry, which was listed in
``microeconomics.__all__`` but defined nowhere.
"""

from __future__ import annotations

import importlib

import pytest


# Submodules whose __init__ must import in a default environment. The
# ``api`` submodule is intentionally excluded: it hard-depends on fastapi,
# which is an optional extra (the top-level package wraps it in try/except).
REQUIRED_SUBMODULES = [
    "geo_infer_econ",
    "geo_infer_econ.core",
    "geo_infer_econ.microeconomics",
    "geo_infer_econ.macroeconomics",
    "geo_infer_econ.bioregional",
    "geo_infer_econ.utils",
]


@pytest.mark.parametrize("module_name", REQUIRED_SUBMODULES)
def test_submodule_imports_cleanly(module_name: str) -> None:
    """Each required submodule __init__ imports without error."""
    module = importlib.import_module(module_name)
    assert module is not None


def test_top_level_all_names_resolve() -> None:
    """Every geo_infer_econ.__all__ entry is resolvable via getattr."""
    import geo_infer_econ

    for name in geo_infer_econ.__all__:
        assert hasattr(geo_infer_econ, name), (
            f"__all__ advertises {name!r} but the attribute does not exist"
        )


def test_microeconomics_all_names_resolve() -> None:
    """Every microeconomics.__all__ entry is resolvable and real."""
    from geo_infer_econ import microeconomics

    for name in microeconomics.__all__:
        assert hasattr(microeconomics, name), (
            f"__all__ advertises {name!r} but the attribute does not exist"
        )


def test_phantom_consumer_theory_models_absent() -> None:
    """ConsumerTheoryModels stays gone: it never had a definition."""
    from geo_infer_econ import microeconomics

    assert "ConsumerTheoryModels" not in microeconomics.__all__
    assert not hasattr(microeconomics, "ConsumerTheoryModels")


def test_duplicate_shadow_classes_removed_from_producer_theory() -> None:
    """producer_theory must not shadow the canonical market/game/behavioral classes."""
    import geo_infer_econ.microeconomics.producer_theory as producer_theory

    assert not hasattr(producer_theory, "MarketStructureAnalysis")
    assert not hasattr(producer_theory, "GameTheoryModels")
    assert not hasattr(producer_theory, "BehavioralEconomicsEngine")

    # The canonical definitions are importable from their own modules and are
    # the exact objects re-exported through the package.
    from geo_infer_econ.microeconomics.market_structure import MarketStructureAnalysis
    from geo_infer_econ.microeconomics.game_theory import GameTheoryModels
    from geo_infer_econ.microeconomics.behavioral_economics import BehavioralEconomicsEngine
    from geo_infer_econ import microeconomics

    assert microeconomics.MarketStructureAnalysis is MarketStructureAnalysis
    assert microeconomics.GameTheoryModels is GameTheoryModels
    assert microeconomics.BehavioralEconomicsEngine is BehavioralEconomicsEngine
