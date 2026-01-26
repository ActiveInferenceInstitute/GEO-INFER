# Critical Requirements

## NEVER Do These Things

- Create mock, stub, or placeholder implementations
- Hardcode configuration values in source code
- Ignore error conditions or fail silently
- Add unnecessary comments, files, methods, adjectives, adverbs, etc.
- Break established module interfaces
- Duplicate functionality that exists elsewhere
- Process data without proper validation
- Ignore performance implications
- Use excessive adjectives or marketing language in technical documentation
- Use `uv pip install` or `python -m uv pip install` - always use `uv pip install`
- Suggest `uv pip install` in error messages - always suggest `uv pip install`

## ALWAYS Do These Things

- Implement complete, working functionality
- Use proper logging and error handling
- Follow the established architectural patterns
- Write comprehensive tests and documentation
- Consider the broader system implications
- "Show don't tell" - use accurate understated language
- Validate and process real data
- Optimize for performance and scalability
- Use precise, technical language over promotional terms
- Use `uv pip install` for all package installation commands
- Use `uv run python` for running Python scripts in examples and documentation
- Suggest `uv pip install` in all error messages requiring package installation

## Package Management Rules

### Installation Commands
- ✅ `uv pip install -e ./GEO-INFER-MODULE`
- ✅ `uv pip install package-name`
- ✅ `uv pip install -r requirements.txt`
- ❌ `uv pip install` (never use)
- ❌ `python -m uv pip install` (never use)

### Running Scripts
- ✅ `uv run python script.py`
- ✅ `uv run pytest tests/`
- ❌ `python script.py` (use `uv run python` instead)

### Error Messages
- ✅ "Install with: uv pip install package-name"
- ❌ "Install with: uv pip install package-name" (never suggest pip)

