import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_fix_h3_v4_api", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_fix_h3_v3_api_calls(tmp_path):
    mod = load_module("fix_h3_v4_api.py")
    f = tmp_path / "sample.py"
    f.write_text("h3.k_ring(x,1)\nh3.geo_to_h3(1,2,3)\n", encoding="utf-8")

    modified, changes = mod.fix_h3_v3_api_calls(str(f))
    new_content = f.read_text(encoding="utf-8")

    assert modified
    assert "geo_to_h3" not in new_content
    assert len(changes) >= 1


