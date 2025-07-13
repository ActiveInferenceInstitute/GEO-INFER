import unittest
import subprocess
from pathlib import Path
import tempfile
import shutil
import os

class TestOSCScripts(unittest.TestCase):
    def setUp(self):
        self.script_dir = Path(__file__).parent.parent / 'bin'
        self.temp_repo_dir = Path(tempfile.mkdtemp())
        # Set environment variable to point to our temp directory
        os.environ['OSC_REPOS_DIR'] = str(self.temp_repo_dir)

    def tearDown(self):
        if self.temp_repo_dir.exists():
            shutil.rmtree(self.temp_repo_dir)
        # Clean up environment variable
        if 'OSC_REPOS_DIR' in os.environ:
            del os.environ['OSC_REPOS_DIR']

    def test_osc_setup_all(self):
        """Test osc_setup_all.py clones repos without running tests."""
        script = self.script_dir / 'osc_setup_all.py'
        if script.exists():
            result = subprocess.run([str(script), '--output-dir', str(self.temp_repo_dir), '--skip-tests'], capture_output=True, text=True)
            # Check if any osc-geo directories were created
            osc_dirs = [child for child in self.temp_repo_dir.iterdir() if 'osc-geo' in str(child)]
            self.assertTrue(len(osc_dirs) > 0, f"No osc-geo directories found in {self.temp_repo_dir}")
        else:
            self.skipTest(f"Script not found: {script}")

    def test_osc_status(self):
        """Test osc_status.py runs and outputs status information."""
        script = self.script_dir / 'osc_status.py'
        if script.exists():
            result = subprocess.run([str(script)], capture_output=True, text=True)
            # The script should run without error, even if no repos are found
            self.assertIn('Repository Status', result.stdout or result.stderr)
        else:
            self.skipTest(f"Script not found: {script}") 