# Advanced Topics

This guide covers techniques for optimizing performance, building custom
models, and scaling GEO-INFER applications to production environments. It is
the advanced companion to the [User Guide](../user_guide/index.md) and the
[Architecture](../architecture/index.md) pages.

## Performance Optimization

- [Performance Optimization Guide](performance_optimization.md) — spatial
  indexing strategies, memory management, parallel processing, and caching for
  large datasets.
- [Scaling Guide](scaling_guide.md) — distributed computing, cloud deployment,
  load balancing, and resource allocation at scale.
- [Memory Management](memory_management.md) — chunked processing, streaming,
  memory profiling, and memory-efficient data structures.

## Custom Model Development

- [Custom Models](custom_models.md) — model architecture patterns, custom
  transition and observation models, precision weighting, and validation.
- [Module catalog](../modules/index.md) — the built-in domain models shipped
  across the 44 GEO-INFER modules (environmental, urban, agricultural,
  economic, and risk).
- [Integration guide](../integration/index.md) — integrating custom models
  with the framework: API design, data flow, serialization, and versioning.

## System Architecture

- [Architecture overview](../architecture/index.md) — system design, data
  pipelines, API design, and observability for GEO-INFER applications.
- [Integration patterns](../integration/index.md) — database, API, message
  queue, and event-driven integration with external systems.
- [Security guidance](../security/index.md) — authentication, authorization,
  encryption, audit logging, and privacy.

## Analytics

- [Spatial analysis](../geospatial/analysis/index.md) — spatial statistics,
  geostatistics, spatial machine learning, and spatial optimization.
- [Temporal analysis](../temporal_analysis_guide.md) — time series modeling,
  forecasting with uncertainty, change detection, and anomaly detection.
- [Scale and resolution](../geospatial/concepts/scale_resolution.md) —
  hierarchical and multi-scale analysis concepts.

## Research and Development

- [Research-grade inference contracts](../research_grade_inference_contracts.md)
  — executable ACT, BAYES, and RISK behavior, uncertainty, and verification.
- [Testing guide](../developer_guide/testing_guide.md) — cross-validation,
  out-of-sample testing, sensitivity analysis, and model comparison.
- [Manuscript and evidence](../../../manuscript/README.md) — the repository
  manuscript pipeline and generated research artifacts.

## Production Deployment

- [Production architecture](production_architecture.md) — high availability,
  fault tolerance, disaster recovery, and capacity planning.
- [Deployment guide](../deployment/index.md) — cloud platforms, Kubernetes,
  and serverless deployment.
- [Developer guide](../developer_guide/index.md) — CI/CD, infrastructure as
  code, configuration management, and monitoring.

## Debugging and Quality

- [Troubleshooting](../support/troubleshooting.md) — profiling, memory leak
  detection, and concurrency debugging.
- [Testing strategies](../developer_guide/testing_guide.md) — unit,
  integration, performance, load, and security testing.
- [Repository guidelines](../developer_guide/repo_guidelines.md) — code
  review, documentation standards, error handling, and logging.

## Monitoring

- [Scaling and monitoring](../deployment/scaling.md) — application performance
  monitoring, alerting, and dashboard design.
- [Performance tuning](performance_optimization.md) — database and query
  optimization, caching, and load balancing.

## External Systems

- [External systems](../integration/external_systems.md) — GIS software,
  databases, cloud services, and real-time data streams.
- [API documentation](../api/index.md) — REST API design, versioning, and
  WebSocket patterns.

## Getting Started with Advanced Topics

### Choose Your Path

**Performance Focus:**

1. [Performance Optimization](performance_optimization.md)
2. [Memory Management](memory_management.md)
3. [Scaling Guide](scaling_guide.md)

**Custom Development:**

1. [Custom Models](custom_models.md)
2. [Module catalog](../modules/index.md)
3. [Integration guide](../integration/index.md)

**Production Deployment:**

1. [Production Architecture](production_architecture.md)
2. [Deployment guide](../deployment/index.md)
3. [Developer guide](../developer_guide/index.md)

**Research Applications:**

1. [Research-grade inference contracts](../research_grade_inference_contracts.md)
2. [Testing guide](../developer_guide/testing_guide.md)
3. [Examples gallery](../examples_gallery.md)

### Prerequisites

Before diving into advanced topics, ensure you have:

- Basic GEO-INFER knowledge — see the [Getting Started](../getting_started/index.md) guide.
- Python expertise and familiarity with the module [API reference](../api/reference.md).
- Spatial data experience — see [Spatial concepts](../geospatial/concepts/index.md).
- Statistics and linear algebra background — see
  [Bayesian inference guide](../bayesian_inference_guide.md).

### Learning Resources

- [API Reference](../api/reference.md)
- [Examples gallery](../examples_gallery.md)
- [Tutorials](../tutorials/index.md)

## Success Metrics

Track your skills development:

- **Performance optimization** — applications running measurably faster.
- **Custom model development** — built models for your domain.
- **Production deployment** — successfully deployed to a production environment.
- **Research contribution** — published or presented work using GEO-INFER.
- **Community contribution** — helped other users with advanced topics.

## Related Resources

### Documentation

- [User Guide](../user_guide/index.md)
- [Developer Guide](../developer_guide/index.md)
- [API Reference](../api/reference.md)

### Community

- [Contributing Guide](../../../CONTRIBUTING.md)
- [Code of Conduct](../../../CODE_OF_CONDUCT.md)
- [Release history](../../../CHANGELOG.md)

Ready to advance? Choose a path above and dive into the topics that interest
you most.
