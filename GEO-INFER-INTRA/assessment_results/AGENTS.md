# Agent Instructions: GEO-INFER-INTRA/assessment_results

## Scope

- Owning module: `GEO-INFER-INTRA`
- Python package: `geo_infer_intra`
- Directory role: Assessment Results workspace within `GEO-INFER-INTRA`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_intra` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `AGENTS_DOC_AUDIT.md`
- `AGENTS_DOC_REVIEW_COMPLETE.md`
- `ASSESSMENT_SUMMARY.md`
- `COMPREHENSIVE_PROGRESS_SUMMARY.md`
- `COMPREHENSIVE_REPOSITORY_ASSESSMENT.md`
- `COMPREHENSIVE_REVIEW_DETAILED.md`
- `COMPREHENSIVE_REVIEW_INDEX.md`
- `COMPREHENSIVE_REVIEW_ROADMAP.md`
- `COMPREHENSIVE_REVIEW_SUMMARY.md`
- `COMPREHENSIVE_UV_MIGRATION_REPORT.md`
- `DEPENDENCY_ANALYSIS.md`
- `DEPENDENCY_VALIDATION_REPORT.md`
- `DEPENDENCY_VALIDATION_SUMMARY.md`
- `HARMONIZATION_ROADMAP.md`
- `IMPLEMENTATION_PROGRESS.md`
- `IMPROVEMENTS_SUMMARY.md`
- `STANDARDS_COMPLIANCE_CHECKLIST.md`
- `TEST_FIXES_SUMMARY.md`
- `UV_MIGRATION_SUMMARY.md`
- `comprehensive_assessment.json`
- `comprehensive_assessment.md`
- `comprehensive_review_2025.json`
- `comprehensive_review_issues_2025.json`
- `comprehensive_review_summary_2025.json`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
