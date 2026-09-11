"""Regression tests for GS-085: SPACE H3 predicate helpers must distinguish
invalid cells from unexpected failures (expected classes silent-False,
unexpected classes logged at debug, never silently swallowed)."""

import unittest
from unittest import mock

import geo_infer_space.backends.h3.operations as ops


def _patch_h3_available(fake):
    return mock.patch.multiple(ops, h3=fake, H3_AVAILABLE=True)


class TestOperationsPredicateHelpers(unittest.TestCase):
    def test_invalid_cell_returns_false(self):
        fake = mock.Mock()
        fake.is_valid_cell.return_value = False
        with _patch_h3_available(fake):
            self.assertFalse(ops.is_valid_cell("not-a-cell"))

    def test_unexpected_error_is_logged(self):
        fake = mock.Mock()
        fake.is_valid_cell.side_effect = RuntimeError("broken backend")
        with _patch_h3_available(fake):
            with self.assertLogs(
                "geo_infer_space.backends.h3.operations", level="DEBUG"
            ) as cap:
                self.assertFalse(ops.is_valid_cell("89283082e3fffff"))
        self.assertIn("Unexpected error", cap.output[0])

    def test_neighbor_unexpected_error_is_logged(self):
        fake = mock.Mock()
        fake.are_neighbor_cells.side_effect = RuntimeError("broken backend")
        with _patch_h3_available(fake):
            with self.assertLogs(
                "geo_infer_space.backends.h3.operations", level="DEBUG"
            ) as cap:
                self.assertFalse(
                    ops.are_neighbor_cells("89283082e3fffff", "89283082e7fffff")
                )
        self.assertIn("Unexpected error", cap.output[0])

    def test_neighbor_bad_type_returns_false(self):
        fake = mock.Mock()
        fake.are_neighbor_cells.side_effect = TypeError("expect str")
        with _patch_h3_available(fake):
            self.assertFalse(
                ops.are_neighbor_cells("89283082e3fffff", "89283082e7fffff")
            )


if __name__ == "__main__":
    unittest.main()
