#!/usr/bin/env python
"""
Unit tests for the geo_infer_art command-line interface.
"""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from geo_infer_art.cli import main


class TestCli(unittest.TestCase):
    """Test suite for the geo-infer-art CLI entry point."""

    def test_help_exits_zero(self):
        """`--help` prints usage and exits 0."""
        with redirect_stdout(StringIO()) as out:
            with self.assertRaises(SystemExit) as ctx:
                with mock.patch("sys.argv", ["geo-infer-art", "--help"]):
                    main()
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("usage", out.getvalue().lower())

    def test_unsupported_input_format_returns_error(self):
        """`geo-art` with an unsupported extension fails cleanly with exit 1."""
        with redirect_stdout(StringIO()) as out:
            with mock.patch(
                "sys.argv",
                ["geo-infer-art", "geo-art", "--input", "data.unsupported",
                 "--output", "out.png"],
            ):
                code = main()
        self.assertEqual(code, 1)
        self.assertIn("Unsupported input file format", out.getvalue())


if __name__ == "__main__":
    unittest.main()
