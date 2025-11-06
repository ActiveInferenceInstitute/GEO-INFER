# Implementation Guidelines

## Code Quality Standards

- Use professional, functional, intelligent, modular, concise, elegant code
- Apply all programming best practices thoughtfully
- Write clearly-commented, interpretable code
- Assess context and file type before making changes
- Implement proper error handling and logging
- Follow PEP 8 style guidelines with Black formatting

## Mathematical Rigor

- Ground implementations in solid mathematical foundations
- Use numpy/scipy for numerical computations
- Implement proper statistical methods for uncertainty
- Validate mathematical correctness with unit tests
- Document mathematical assumptions and limitations
- Include mathematical derivations in docstrings

## Geospatial Standards

- Use established geospatial libraries (geopandas, shapely, rasterio, h3)
- Implement proper coordinate reference system handling
- Support standard geospatial formats (GeoJSON, Shapefile, GeoTIFF, COG)
- Follow OGC standards where applicable
- Handle spatial and temporal indexing efficiently
- Integrate with OS-Climate H3 tools when appropriate

## Data-Driven Architecture

- Design for real data processing and analysis
- Implement robust data validation and quality control
- Support multiple data formats and sources
- Build scalable data pipelines
- Include data transformation and preprocessing capabilities
- Implement caching and optimization strategies

## Integration Patterns

- Design for cross-module integration from the start
- Use standardized data models and interfaces
- Implement proper dependency injection patterns
- Support both synchronous and asynchronous communication
- Design for scalability and performance
- Follow established data flow patterns between modules

## Performance Optimization

- Profile code with realistic data volumes
- Implement efficient algorithms and data structures
- Use appropriate caching and indexing strategies
- Optimize for both memory and computational efficiency
- Test scalability with large datasets

## Quality Assurance

- Validate data integrity and consistency
- Implement comprehensive error handling
- Test with diverse data sources and formats
- Monitor performance and resource usage
- Document data requirements and constraints

