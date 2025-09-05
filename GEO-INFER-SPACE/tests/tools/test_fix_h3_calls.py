import importlib.util
from pathlib import Path


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location("_fix_h3_calls", tools_dir / module_filename)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_fix_h3_calls_in_file(tmp_path: Path):
    mod = load_module("fix_h3_calls.py")
    source = tmp_path / "viz.py"
    source.write_text(
        """
is_valid_cell(cell)
cell_to_boundary(cell)
get_resolution(cell)
cell_area(cell)
cell_to_latlng(cell)
latlng_to_cell(1,2,3)
""",
        encoding="utf-8",
    )

    mod.fix_h3_calls_in_file(str(source))

    content = source.read_text(encoding="utf-8")
    assert "h3_lib.is_valid_cell" in content
    assert "h3_lib.cell_to_boundary" in content
    assert "h3_lib.get_resolution" in content
    assert "h3_lib.cell_area" in content
    assert "h3_lib.cell_to_latlng" in content
    assert "h3_lib.latlng_to_cell" in content


