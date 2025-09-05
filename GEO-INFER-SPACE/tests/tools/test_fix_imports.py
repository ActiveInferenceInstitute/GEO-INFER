import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_fix_imports", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


essage = "from h3.module import something\n"

def test_fix_imports_in_file(tmp_path: Path):
    mod = load_module("fix_imports.py")
    f = tmp_path / "ex.py"
    f.write_text(essage, encoding="utf-8")

    mod.fix_imports_in_file(str(f))

    content = f.read_text(encoding="utf-8")
    assert content.startswith("from module import something")


