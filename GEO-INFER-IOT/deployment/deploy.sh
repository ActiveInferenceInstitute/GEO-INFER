#!/bin/bash

# GEO-INFER-IOT Deployment Script
# This script provides automated deployment options for different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_dependencies() {
    print_status "Checking deployment dependencies..."

    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Dependencies check passed"
}

# Function to setup configuration
setup_config() {
    print_status "Setting up configuration..."

    # Create config directory if it doesn't exist
    mkdir -p config

    # Copy example configuration if config file doesn't exist
    if [ ! -f "config/iot_config.yaml" ]; then
        cp config/example.yaml config/iot_config.yaml
        print_warning "Created default configuration from example. Please review and customize config/iot_config.yaml"
    fi

    # Create additional directories
    mkdir -p logs data mosquitto/{config,data,log} postgres/init influxdb/config grafana/{provisioning,dashboards} prometheus nginx/{ssl,logs}
}

# Function to generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    print_status "Generating SSL certificates for development..."

    if [ ! -f "nginx/ssl/server.crt" ] || [ ! -f "nginx/ssl/server.key" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/server.key -out nginx/ssl/server.crt \
            -days 365 -nodes -subj "/CN=geo-infer-iot.local"

        print_success "Generated self-signed SSL certificates"
    else
        print_status "SSL certificates already exist, skipping generation"
    fi
}

# Function to deploy with Docker Compose
deploy_docker_compose() {
    print_status "Deploying with Docker Compose..."

    # Setup configuration
    setup_config

    # Generate SSL certificates if needed
    generate_ssl_certificates

    # Build and start services
    print_status "Building and starting services..."
    docker-compose build --no-cache
    docker-compose up -d

    print_success "Deployment completed successfully!"
    print_status "Services are starting up. This may take a few minutes."

    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30

    # Check service health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "IoT API is healthy and ready!"
    else
        print_warning "IoT API may not be fully ready yet. Check logs with: docker-compose logs geo-infer-iot-api"
    fi

    print_status "Access points:"
    print_status "  - REST API: http://localhost:8000"
    print_status "  - WebSocket API: ws://localhost:8001"
    print_status "  - Grafana Dashboard: http://localhost:3000 (admin/admin)"
    print_status "  - MQTT Broker: mqtt://localhost:1883"

    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Function to deploy with Kubernetes (basic)
deploy_kubernetes() {
    print_status "Deploying with Kubernetes..."

    if ! command_exists kubectl; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi

    # Create namespace if it doesn't exist
    kubectl create namespace geo-infer-iot --dry-run=client -o yaml | kubectl apply -f -

    # Apply Kubernetes manifests
    print_status "Applying Kubernetes manifests..."

    # This would apply actual Kubernetes YAML files
    # For now, we'll create a simple deployment
    cat > k8s-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geo-infer-iot-api
  namespace: geo-infer-iot
  labels:
    app: geo-infer-iot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geo-infer-iot
  template:
    metadata:
      labels:
        app: geo-infer-iot
    spec:
      containers:
      - name: geo-infer-iot
        image: geo-infer-iot:latest
        ports:
        - containerPort: 8000
        - containerPort: 8001
        env:
        - name: CONFIG_PATH
          value: "/app/config/iot_config.yaml"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
      volumes:
      - name: config-volume
        configMap:
          name: iot-config
---
apiVersion: v1
kind: Service
metadata:
  name: geo-infer-iot-service
  namespace: geo-infer-iot
spec:
  selector:
    app: geo-infer-iot
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: websocket
    port: 8001
    targetPort: 8001
  type: LoadBalancer
EOF

    kubectl apply -f k8s-deployment.yaml

    print_success "Kubernetes deployment initiated"
    print_status "Check status with: kubectl get pods -n geo-infer-iot"
    print_status "View logs with: kubectl logs -f deployment/geo-infer-iot-api -n geo-infer-iot"
}

# Function to deploy to AWS (basic)
deploy_aws() {
    print_status "Deploying to AWS..."

    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi

    # Check if ECR repository exists
    REPO_NAME="geo-infer-iot"
    AWS_REGION=${AWS_REGION:-us-east-1}

    if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION >/dev/null 2>&1; then
        print_status "Creating ECR repository..."
        aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION
    fi

    # Build and push Docker image
    print_status "Building and pushing Docker image to ECR..."
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:latest"

    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Build and tag image
    docker build -t geo-infer-iot .
    docker tag geo-infer-iot:latest $IMAGE_URI

    # Push image
    docker push $IMAGE_URI

    print_success "Docker image pushed to ECR: $IMAGE_URI"

    # Create ECS cluster and service (simplified)
    print_status "ECS deployment setup would go here..."
    print_status "Image URI for ECS: $IMAGE_URI"
}

# Function to run tests before deployment
run_tests() {
    print_status "Running tests before deployment..."

    if [ -f "tests/run_tests.sh" ]; then
        bash tests/run_tests.sh
        print_success "Tests passed"
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Function to show deployment status
show_status() {
    print_status "Current deployment status:"

    if command_exists docker-compose; then
        echo "Docker Compose services:"
        docker-compose ps

        echo -e "\nContainer logs (last 20 lines):"
        docker-compose logs --tail=20
    fi

    if command_exists kubectl; then
        echo -e "\nKubernetes resources:"
        kubectl get pods,services,deployments -n geo-infer-iot --no-headers 2>/dev/null || echo "No Kubernetes resources found"
    fi
}

# Function to cleanup deployment
cleanup() {
    print_status "Cleaning up deployment..."

    if command_exists docker-compose; then
        docker-compose down -v --remove-orphans
        print_success "Docker Compose cleanup completed"
    fi

    if command_exists kubectl; then
        kubectl delete namespace geo-infer-iot --ignore-not-found=true
        print_success "Kubernetes cleanup completed"
    fi

    # Clean up generated files
    rm -f k8s-deployment.yaml
}

# Main deployment logic
main() {
    local DEPLOYMENT_TYPE=${1:-docker}

    print_status "Starting GEO-INFER-IOT deployment (type: $DEPLOYMENT_TYPE)"

    # Check dependencies
    check_dependencies

    case $DEPLOYMENT_TYPE in
        "docker")
            deploy_docker_compose
            ;;
        "kubernetes"|"k8s")
            deploy_kubernetes
            ;;
        "aws")
            deploy_aws
            ;;
        "test")
            run_tests
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            print_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            print_status "Available options: docker, kubernetes, aws, test, status, cleanup"
            exit 1
            ;;
    esac

    print_success "Deployment script completed"
}

# Run main function with all arguments
main "$@"
