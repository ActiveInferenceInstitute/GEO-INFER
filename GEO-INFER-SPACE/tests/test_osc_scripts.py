import unittest
import subprocess
from pathlib import Path
import tempfile
import shutil

class TestOSCScripts(unittest.TestCase):
    def setUp(self):
        self.script_dir = Path(__file__).parent.parent / 'bin'
        self.temp_repo_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.temp_repo_dir.exists():
            shutil.rmtree(self.temp_repo_dir)

    def test_osc_setup_all(self):
        """Test osc_setup_all.py clones repos without running tests."""
        script = self.script_dir / 'osc_setup_all.py'
        result = subprocess.run([str(script), '--output-dir', str(self.temp_repo_dir), '--skip-tests'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(any('osc-geo' in str(child) for child in self.temp_repo_dir.iterdir()))

    def test_osc_status(self):
        """Test osc_status.py runs and outputs status information."""
        script = self.script_dir / 'osc_status.py'
        result = subprocess.run([str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Repository Status', result.stdout) 