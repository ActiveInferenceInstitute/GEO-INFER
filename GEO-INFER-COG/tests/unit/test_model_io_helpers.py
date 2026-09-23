"""Round-trip tests for cognitive model load/save helpers (GS19-55).

Regression contract: ``load_cognitive_model`` accepts str and Path inputs,
parses JSON and YAML by suffix, and reports failures as an empty dict.
"""


import pytest

from geo_infer_cog.utils.helpers import load_cognitive_model, save_cognitive_model


@pytest.fixture()
def model_config():
    return {"name": "attention", "layers": 3, "parameters": {"rate": 0.5}}


def test_round_trip_json(tmp_path, model_config):
    path = tmp_path / "model.json"
    assert save_cognitive_model(model_config, path) is True
    assert load_cognitive_model(path) == model_config


def test_round_trip_yaml(tmp_path, model_config):
    path = tmp_path / "model.yaml"
    assert save_cognitive_model(model_config, path) is True
    assert load_cognitive_model(path) == model_config


def test_round_trip_string_path(tmp_path, model_config):
    """str and Path inputs are both accepted (str input used to return {})."""
    path = tmp_path / "model.json"
    assert save_cognitive_model(model_config, path) is True
    assert load_cognitive_model(str(path)) == model_config


def test_yml_suffix_parsed_as_yaml(tmp_path, model_config):
    path = tmp_path / "model.yml"
    path.write_text("name: memory\nlayers: 2\n", encoding="utf-8")
    assert load_cognitive_model(path) == {"name": "memory", "layers": 2}


def test_invalid_path_returns_empty_dict(tmp_path, model_config):
    path = tmp_path / "missing.json"
    save_cognitive_model(model_config, path)
    assert load_cognitive_model(tmp_path / "nonexistent.json") == {}
