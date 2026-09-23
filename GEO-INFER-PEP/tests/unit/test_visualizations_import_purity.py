"""Import-purity tests for PEP visualization modules (GS19-75).

Contract: importing the visualization modules must not mutate the filesystem
(SKILL.md forbids import-time state mutation); output directories are created
on write by the plot functions.
"""

import importlib
import sys
from pathlib import Path

import pytest

VISUAL_MODULES = [
    "geo_infer_pep.visualizations.crm_visuals",
    "geo_infer_pep.visualizations.hr_visuals",
    "geo_infer_pep.visualizations.talent_visuals",
]


@pytest.fixture()
def fresh_import_cwd(tmp_path, monkeypatch):
    """Run imports in a pristine cwd with the visual modules freshly loaded."""
    monkeypatch.chdir(tmp_path)
    saved = {name: sys.modules.pop(name, None) for name in VISUAL_MODULES}
    sys.modules.pop("geo_infer_pep.visualizations", None)
    yield tmp_path
    for name, module in saved.items():
        if module is not None:
            sys.modules[name] = module


def test_import_creates_no_output_directories(fresh_import_cwd):
    cwd = fresh_import_cwd
    for name in VISUAL_MODULES:
        importlib.import_module(name)
    assert not (cwd / "visualizations_output").exists()


def test_plot_creates_directory_on_write(fresh_import_cwd):
    """Plotting creates the output directory only when saving."""
    cwd = fresh_import_cwd
    import matplotlib

    matplotlib.use("Agg", force=True)
    talent = importlib.import_module("geo_infer_pep.visualizations.talent_visuals")

    out_dir = cwd / "created_on_write"
    assert not out_dir.exists()

    result = talent.plot_time_to_hire_distribution([1, 2, 3, 4, 5], output_dir=out_dir)
    assert result is not None
    assert Path(result).exists()
    assert out_dir.exists()
