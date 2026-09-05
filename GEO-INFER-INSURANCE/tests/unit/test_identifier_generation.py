"""Unique identifier generation for policies and claims.

Extracted from GEO-INFER-RISK when the underwriting subsystem moved here: the
old 4-digit suffix collided within a single timestamp second.
"""

from geo_infer_insurance.underwriting.core.claims_processing import ClaimsProcessor
from geo_infer_insurance.underwriting.core.policy_management import PolicyManager

import numpy as np

def global_stream_untouched(action: object) -> bool:
    """Return whether ``action`` left the numpy.random singleton alone."""
    np.random.seed(4242)
    expected = np.random.random()
    np.random.seed(4242)
    action()  # type: ignore[operator]
    return bool(np.random.random() == expected)


def test_policy_numbers_are_unique_in_bulk() -> None:
    manager = PolicyManager()
    numbers = {manager._generate_policy_number() for _ in range(5000)}
    assert len(numbers) == 5000
    assert all(number.startswith("POL") for number in numbers)


def test_claim_numbers_are_unique_in_bulk() -> None:
    processor = ClaimsProcessor()
    numbers = {processor._generate_claim_number() for _ in range(5000)}
    assert len(numbers) == 5000
    assert all(number.startswith("CLM") for number in numbers)


def test_identifier_generation_leaves_global_stream_untouched() -> None:
    manager = PolicyManager()
    assert global_stream_untouched(manager._generate_policy_number)
