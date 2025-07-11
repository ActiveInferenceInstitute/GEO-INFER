import unittest
import subprocess
from pathlib import Path

class TestOSCScripts(unittest.TestCase):
    def setUp(self):
        self.script_dir = Path(__file__).parent.parent.parent / 'bin'
        self.temp_repo_dir = Path('temp_repos')
        self.temp_repo_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.temp_repo_dir.exists():
            for child in self.temp_repo_dir.iterdir():
                if child.is_dir():
                    subprocess.run(['rm', '-rf', str(child)])
            self.temp_repo_dir.rmdir()

    def test_osc_setup_all(self):
        """Test osc_setup_all.py clones repos and sets up."""
        script = self.script_dir / 'osc_setup_all.py'
        result = subprocess.run([str(script), '--output-dir', str(self.temp_repo_dir)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.temp_repo_dir / 'osc-geo-h3grid-srv').exists())

    def test_osc_status(self):
        """Test osc_status.py runs and outputs status."""
        script = self.script_dir / 'osc_status.py'
        result = subprocess.run([str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('repositories', result.stdout) 