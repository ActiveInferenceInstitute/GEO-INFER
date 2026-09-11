"""Regression tests for GS-085: ACT H3 adapter validation must distinguish
invalid cells from unexpected backend failures (logged, not silent)."""

import unittest
from unittest import mock

from geo_infer_act.utils.h3_adapter import H3Adapter


def _adapter_with(fake_h3):
    adapter = H3Adapter.__new__(H3Adapter)
    adapter.space_indexer = None
    adapter.h3 = fake_h3
    adapter.source = "direct"
    return adapter


class TestH3AdapterValidation(unittest.TestCase):
    def test_invalid_cell_string_returns_false(self):
        fake = mock.Mock()
        fake.is_valid_cell.return_value = False
        adapter = _adapter_with(fake)
        self.assertFalse(adapter.is_valid_cell("not-a-cell"))
        fake.is_valid_cell.assert_called_once_with("not-a-cell")

    def test_valid_cell_returns_true(self):
        fake = mock.Mock()
        fake.is_valid_cell.return_value = True
        adapter = _adapter_with(fake)
        self.assertTrue(adapter.is_valid_cell("89283082e3fffff"))

    def test_unexpected_error_is_logged_not_silent(self):
        fake = mock.Mock()
        fake.is_valid_cell.side_effect = RuntimeError("broken backend")
        adapter = _adapter_with(fake)
        with self.assertLogs("geo_infer_act.utils.h3_adapter", level="DEBUG") as cap:
            self.assertFalse(adapter.is_valid_cell("89283082e3fffff"))
        self.assertIn("Unexpected error", cap.output[0])

    def test_bad_index_type_returns_false_without_logging(self):
        fake = mock.Mock()
        fake.is_valid_cell.side_effect = TypeError("expect str")
        adapter = _adapter_with(fake)
        self.assertFalse(adapter.is_valid_cell(12345))


if __name__ == "__main__":
    unittest.main()
