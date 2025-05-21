# GEO-INFER-OPS

## Overview
GEO-INFER-OPS is the operational kernel for the GEO-INFER framework, providing essential infrastructure for logging, monitoring, testing, and configuration management. This module serves as the foundation for ensuring reliable, scalable, and maintainable operations across all GEO-INFER components.

## Architecture

```mermaid
graph TB
    subgraph Core Components
        C[Configuration]
        L[Logging]
        M[Monitoring]
        T[Testing]
    end
    
    subgraph External Systems
        P[Prometheus]
        G[Grafana]
        D[Docker]
        K[Kubernetes]
    end
    
    subgraph Other Modules
        SEC[GEO-INFER-SEC]
        DATA[GEO-INFER-DATA]
        API[GEO-INFER-API]
        APP[GEO-INFER-APP]
    end
    
    C --> L
    C --> M
    C --> T
    
    L --> P
    M --> P
    P --> G
    
    T --> D
    T --> K
    
    SEC --> C
    DATA --> C
    API --> C
    APP --> C
```

## Key Features

### Configuration Management
- YAML-based configuration with validation
- Environment-specific settings
- Secure credential management
- Dynamic configuration updates

### Logging System
- Structured logging with JSON output
- Multiple log levels and formats
- File and console output
- Custom log processors

### Monitoring
- Prometheus metrics integration
- Request/response tracking
- Error rate monitoring
- Resource usage metrics
- Grafana dashboards

### Testing Framework
- Automated test suite
- Coverage reporting
- Parallel test execution
- Mock utilities
- Test data management

## Directory Structure

```mermaid
graph TD
    A[GEO-INFER-OPS] --> B[src]
    A --> C[config]
    A --> D[deployment]
    A --> E[monitoring]
    A --> F[tests]
    A --> G[docs]
    
    B --> B1[geo_infer_ops]
    B1 --> B2[core]
    B1 --> B3[api]
    B1 --> B4[models]
    B1 --> B5[utils]
    
    C --> C1[example.yaml]
    C --> C2[local.yaml]
    
    D --> D1[kubernetes]
    D --> D2[docker]
    
    E --> E1[prometheus]
    E --> E2[grafana]
    
    F --> F1[test_config.py]
    F --> F2[test_logging.py]
    F --> F3[test_monitoring.py]
    F --> F4[test_testing.py]
```

## Getting Started

### Installation
```bash
pip install -e .
```

### Configuration
```bash
cp config/example.yaml config/local.yaml
# Edit local.yaml with your configuration
```

### Running Tests
```bash
pytest tests/
```

## Integration with Other Modules

```mermaid
sequenceDiagram
    participant App as GEO-INFER-APP
    participant API as GEO-INFER-API
    participant Data as GEO-INFER-DATA
    participant Sec as GEO-INFER-SEC
    participant Ops as GEO-INFER-OPS
    
    App->>Ops: Initialize logging
    Ops-->>App: Configured logger
    
    API->>Ops: Setup monitoring
    Ops-->>API: Configured metrics
    
    Data->>Ops: Load configuration
    Ops-->>Data: Validated config
    
    Sec->>Ops: Setup testing
    Ops-->>Sec: Test environment
```

## Deployment

### Docker
```bash
docker build -t geo-infer-ops .
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

## Monitoring Dashboard

```mermaid
graph LR
    subgraph Metrics Collection
        A[Application] --> B[Prometheus]
        C[System] --> B
    end
    
    subgraph Visualization
        B --> D[Grafana]
        D --> E[Dashboard 1]
        D --> F[Dashboard 2]
        D --> G[Dashboard 3]
    end
    
    subgraph Alerts
        B --> H[Alert Manager]
        H --> I[Email]
        H --> J[Slack]
    end
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 