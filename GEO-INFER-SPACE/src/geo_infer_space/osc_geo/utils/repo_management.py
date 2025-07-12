import os
import sys
import subprocess
from pathlib import Path
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepoManager:
    """
    Manages cloning, setting up, and testing OS-Climate repositories.
    """
    def __init__(self, output_dir: str = "./repo", force_clone: bool = False, verbose: bool = False):
        """
        Initializes the RepoManager.

        Args:
            output_dir (str): Directory where repositories will be cloned.
            force_clone (bool): If True, force re-clones repositories.
            verbose (bool): If True, enable verbose output.
        """
        self.output_dir = Path(output_dir).resolve()
        self.force_clone = force_clone
        self.verbose = verbose
        self.osc_repos = {
            "osc-geo-h3grid-srv": "https://github.com/docxology/osc-geo-h3grid-srv",
            "osc-geo-h3loader-cli": "https://github.com/docxology/osc-geo-h3loader-cli",
        }

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Repository output directory set to: {self.output_dir}")

    def _run_command(self, command: list[str], cwd: Path, description: str):
        """
        Runs a shell command and logs its output.

        Args:
            command (list[str]): The command and its arguments as a list.
            cwd (Path): The current working directory for the command.
            description (str): A description of the command being run for logging.

        Returns:
            bool: True if the command succeeded, False otherwise.
        """
        logger.info(f"Running command: {description} in {cwd}")
        try:
            process = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            if self.verbose:
                logger.info(f"STDOUT:\n{process.stdout}")
            logger.info(f"Successfully ran: {description}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {description}")
            logger.error(f"STDERR:\n{e.stderr}")
            if self.verbose:
                logger.error(f"STDOUT:\n{e.stdout}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while running {description}: {e}")
            return False

    def clone_repos(self, repo_name: str = None) -> bool:
        """
        Clones or updates the specified OS-Climate repositories.

        Args:
            repo_name (str, optional): The name of a specific repository to clone.
                                       If None, all configured repositories will be cloned.

        Returns:
            bool: True if all specified repositories were successfully cloned/updated, False otherwise.
        """
        repos_to_clone = {repo_name: self.osc_repos[repo_name]} if repo_name else self.osc_repos
        all_succeeded = True

        for name, url in repos_to_clone.items():
            repo_path = self.output_dir / name
            if repo_path.exists():
                if self.force_clone:
                    logger.info(f"Force cloning: Removing existing repository at {repo_path}")
                    shutil.rmtree(repo_path)
                else:
                    logger.info(f"Repository {name} already exists at {repo_path}. Pulling latest changes.")
                    if not self._run_command(["git", "pull"], cwd=repo_path, description=f"pulling {name}"):
                        all_succeeded = False
                    continue

            logger.info(f"Cloning {url} into {repo_path}")
            if not self._run_command(["git", "clone", url, str(repo_path)], cwd=self.output_dir, description=f"cloning {name}"):
                all_succeeded = False

        return all_succeeded

    def setup_repo_venv_and_install(self, repo_name: str) -> bool:
        """
        Sets up a virtual environment and installs dependencies for a given repository.

        Args:
            repo_name (str): The name of the repository to set up.

        Returns:
            bool: True if setup and installation succeeded, False otherwise.
        """
        repo_path = self.output_dir / repo_name
        venv_path = repo_path / "venv"
        
        if not repo_path.exists():
            logger.error(f"Repository directory not found: {repo_path}. Please clone it first.")
            return False

        logger.info(f"Setting up virtual environment for {repo_name} at {venv_path}")
        if not self._run_command([sys.executable, "-m", "venv", str(venv_path)], cwd=repo_path, description=f"creating venv for {repo_name}"):
            return False
        
        # Determine pip executable path within the new venv
        pip_executable = venv_path / "bin" / "pip"

        logger.info(f"Installing pip in virtual environment for {repo_name}")
        if not self._run_command([str(pip_executable), "install", "--upgrade", "pip"], cwd=repo_path, description=f"upgrading pip in venv for {repo_name}"):
            return False

        requirements_path = repo_path / "requirements.txt"
        if requirements_path.exists():
            logger.info(f"Installing dependencies from {requirements_path} for {repo_name}")
            if not self._run_command([str(pip_executable), "install", "-r", str(requirements_path)], cwd=repo_path, description=f"installing requirements for {repo_name}"):
                return False
        else:
            logger.warning(f"No requirements.txt found for {repo_name} at {requirements_path}. Skipping dependency installation.")
        
        logger.info(f"Setting up PYTHONPATH for {repo_name}")
        # Add the repository's src directory to PYTHONPATH for tests
        repo_src_path = repo_path / "src"
        if repo_src_path.exists():
            # This needs to be set in the subprocess environment for tests
            # For direct imports, we'll add it to sys.path in setup.py commands
            logger.info(f"Added {repo_src_path} to PYTHONPATH for {repo_name} operations.")
        
        return True

    def run_repo_tests(self, repo_name: str) -> bool:
        """
        Runs the test suite for a given repository.

        Args:
            repo_name (str): The name of the repository to test.

        Returns:
            bool: True if tests passed, False otherwise.
        """
        repo_path = self.output_dir / repo_name
        venv_python = repo_path / "venv" / "bin" / "python"
        
        if not repo_path.exists():
            logger.error(f"Repository directory not found: {repo_path}. Please clone it first.")
            return False
        
        if not venv_python.exists():
            logger.error(f"Virtual environment not found for {repo_name} at {venv_python}. Please set it up first.")
            return False

        logger.info(f"Running tests for {repo_name}")
        # Adjust PYTHONPATH for the test run
        env = os.environ.copy()
        repo_src_path = repo_path / "src"
        if repo_src_path.exists():
            env["PYTHONPATH"] = str(repo_src_path) + os.pathsep + env.get("PYTHONPATH", "")

        return self._run_command(
            [str(venv_python), "-m", "pytest", str(repo_path / "test")],
            cwd=repo_path,
            description=f"running tests for {repo_name}",
            env=env # Pass modified environment here
        )

    def run_all(self, target_repo: str = None) -> None:
        """
        Executes the full setup and test workflow.

        Args:
            target_repo (str, optional): If specified, only run for this repository.
                                         Otherwise, run for all configured repositories.
        """
        repos_to_process = [target_repo] if target_repo else list(self.osc_repos.keys())
        
        overall_success = True

        for repo in repos_to_process:
            logger.info(f"--- Processing {repo} ---")
            
            # Clone/Update
            if not self.clone_repos(repo_name=repo):
                logger.error(f"Failed to clone/update {repo}. Skipping further steps for this repo.")
                overall_success = False
                continue

            # Setup Venv and Install Dependencies
            if not self.setup_repo_venv_and_install(repo_name=repo):
                logger.error(f"Failed to set up virtual environment or install dependencies for {repo}. Skipping tests.")
                overall_success = False
                continue

            # Run Tests
            if not self.run_repo_tests(repo_name=repo):
                logger.error(f"Tests failed for {repo}.")
                overall_success = False
                continue
            
            logger.info(f"--- Successfully processed {repo} ---")

        if overall_success:
            logger.info("All specified repositories processed successfully.")
        else:
            logger.error("Some repositories failed to process correctly.")

def main():
    """Main entry point for the repo_management script."""
    # This main function is a placeholder and won't be directly used once integrated into setup.py
    # It demonstrates how RepoManager would be used.
    # In setup.py, we'll parse arguments differently and call methods directly.
    manager = RepoManager(force_clone=True, verbose=True)
    manager.run_all()

if __name__ == "__main__":
    main() 