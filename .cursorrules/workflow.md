# Development Workflow

## Environment Management with uv

**All environment management and package installation MUST use `uv`**:
- **Installation**: Always use `uv pip install` instead of `pip install`
- **Running Scripts**: Use `uv run python` instead of `python` for scripts
- **Dependencies**: All dependency installation commands in documentation and code must use `uv`
- **Error Messages**: All error messages suggesting package installation must recommend `uv pip install`
- **Setup Scripts**: All setup and installation scripts must use `uv` commands

**Rationale**: `uv` provides faster, more reliable package management and is the standard tool for the GEO-INFER framework.

## Before Writing Code

1. **Understand the Module**: Read the module's README and existing documentation
2. **Check Dependencies**: Understand which other GEO-INFER modules are dependencies
3. **Review Examples**: Look at existing examples to understand usage patterns
4. **Plan Integration**: Consider how your code will interact with other modules
5. **Analyze Data Requirements**: Understand input/output data formats and sources

## While Writing Code

1. **Follow Existing Patterns**: Maintain consistency with existing code style
2. **Document as You Go**: Write docstrings and comments simultaneously with code
3. **Test Incrementally**: Write unit tests for each function/method
4. **Consider Performance**: Optimize for both memory and computational efficiency
5. **Validate Data**: Implement proper data validation and error handling

## After Writing Code

1. **Comprehensive Testing**: Ensure all code paths are tested
2. **Integration Testing**: Test cross-module interactions
3. **Documentation Updates**: Update READMEs and API documentation
4. **Example Creation**: Create working examples demonstrating functionality
5. **Performance Validation**: Test with realistic data volumes

## Data-Driven Development

### Real Data Processing

- Always work with real data sources and formats
- Implement proper data validation and quality control
- Build scalable data processing pipelines
- Support multiple data formats and sources
- Include data transformation capabilities

### Performance Optimization

- Profile code with realistic data volumes
- Implement efficient algorithms and data structures
- Use appropriate caching and indexing strategies
- Optimize for both memory and computational efficiency
- Test scalability with large datasets

### Quality Assurance

- Validate data integrity and consistency
- Implement comprehensive error handling
- Test with diverse data sources and formats
- Monitor performance and resource usage
- Document data requirements and constraints

