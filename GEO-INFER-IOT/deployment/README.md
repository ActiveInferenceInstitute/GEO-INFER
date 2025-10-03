# Deployment Guide

This guide provides comprehensive deployment instructions for the GEO-INFER-IOT module, including Docker, Kubernetes, and cloud deployment options.

## Quick Start

### Using Docker Compose (Recommended for Development)

1. **Prerequisites**
   - Docker (version 20.10+)
   - Docker Compose (version 2.0+)
   - Git

2. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd GEO-INFER/GEO-INFER-IOT
   ```

3. **Deploy Services**
   ```bash
   # Make deployment script executable
   chmod +x deployment/deploy.sh

   # Deploy with Docker Compose
   ./deployment/deploy.sh docker
   ```

4. **Access the Application**
   - **REST API**: http://localhost:8000
   - **WebSocket API**: ws://localhost:8001
   - **Grafana Dashboard**: http://localhost:3000 (admin/admin)
   - **MQTT Broker**: mqtt://localhost:1883

### Using Kubernetes

1. **Prerequisites**
   - Kubernetes cluster (kubectl configured)
   - Docker

2. **Deploy**
   ```bash
   ./deployment/deploy.sh kubernetes
   ```

3. **Access**
   ```bash
   kubectl get services -n geo-infer-iot
   ```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IoT Devices   │────│   MQTT Broker   │────│   GEO-INFER-IOT │
│   (Sensors)     │    │   (Mosquitto)   │    │   API Service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Time Series   │    │   Spatial DB    │    │   Redis Cache   │
│   Database      │    │   (PostGIS)     │    │                 │
│   (InfluxDB)    │    └─────────────────┘    └─────────────────┘
└─────────────────┘              │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Visualization │    │   Metrics       │
│   (Prometheus)  │    │   (Grafana)     │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Deployment Options

### 1. Docker Compose (Development/Testing)

**Features:**
- Complete development environment
- Hot-reload for development
- Monitoring and visualization included
- Easy scaling for testing

**Services Included:**
- **geo-infer-iot-api**: Main IoT API service
- **mqtt-broker**: Eclipse Mosquitto MQTT broker
- **influxdb**: Time series database for sensor data
- **postgres**: PostGIS spatial database
- **redis**: In-memory cache and message broker
- **grafana**: Monitoring and visualization dashboard
- **prometheus**: Metrics collection and alerting
- **nginx**: Reverse proxy and load balancer

**Usage:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f geo-infer-iot-api

# Stop services
docker-compose down

# Scale API service
docker-compose up -d --scale geo-infer-iot-api=3
```

### 2. Kubernetes (Production)

**Features:**
- High availability and scalability
- Auto-scaling based on load
- Rolling updates
- Service mesh integration ready

**Prerequisites:**
- Kubernetes cluster
- kubectl configured
- Container registry (ECR, GCR, etc.)

**Deployment:**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods,services -n geo-infer-iot

# Scale deployment
kubectl scale deployment geo-infer-iot-api --replicas=5

# Update deployment
kubectl set image deployment/geo-infer-iot-api geo-infer-iot=your-registry/geo-infer-iot:v2.0.0
```

**Kubernetes Resources:**
- **Deployment**: Scalable API service deployment
- **Service**: LoadBalancer service for external access
- **ConfigMap**: Application configuration
- **Secret**: Sensitive configuration data
- **PersistentVolumeClaim**: Data persistence
- **HorizontalPodAutoscaler**: Auto-scaling rules

### 3. Cloud Platforms

#### AWS Deployment

**Prerequisites:**
- AWS CLI configured
- ECR repository created
- ECS cluster or EKS cluster

**Deployment Steps:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t geo-infer-iot .
docker tag geo-infer-iot:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/geo-infer-iot:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/geo-infer-iot:latest

# Deploy to ECS (example)
aws ecs create-service --cluster your-cluster --service-name geo-infer-iot --task-definition geo-infer-iot --desired-count 3
```

#### Azure Deployment

**Prerequisites:**
- Azure CLI installed
- Azure Container Registry (ACR) created
- Azure Kubernetes Service (AKS) cluster

**Deployment Steps:**
```bash
# Login to ACR
az acr login --name your-registry

# Build and push image
docker build -t geo-infer-iot .
docker tag geo-infer-iot your-registry.azurecr.io/geo-infer-iot:latest
docker push your-registry.azurecr.io/geo-infer-iot:latest

# Deploy to AKS
kubectl apply -f k8s/ --namespace geo-infer-iot
```

