# Support and Troubleshooting

Use this page to diagnose repository-backed workflows. Start with the exact
command and traceback, then narrow the issue to a module or validator.

## First checks

```bash
git status --short
uv run python -c "import sys; print(sys.executable)"
uv pip check
uv run python GEO-INFER-TEST/run_unified_tests.py --list-modules
```

If an import or test result differs between shells, run the same command under
`uv run` and verify the lockfile has been synced.

## Choose the issue type

- [Installation issues](installation_issues.md) — Python, uv, optional
  dependencies, and H3 installation.
- [Troubleshooting](troubleshooting.md) — systematic diagnosis and common
  runtime boundaries.
- [Performance issues](performance_issues.md) — memory, cell-count, and
  computational scaling.
- [FAQ](faq.md) — concise answers to common repository questions.
- [Security policy](../../../SECURITY.md) — vulnerability reporting and
  security responsibilities.

## Error triage

1. Read the full traceback and identify the last exception.
2. Confirm the interpreter with `uv run python`.
3. Identify the owning module from the traceback path.
4. Reproduce with the smallest real input.
5. Run the focused test or validator from that module.
6. Open a GitHub issue with the command, environment, traceback, expected
   behavior, and a minimal reproducible example if the problem remains.

## Common boundaries

### H3

Verify `h3>=4.5.0,<5`, use v4 names, and keep latitude/longitude order
explicit. See the [H3 guide](../geospatial/data_formats/h3/index.md).

### Documentation

Run:

```bash
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
git diff --check
```

### Tests

A strict run rejects warnings, skips, xfails, empty selections, collection
errors, and unavailable required dependencies. See the
[testing guide](../developer_guide/testing_guide.md).

### Artifacts

Inspect `.geo-infer-test-results/` for JUnit, summary, model-audit, and
manifest evidence. Scenario outputs must use explicit directories and remain
outside the repository root.

## Report a bug

Use the [bug report template](../../../.github/ISSUE_TEMPLATE/bug_report.md).
Include the module, package version, Python version, command, traceback, input
shape/CRS/units, and the smallest reproducer. Do not include secrets or
sensitive location data.
