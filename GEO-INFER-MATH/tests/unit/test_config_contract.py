"""Contract tests for GEO-INFER-MATH config and core package surface.

GS19-72: ``configure()`` accepts ``"<section>.<option>"`` dotted keys and
dict-of-sections values, and raises ``ValueError`` for unknown sections
and non-dotted plain keys instead of silently misrouting values.

GS19-73: the dead ``core/integration.py`` module was deleted and removed
from the core ``__all__`` — the import must fail loudly.
"""

import pytest

import geo_infer_math.core
from geo_infer_math.config import configure, get_config


@pytest.fixture(autouse=True)
def restore_global_config():
    """configure() mutates the global singleton — restore it afterwards."""
    snapshot = {
        section: dict(values) for section, values in get_config().to_dict().items()
    }
    yield
    config = get_config()
    for section, values in snapshot.items():
        config.update(section, values)


class TestConfigureRoundTrips:
    """The two accepted configure() forms survive a get round-trip."""

    def test_dotted_key_round_trip(self) -> None:
        result = configure(**{"numerical.precision": "float32"})

        assert result is get_config()
        assert get_config().get("numerical", "precision") == "float32"

    def test_dict_of_sections_round_trip_merges(self) -> None:
        configure(**{"performance": {"num_workers": 8}})

        assert get_config().get("performance", "num_workers") == 8
        # The merge preserves untouched options in the same section.
        assert get_config().get("performance", "cache_size") == 256


class TestConfigureRejections:
    """Misconfigured keys raise ValueError instead of landing somewhere."""

    def test_unknown_section_dotted_form_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown configuration section"):
            configure(**{"nonexistent_section.precision": 1})

    def test_unknown_section_dict_form_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown configuration section"):
            configure(**{"nonexistent_section": {"option": 1}})

    def test_plain_non_dotted_key_raises(self) -> None:
        """A non-dotted key with a non-dict value has no valid target."""
        with pytest.raises(ValueError, match="Invalid configuration key"):
            configure(**{"numerical": "not-a-section-dict"})


class TestDeletedIntegrationModule:
    """GS19-73: core/integration.py was deleted with zero consumers."""

    def test_importing_deleted_module_raises_import_error(self) -> None:
        with pytest.raises(ImportError):
            from geo_infer_math.core import integration  # noqa: F401

    def test_integration_absent_from_core_all(self) -> None:
        assert "integration" not in geo_infer_math.core.__all__
        # Sanity: the __all__ itself is intact, not emptied wholesale.
        assert "symbolic_math" in geo_infer_math.core.__all__