#### Google Cloud Deployment

**Prerequisites:**
- gcloud CLI configured
- Google Container Registry (GCR) or Artifact Registry
- Google Kubernetes Engine (GKE) cluster

**Deployment Steps:**
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build and push image
docker build -t geo-infer-iot .
docker tag geo-infer-iot gcr.io/your-project/geo-infer-iot:latest
docker push gcr.io/your-project/geo-infer-iot:latest

# Deploy to GKE
kubectl apply -f k8s/ --namespace geo-infer-iot
```

## Configuration Management

### Environment Variables

Key configuration can be overridden using environment variables:

```bash
# Database connections
export POSTGRES_HOST=your-postgres-host
export INFLUXDB_HOST=your-influxdb-host
export REDIS_HOST=your-redis-host

# MQTT configuration
export MQTT_BROKER_HOST=your-mqtt-broker
export MQTT_BROKER_PORT=1883

# Security
export JWT_SECRET=your-jwt-secret

# Performance monitoring
export PROMETHEUS_ENABLED=true
export GRAFANA_ADMIN_PASSWORD=your-password
```

### Configuration Files

1. **Application Configuration**: `config/iot_config.yaml`
2. **Docker Configuration**: `docker-compose.yml`
3. **Kubernetes Configuration**: `k8s/` directory
4. **Monitoring Configuration**: `grafana/` and `prometheus/` directories

## Monitoring and Observability

### Grafana Dashboards

Pre-configured dashboards are available for:

- **System Performance**: CPU, memory, disk, network metrics
- **IoT Metrics**: Sensor count, measurement throughput, error rates
- **Spatial Analysis**: Coverage area, inference performance
- **Network Health**: Topology status, link quality

Access Grafana at http://localhost:3000 (admin/admin)

### Prometheus Metrics

Metrics are automatically collected for:

- **Application Metrics**: Request count, response time, error rates
- **System Metrics**: CPU, memory, disk usage
- **IoT Metrics**: Sensor registrations, measurements processed
- **Custom Metrics**: Spatial inference performance, data quality scores

### Logging

- **Application Logs**: `/app/logs/application.log`
- **Container Logs**: Available via `docker-compose logs`
- **Structured Logging**: JSON format for better parsing
- **Log Rotation**: Automatic daily rotation with retention

## Scaling and Performance

### Horizontal Scaling

**Docker Compose:**
```bash
# Scale API service
docker-compose up -d --scale geo-infer-iot-api=5
```

**Kubernetes:**
```bash
# Scale deployment
kubectl scale deployment geo-infer-iot-api --replicas=10

# Configure horizontal pod autoscaler
kubectl autoscale deployment geo-infer-iot-api --cpu-percent=70 --min=3 --max=20
```

### Performance Tuning

**Memory Optimization:**
- Use Redis for caching frequently accessed data
- Implement connection pooling for database connections
- Enable gzip compression for API responses

**CPU Optimization:**
- Use async/await patterns for I/O operations
- Implement proper connection pooling
- Use streaming for large data transfers

**Storage Optimization:**
- Use time-based partitioning for time series data
- Implement data retention policies
- Use appropriate indexing for query performance

## Security Considerations

### Network Security
- Services communicate over internal Docker network
- External access only through reverse proxy (nginx)
- MQTT broker authentication and authorization
- API authentication via JWT tokens

### Data Security
- Sensitive configuration stored in Docker secrets
- Database credentials rotated regularly
- Data encrypted at rest and in transit
- Audit logging for all data access

### Access Control
- Role-based access control (RBAC) for API endpoints
- Kubernetes RBAC for cluster access
- Database user permissions properly configured
- API rate limiting and DDoS protection

## Troubleshooting

### Common Issues

**1. Services not starting**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs geo-infer-iot-api

# Check resource usage
docker stats
```

**2. Database connection issues**
```bash
# Check database service status
docker-compose exec postgres pg_isready -U geo_infer

# Check InfluxDB health
curl http://localhost:8086/health
```

**3. Performance issues**
```bash
# Monitor system resources
docker-compose exec geo-infer-iot-api top

# Check application metrics
curl http://localhost:8000/metrics

# Run performance benchmarks
python -c "from geo_infer_iot.performance import run_performance_benchmark; run_performance_benchmark('ingestion_throughput')"
```

