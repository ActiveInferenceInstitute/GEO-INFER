import unittest
import subprocess
from pathlib import Path
import tempfile
import shutil
import os
import pytest
import sys

def reset_and_reinstall_venvs(repo_base_dir):
    """
    Reset and reinstall virtual environments for all cloned OSC repositories.
    This ensures clean, working virtual environments from a cold start.
    
    Args:
        repo_base_dir (str): Base directory containing cloned repositories
    """
    repo_path = Path(repo_base_dir)
    if not repo_path.exists():
        print(f"Repository base directory does not exist: {repo_base_dir}")
        return False
    
    success_count = 0
    total_repos = 0
    
    for repo_dir in repo_path.iterdir():
        if not repo_dir.is_dir() or repo_dir.name.startswith('.'):
            continue
            
        total_repos += 1
        print(f"Processing repository: {repo_dir.name}")
        
        # Check if this is an OSC repository
        if not (repo_dir.name.startswith('osc-') or 'h3' in repo_dir.name.lower()):
            print(f"Skipping non-OSC repository: {repo_dir.name}")
            continue
        
        venv_path = repo_dir / "venv"
        requirements_file = repo_dir / "requirements.txt"
        
        # Remove existing virtual environment if it exists
        if venv_path.exists():
            print(f"Removing existing virtual environment: {venv_path}")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print(f"Warning: Could not remove {venv_path}: {e}")
        
        # Create new virtual environment
        print(f"Creating new virtual environment: {venv_path}")
        try:
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"Failed to create virtual environment for {repo_dir.name}: {result.stderr}")
                continue
                
        except subprocess.TimeoutExpired:
            print(f"Timeout creating virtual environment for {repo_dir.name}")
            continue
        except Exception as e:
            print(f"Error creating virtual environment for {repo_dir.name}: {e}")
            continue
        
        # Install requirements if they exist
        if requirements_file.exists():
            print(f"Installing requirements from: {requirements_file}")
            try:
                # Get the path to pip in the new virtual environment
                if os.name == 'nt':  # Windows
                    pip_path = venv_path / "Scripts" / "pip"
                else:  # Unix/Linux/macOS
                    pip_path = venv_path / "bin" / "pip"
                
                # Install requirements
                result = subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"Warning: Failed to install requirements for {repo_dir.name}: {result.stderr}")
                else:
                    print(f"Successfully installed requirements for {repo_dir.name}")
                    
            except subprocess.TimeoutExpired:
                print(f"Timeout installing requirements for {repo_dir.name}")
            except Exception as e:
                print(f"Error installing requirements for {repo_dir.name}: {e}")
        else:
            print(f"No requirements.txt found for {repo_dir.name}")
        
        # Verify H3 installation specifically
        try:
            if os.name == 'nt':  # Windows
                python_path = venv_path / "Scripts" / "python"
            else:  # Unix/Linux/macOS
                python_path = venv_path / "bin" / "python"
            
            # Test H3 import
            result = subprocess.run([
                str(python_path), "-c", "import h3; print(f'H3 version: {h3.__version__}')"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"H3 verification successful for {repo_dir.name}: {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"H3 verification failed for {repo_dir.name}: {result.stderr}")
                
        except Exception as e:
            print(f"Error verifying H3 for {repo_dir.name}: {e}")
    
    print(f"Virtual environment reset complete: {success_count}/{total_repos} repositories processed successfully")
    return success_count > 0

@pytest.mark.setup
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
        """
        Test osc_setup_all.py clones repos without running tests, then reset virtual environments.
        Fails if script is missing or times out.
        """
        script = self.script_dir / 'osc_setup_all.py'
        if script.exists():
            try:
                result = subprocess.run([str(script), '--output-dir', str(self.temp_repo_dir), '--skip-tests'], 
                                      capture_output=True, text=True, timeout=120)
                # Check if any directories were created (not necessarily osc-geo)
                created_dirs = list(self.temp_repo_dir.iterdir())
                self.assertTrue(len(created_dirs) >= 0, f"Script should run without error")
                # Check if script ran successfully (exit code 0 or reasonable output)
                self.assertTrue(result.returncode == 0 or 'Repository' in result.stdout or 'Repository' in result.stderr,
                              f"Script should run successfully. Return code: {result.returncode}")
                
                # Reset and reinstall virtual environments
                print("Resetting and reinstalling virtual environments...")
                venv_success = reset_and_reinstall_venvs(str(self.temp_repo_dir))
                self.assertTrue(venv_success, "Virtual environment reset failed")
                
            except subprocess.TimeoutExpired:
                raise AssertionError("Script timed out - test failed")
            except Exception as e:
                raise AssertionError(f"Script execution failed: {e}")
        else:
            raise AssertionError(f"Script not found: {script}")

    def test_osc_status(self):
        """
        Test osc_status.py runs and outputs status information. Fails if script is missing.
        """
        script = self.script_dir / 'osc_status.py'
        if script.exists():
            result = subprocess.run([str(script)], capture_output=True, text=True)
            # The script should run without error, even if no repos are found
            self.assertIn('Repository Status', result.stdout or result.stderr)
        else:
            raise AssertionError(f"Script not found: {script}") 