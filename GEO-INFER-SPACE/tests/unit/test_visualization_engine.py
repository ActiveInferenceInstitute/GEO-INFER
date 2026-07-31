import unittest
import json
from pathlib import Path
import tempfile
import pytest
from geo_infer_space.core.visualization_engine import InteractiveVisualizationEngine

@pytest.mark.reporting
class TestInteractiveVisualizationEngine(unittest.TestCase):
    def setUp(self):
        self.config = {'location': {'bounds': {'north': 42, 'south': 41, 'east': -123, 'west': -125}}}
        self._tmpdir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self._tmpdir.name)
        self.engine = InteractiveVisualizationEngine(self.config, self.output_dir)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_initialization(self):
        """Test engine initialization with config."""
        self.assertEqual(self.engine.center_lat, 41.5)
        self.assertEqual(self.engine.center_lon, -124.0)

    def test_create_comprehensive_dashboard(self):
        """Test dashboard creation with small real data."""
        analysis_results = {'domain_results': {'forest_health': {}}}
        dashboard_path = self.engine.create_comprehensive_dashboard(analysis_results)
        self.assertTrue(Path(dashboard_path).exists())
        self.assertTrue(Path(dashboard_path).is_relative_to(self.output_dir))
        self.assertNotIn("FOREST-", Path(dashboard_path).read_text(encoding="utf-8"))
        manifest_path = Path(dashboard_path).with_suffix(".manifest.json")
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["h3_version"], "4.5.0")
        self.assertTrue(manifest["accessibility"]["nonempty_html"])

    def test_deterministic_output_name_and_manifest(self):
        """Explicit run metadata produces a stable, auditable artifact pair."""
        path = Path(
            self.engine.create_comprehensive_dashboard(
                {"domain_results": {}},
                {
                    "output_name": "deterministic.html",
                    "generated_at": "2026-07-30T00:00:00Z",
                },
            )
        )
        manifest = json.loads(path.with_suffix(".manifest.json").read_text())
        self.assertEqual(path.name, "deterministic.html")
        self.assertEqual(manifest["generated_at"], "2026-07-30T00:00:00Z")
        self.assertEqual(manifest["artifacts"][0]["path"], "deterministic.html")