**4. Memory issues**
```bash
# Check memory usage
docker-compose exec geo-infer-iot-api python -c "import psutil; print(psutil.virtual_memory())"

# Monitor garbage collection
docker-compose exec geo-infer-iot-api python -c "import gc; gc.collect(); print('GC completed')"
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```yaml
# In config/iot_config.yaml
logging:
  level: DEBUG
  format: detailed
```

### Health Checks

All services include health check endpoints:

- **API Service**: `GET /health`
- **Database Services**: Built-in health checks
- **Message Broker**: Connection tests

## Backup and Recovery

### Database Backups

**InfluxDB:**
```bash
# Create backup
docker exec geo-infer-influxdb influx backup /backups

# Restore from backup
docker exec geo-infer-influxdb influx restore /backups
```

**PostgreSQL:**
```bash
# Create backup
docker exec geo-infer-postgres pg_dump -U geo_infer spatial_iot > backup.sql

# Restore from backup
docker exec -i geo-infer-postgres psql -U geo_infer spatial_iot < backup.sql
```

### Configuration Backup

```bash
# Backup configuration
cp config/iot_config.yaml config/iot_config.yaml.backup.$(date +%Y%m%d_%H%M%S)

# Restore configuration
cp config/iot_config.yaml.backup.LATEST config/iot_config.yaml
```

### Data Export

```python
# Export system state for backup
from geo_infer_iot import IoTSystem
system = IoTSystem()
system.export_system_state('backup/system_state.json')
```

## Production Checklist

Before deploying to production, ensure:

- [ ] All environment variables are properly configured
- [ ] SSL certificates are valid (not self-signed for production)
- [ ] Database credentials are secure and rotated
- [ ] Monitoring and alerting are configured
- [ ] Backup procedures are tested
- [ ] Performance benchmarks meet requirements
- [ ] Security scans pass
- [ ] Documentation is up to date
- [ ] Team is trained on deployment procedures

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review system logs for errors
   - Check disk space usage
   - Verify backup integrity
   - Update system packages

2. **Monthly**
   - Run full performance benchmarks
   - Review and update configurations
   - Test disaster recovery procedures
   - Security audit and updates

3. **Quarterly**
   - Major version updates
   - Capacity planning review
   - Performance optimization review
   - Documentation updates

### Getting Help

- **Documentation**: Check this deployment guide
- **Logs**: Review application and system logs
- **Metrics**: Check Grafana dashboards for anomalies
- **Community**: Join the GEO-INFER community for support

### Emergency Procedures

**Service Outage:**
1. Check system status: `docker-compose ps`
2. Review logs: `docker-compose logs geo-infer-iot-api`
3. Check resource usage: `docker stats`
4. Restart affected services: `docker-compose restart geo-infer-iot-api`

**Data Loss:**
1. Stop all services: `docker-compose down`
2. Restore from latest backup
3. Verify data integrity
4. Restart services with reduced load

**Security Incident:**
1. Isolate affected systems
2. Review audit logs
3. Change all credentials
4. Perform security scan
5. Report incident as required

## Advanced Configuration

### Custom Docker Images

Create optimized images for specific use cases:

```dockerfile
# Custom Dockerfile for edge deployment
FROM geo-infer-iot:latest

# Install edge-specific dependencies
RUN apt-get update && apt-get install -y \
    mosquitto-clients \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy edge-specific configuration
COPY edge-config.yaml /app/config/iot_config.yaml

# Set edge-specific environment
ENV DEPLOYMENT_MODE=edge \
    SENSOR_POLL_INTERVAL=30
```

### Multi-Region Deployment

For global deployments across multiple regions:

```yaml
# Regional configuration
regions:
  us-east-1:
    mqtt_broker: mqtt.us-east-1.example.com
    database: postgres.us-east-1.example.com
    storage: s3.us-east-1.amazonaws.com

  eu-west-1:
    mqtt_broker: mqtt.eu-west-1.example.com
    database: postgres.eu-west-1.example.com
    storage: s3.eu-west-1.amazonaws.com
```

### High Availability Setup

For production high availability:

```yaml
# HA configuration
high_availability:
  enabled: true
  replication_factor: 3
  failover_timeout: 30
  load_balancer_algorithm: round_robin

# Database clustering
database:
  cluster:
    enabled: true
    nodes: 3
    replication: synchronous
```

This deployment guide provides comprehensive coverage for deploying GEO-INFER-IOT in various environments, from development to production. For specific questions or issues, refer to the troubleshooting section or contact the development team.
