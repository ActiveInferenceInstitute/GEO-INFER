### Testing (SPACE)

Run the SPACE test suite:
```bash
cd GEO-INFER-SPACE
uv pip install -e .[dev]
pytest -q
```

#### Tool Tests

Tool-specific tests live under `tests/tools/` and validate behaviors using temporary files.

#### H3 Tests

Core H3 tests are in `tests/test_h3_core.py` and the direct runner is available via:
```bash
gis-h3-tests
```


