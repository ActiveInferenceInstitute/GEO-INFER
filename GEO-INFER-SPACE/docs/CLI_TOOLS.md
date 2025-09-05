### GEO-INFER-SPACE CLI Tools

The SPACE module exposes a set of CLI tools to assist with H3 v4 migration, verification, and diagnostics.

Prerequisite: Install the module in editable mode.
```bash
uv pip install -e ./GEO-INFER-SPACE
```

#### Commands

- gis-verify-h3-v4: Verify codebase uses H3 v4 API and report v3 remnants
- gis-fix-h3-v4: Apply automated H3 v3→v4 replacements across the codebase
- gis-fix-h3-calls: Normalize H3 calls (adds h3_lib prefixes in legacy examples)
- gis-fix-double-h3: Remove duplicated h3_lib.h3_lib prefixes
- gis-fix-imports: Simplify example imports (remove h3. prefix)
- gis-fix-rel-imports: Convert relative imports to absolute in legacy H3 examples
- gis-h3-tests: Run simple H3 functionality checks

All tools can be executed from the repo root or any subdirectory; they resolve targets robustly.


