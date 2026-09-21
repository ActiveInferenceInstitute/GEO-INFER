#!/usr/bin/env python
"""
Unit tests for the geo_infer_art command-line interface.
"""

import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

import numpy as np
from PIL import Image, ImageSequence

from geo_infer_art.cli import main


def _write_points_geojson(path: str) -> None:
    """Write a minimal two-point GeoJSON FeatureCollection."""
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
                "properties": {},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1.0, 1.0]},
                "properties": {},
            },
        ],
    }
    with open(path, "w") as f:
        json.dump(geojson, f)


def _load_gif_frames(path: str):
    """Load GIF frames as RGB numpy arrays."""
    with Image.open(path) as gif:
        return [np.array(frame.convert("RGB")) for frame in ImageSequence.Iterator(gif)]


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
                [
                    "geo-infer-art",
                    "geo-art",
                    "--input",
                    "data.unsupported",
                    "--output",
                    "out.png",
                ],
            ):
                code = main()
        self.assertEqual(code, 1)
        self.assertIn("Unsupported input file format", out.getvalue())


class TestAnimate(unittest.TestCase):
    """Test suite for the `animate` CLI command."""

    def _run_animate(self, out_path: str, parameter: str, values: list):
        """Run an `animate --animation-type parameter_sweep` invocation."""
        with tempfile.TemporaryDirectory() as tmp:
            geojson = os.path.join(tmp, "points.geojson")
            _write_points_geojson(geojson)
            args = [
                "geo-infer-art",
                "animate",
                "--input",
                geojson,
                "--output",
                out_path,
                "--animation-type",
                "parameter_sweep",
                "--parameter",
                parameter,
                "--values",
                *values,
                "--duration",
                "1",
                "--fps",
                "2",
            ]
            with redirect_stdout(StringIO()) as out:
                with mock.patch("sys.argv", args):
                    code = main()
            return code, out.getvalue()

    def test_parameter_sweep_abstraction_vary_frames(self):
        """abstraction_level sweep produces distinct frames in the GIF."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.gif")
            code, _ = self._run_animate(out, "abstraction_level", ["0.1", "0.9"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(out))
            frames = _load_gif_frames(out)
            self.assertGreaterEqual(len(frames), 2)
            self.assertFalse(np.array_equal(frames[0], frames[1]))

    def test_parameter_sweep_style_vary_frames(self):
        """style sweep produces distinct frames in the GIF."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.gif")
            code, _ = self._run_animate(out, "style", ["contour", "particles"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(out))
            frames = _load_gif_frames(out)
            self.assertGreaterEqual(len(frames), 2)
            self.assertFalse(np.array_equal(frames[0], frames[1]))

    def test_parameter_sweep_rejects_unsupported_parameter(self):
        """Unsupported sweep parameter fails with exit 1 and no output."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.gif")
            code, stdout = self._run_animate(out, "resolution", ["100", "200"])
            self.assertEqual(code, 1)
            self.assertIn("Error", stdout)
            self.assertFalse(os.path.exists(out))

    def test_parameter_sweep_rejects_non_numeric_values(self):
        """Non-numeric values for abstraction_level fail with exit 1."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out.gif")
            code, stdout = self._run_animate(out, "abstraction_level", ["abc"])
            self.assertEqual(code, 1)
            self.assertIn("Error", stdout)


if __name__ == "__main__":
    unittest.main()
