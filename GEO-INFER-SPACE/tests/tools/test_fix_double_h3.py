import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_fix_double_h3", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_fix_double_h3_lib(tmp_path: Path):
    mod = load_module("fix_double_h3.py")
    f = tmp_path / "a.py"
    f.write_text("h3_lib.h3_lib.is_valid_cell(x)", encoding="utf-8")

    mod.fix_double_h3_lib(str(f))

    content = f.read_text(encoding="utf-8")
    assert "h3_lib.h3_lib" not in content
    assert "h3_lib.is_valid_cell" in content


