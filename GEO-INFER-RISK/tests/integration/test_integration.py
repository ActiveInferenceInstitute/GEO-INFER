"""
Integration tests for GEO-INFER-RISK.
"""

from __future__ import annotations

import geo_infer_risk
from geo_infer_risk.core import EnhancedRiskEngine


class TestRiskIntegration:
    """Test risk module integration."""

    def test_module_integration(self) -> None:
        """The package imports and its public surface is intact."""
        # Every advertised export resolves to a real object (guards against
        # the historical silent-None try/except imports).
        for name in geo_infer_risk.__all__:
            assert hasattr(geo_infer_risk, name), name
            assert getattr(geo_infer_risk, name) is not None, name

        engine = EnhancedRiskEngine()
        assert engine is not None
