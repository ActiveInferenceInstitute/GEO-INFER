"""Regression tests for CLI exit codes (GS-225).

Command handlers must return bool success and main() must exit non-zero on
handled failures so scripted pipelines can detect failure.
"""

import argparse

import pandas as pd
import pytest

from geo_infer_sec.cli import (
    command_anonymize,
    command_generate_token,
    command_risk_assessment,
)


@pytest.fixture
def nongeo_csv(tmp_path):
    path = tmp_path / "plain.csv"
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_csv(path, index=False)
    return str(path)


def test_anonymize_nongeo_csv_returns_false(nongeo_csv, tmp_path):
    """A non-geospatial CSV must be a handled failure (exit 1 upstream)."""
    args = argparse.Namespace(
        input_file=nongeo_csv,
        output_file=str(tmp_path / "out.geojson"),
        method="perturbation",
        epsilon=100.0,
        k=5,
        h3_resolution=8,
        admin_boundaries=None,
        attribute_cols=None,
    )
    assert command_anonymize(args) is False


def test_anonymize_unsupported_format_returns_false(tmp_path):
    args = argparse.Namespace(
        input_file=str(tmp_path / "data.txt"),
        output_file=str(tmp_path / "out.geojson"),
        method="perturbation",
        epsilon=100.0,
        k=5,
        h3_resolution=8,
        admin_boundaries=None,
        attribute_cols=None,
    )
    (tmp_path / "data.txt").write_text("not data\n")
    assert command_anonymize(args) is False


def test_generate_token_returns_true_and_prints(capsys):
    args = argparse.Namespace(length=16)
    assert command_generate_token(args) is True
    assert "Secure token:" in capsys.readouterr().out


def test_risk_assessment_returns_true(capsys):
    args = argparse.Namespace(name="t1", format="text", output_file=None)
    assert command_risk_assessment(args) is True
