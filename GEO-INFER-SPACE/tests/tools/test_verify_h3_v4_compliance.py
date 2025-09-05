import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_verify_h3_v4", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_verifier_detects_v3_and_v4(tmp_path):
    mod = load_module("verify_h3_v4_compliance.py")
    v3 = tmp_path / "old.py"
    v4 = tmp_path / "new.py"

    v3.write_text("h3.geo_to_h3(1,2,3)\n", encoding="utf-8")
    v4.write_text("h3.latlng_to_cell(1,2,3)\n", encoding="utf-8")

    has_v3, issues = mod.check_file_for_v3_api(str(v3))
    has_v4, usage = mod.check_file_for_v4_api(str(v4))

    assert has_v3 and issues
    assert has_v4 and usage


