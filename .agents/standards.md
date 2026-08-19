# Excellence Standards & Code Review

## Code Review Checklist

### Functionality

- [ ] No mock or placeholder methods
- [ ] All functions fully implemented with real logic
- [ ] Proper error handling (specific exceptions, logging)
- [ ] Mathematical correctness validated with tests
- [ ] Data processing pipelines complete and tested
- [ ] Graceful degradation for optional dependencies

### Documentation

- [ ] Google-style docstrings for all public APIs
- [ ] Type hints for all parameters, returns, and attributes
- [ ] README.md updated if module behaviour changed
- [ ] AGENTS.md updated if key files or patterns changed
- [ ] Examples provided and verified to run
- [ ] Mathematical foundations documented with citations
- [ ] Language is concise and professional

### Integration

- [ ] Follows established module patterns
- [ ] Uses standardised data models (Pydantic at boundaries)
- [ ] Properly handles cross-module dependencies
- [ ] Uses H3 v4 API exclusively for spatial operations
- [ ] Respects layered architecture (Foundation → Data → Domain → App)

### Quality

- [ ] Code formatted with Black and isort
- [ ] Passes ruff check with 0 errors
- [ ] Test coverage ≥80% for modified files
- [ ] Performance tested with realistic data volumes
- [ ] Security: no hardcoded secrets, inputs validated
- [ ] Structured logging (no `print()` statements)

## Code Formatting

```bash
# Format code
black .
isort .

# Lint
ruff check --fix .

# Type check (core modules)
mypy --strict src/
```

## Commit Message Conventions

```
<type>(<scope>): <description>

<body>
```

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or correcting tests |
| `chore` | Build process, tooling, dependencies |

Examples:

- `feat(RISK): implement spatial autocorrelation (Moran's I)`
- `fix(COMMS): resolve subscriber lookup returning empty list`
- `docs(AGENT): update AGENTS.md with telemetry patterns`

## Framework Status (2026-02-25)

| Area | Status |
|------|--------|
| Documentation Quality | ✅ Standards established, YAML front matter applied |
| Integration Patterns | ✅ Cross-module tutorials created |
| Testing Framework | ✅ Unified test suite operational (416 files) |
| H3 v4 Migration | ✅ Fully migrated (0 legacy calls) |
| Module Maturity | Mixed — Core: Beta, Domain: Alpha-Beta |
| Placeholder Count | ~50 remaining (down from 86) |

## Current Priorities

### High Priority

1. Eliminate remaining LOG placeholders (19 across delivery/transport/supply_chain)
2. Complete RISK exposure model data loaders (6 remaining)
3. Replace BAYES tfp_interface placeholder
4. Achieve ≥80% test coverage across all 44 modules

### Medium Priority

1. Mypy strict mode passing in all analytical core modules
2. Automated documentation generation (Sphinx)
3. Performance benchmarks for spatial operations
4. Expand property-based (Hypothesis) tests

## Release Checklist

Before tagging any version release:

- [ ] All tests pass: `uv run python GEO-INFER-TEST/run_unified_tests.py`
- [ ] 0 placeholder/stub implementations in source code
- [ ] 0 `pass` stubs (excluding `__init__.py`, `except`, abstract methods)
- [ ] Black/isort/ruff clean
- [ ] Coverage ≥80% per module
- [ ] README.md + AGENTS.md up to date in all 44 modules
- [ ] CHANGELOG.md entries for this version
- [ ] `pyproject.toml` version updated
- [ ] TODO.md progress metrics refreshed

---

Every line of code should reflect production-quality engineering: mathematical rigour, functional completeness, structured logging, and precise documentation. Use technical accuracy over promotional language.
