"""Integration coverage for deterministic generation and style metadata."""

import numpy as np

from geo_infer_art.core.aesthetics.style_transfer import StyleTransfer
from geo_infer_art.core.generation.procedural_art import ProceduralArt


def test_procedural_generation_is_finite_and_style_metadata_is_available() -> None:
    """Generate a small seeded artifact and validate its style metadata contract."""
    art = ProceduralArt(
        algorithm="noise_field", params={"seed": 42}, resolution=(24, 24)
    )
    generated = art.generate()
    # Metadata lookup is intentionally usable without TensorFlow model loading.
    info = StyleTransfer.get_style_info(object.__new__(StyleTransfer), "watercolor")

    assert generated is art
    assert art.image is not None
    assert np.isfinite(np.asarray(art.image, dtype=float)).all()
    assert info["name"] == "watercolor"
    assert info["category"] == "landscape"
