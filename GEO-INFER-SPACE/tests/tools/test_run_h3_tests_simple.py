import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_run_h3_tests_simple", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


essage = ""

def test_run_h3_tests_main_smoke():
    mod = load_module("run_h3_tests_simple.py")
    rc = mod.main()
    assert isinstance(rc, int)


