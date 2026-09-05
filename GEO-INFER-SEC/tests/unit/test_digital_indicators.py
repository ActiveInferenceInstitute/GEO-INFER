"""DigitalSecurityManager loads threat indicators from a configurable YAML file."""

import tempfile
import unittest
from pathlib import Path

from geo_infer_sec.core.digital_security import DigitalSecurityManager


class TestThreatIndicatorLoading(unittest.TestCase):
    def test_loads_indicators_from_configured_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            indicator_file = Path(tmp) / "indicators.yaml"
            indicator_file.write_text(
                "blocked_ips:\n  - 203.0.113.50\n"
                "threat_indicators:\n  - bad-actor.example\n"
                "trusted_ips:\n  - 198.51.100.9\n"
            )
            manager = DigitalSecurityManager(
                config_path=str(
                    Path(tmp) / "config.yaml"
                )
            )
            # Point the manager at the indicator file via its config contract.
            manager.config["threat_indicators_file"] = str(indicator_file)
            manager._load_threat_intelligence()

            self.assertIn("203.0.113.50", manager.blocked_ips)
            self.assertIn("bad-actor.example", manager.threat_indicators)
            self.assertIn("198.51.100.9", manager.trusted_ips)
            self.assertNotIn("192.168.1.100", manager.blocked_ips)

    def test_missing_file_starts_empty(self):
        manager = DigitalSecurityManager()
        manager.config["threat_indicators_file"] = "/nonexistent/indicators.yaml"
        manager.blocked_ips.clear()
        manager.threat_indicators.clear()
        manager._load_threat_intelligence()
        self.assertEqual(manager.blocked_ips, set())
        self.assertEqual(manager.threat_indicators, set())
