# Core Development Principles

## 1. NO MOCK METHODS — EVER

- Never create placeholder, stub, or mock methods
- Every function must be fully implemented with real logic
- Use proper error handling instead of `pass` or `NotImplementedError`
- If functionality is complex, break it into smaller, implementable pieces
- Implement real data analysis and processing pipelines

## 2. Maximum Intelligence & Documentation

- Write intelligent, thoughtful code that demonstrates deep understanding
- Include comprehensive docstrings for all functions, classes, and modules
- Use type hints for all function parameters and return values
- Document the mathematical/theoretical basis for algorithms
- Include example usage in docstrings
- Provide mathematical foundations and citations where applicable

## 3. Leverage Existing Module Structure

- Understand and work within the established 44-module hierarchy
- Use the standardised directory structure: `src/`, `docs/`, `examples/`, `tests/`, `config/`
- Follow existing patterns for API design, data models, and utilities
- Import and extend existing functionality rather than reimplementing
- Respect module dependencies and data flow patterns

## 4. Active Inference First

- Ground all implementations in Active Inference mathematical principles
- Implement free energy minimisation where applicable
- Use Bayesian inference for uncertainty quantification (pymc, pymdp)
- Design perception-action loops for autonomous systems
- Apply probabilistic reasoning to spatial-temporal problems
- Reference the Free Energy Principle literature in docstrings

## 5. Concise Professional Communication

- Avoid unnecessary adjectives and descriptive hyperbole
- Use precise, understated language that shows rather than tells
- Prefer "provides" over "provides comprehensive and sophisticated"
- Eliminate redundant descriptors ("advanced", "sophisticated", "cutting-edge")
- Focus on functionality and capabilities rather than marketing language

## 6. Documentation Standards Compliance

- Follow established documentation templates and standards
- Use YAML front matter for machine-readable metadata
- Maintain cross-linking between modules and documentation
- Include working code examples and integration patterns
- Update documentation simultaneously with code changes
- Use consistent terminology and formatting across all docs

## 7. Structured Logging

- Use `logging.getLogger(__name__)` in every module
- Log at appropriate levels: `DEBUG` for internals, `INFO` for operations, `WARNING` for degraded states, `ERROR` for failures
- Include contextual information in log messages (IDs, counts, durations)
- Never use `print()` for operational output in library code
- Use structured key-value pairs where possible

```python
import logging
logger = logging.getLogger(__name__)

def process_data(data: list) -> dict:
    logger.info("Processing %d records", len(data))
    # ...
    logger.debug("Processing complete in %.2fs", duration)
```

## 8. Graceful Dependency Degradation

- Use `try/except ImportError` for optional dependencies
- Provide meaningful fallback behaviour when optional deps are unavailable
- Log a warning when falling back, never fail silently
- Document which features require which optional dependencies

```python
try:
    import pymc as pm
    HAS_PYMC = True
except ImportError:
    HAS_PYMC = False
    logger.warning("pymc not available; Bayesian inference features disabled")
```

## 9. Security First

- Never hardcode secrets, API keys, or credentials in source code
- Use environment variables (`os.environ.get(...)`) or config files for sensitive values
- Validate and sanitise all external inputs
- Follow the principle of least privilege for file and network access
- Monitor dependencies for known CVEs
