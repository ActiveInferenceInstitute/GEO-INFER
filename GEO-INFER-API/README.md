# GEO-INFER-API

**Standardized Interfaces for Geospatial Interoperability**

## Overview

GEO-INFER-API is the **central nervous system for communication and interoperability** within the GEO-INFER framework and with external systems. This module is responsible for designing, developing, and managing standardized, secure, and efficient Application Programming Interfaces (APIs). It serves as a unified gateway, abstracting the complexities of individual modules and providing consistent access to their functionalities and data. By adhering to widely adopted geospatial and web API standards, GEO-INFER-API ensures that different components can communicate effectively, and that external developers and applications can easily integrate with the GEO-INFER ecosystem.

## Core Objectives

-   **Interoperability:** Enable seamless data exchange and functional interaction between all GEO-INFER modules and with external systems using common standards.
-   **Standardization:** Implement and promote the use of OGC (Open Geospatial Consortium) and other relevant API standards (e.g., REST, GraphQL, STAC).
-   **Abstraction:** Provide a simplified and consistent interface to complex underlying functionalities of various GEO-INFER modules.
-   **Security:** Ensure all API interactions are secure through robust authentication, authorization, and data protection mechanisms.
-   **Discoverability & Usability:** Make APIs easily discoverable, well-documented, and straightforward for developers to use, providing client SDKs where appropriate.
-   **Scalability & Performance:** Design APIs that can handle a high volume of requests efficiently and scale with the growth of the GEO-INFER framework.

## Key Features

-   **OGC-Compliant API Development:** Implementation of key OGC API standards (e.g., OGC API Features, Processes, Maps, Tiles, EDR - Environmental Data Retrieval) to ensure interoperability with standard GIS tools and platforms.
-   **Versatile API Paradigms:** Support for multiple API styles including RESTful services (using frameworks like FastAPI) for resource-oriented interactions and GraphQL for flexible and efficient data querying, catering to different client needs.
-   **Webhook & Real-time Event Integration:** Mechanisms for real-time communication, allowing modules or external services to subscribe to events and receive updates via webhooks or WebSocket connections (e.g., for data updates, completed analyses).
-   **Comprehensive API Documentation & SDKs:** Auto-generated, interactive API documentation (e.g., Swagger/OpenAPI, ReDoc) and the provision of client Software Development Kits (SDKs) in popular languages (Python, JavaScript, R) to simplify integration.
-   **API Gateway Functionality:** Acts as a central entry point for API requests, handling routing, rate limiting, request/response transformation, and potentially aggregating services from multiple backend modules.
-   **Security & Access Control:** Robust implementation of authentication (e.g., API keys, OAuth 2.0, JWT) and authorization (e.g., role-based access control - RBAC) mechanisms, integrated with GEO-INFER-SEC.
-   **Geospatial Data Streaming:** Capabilities for streaming large geospatial datasets or real-time sensor data efficiently over APIs.

## Data Flow

### Inputs
- **Client Requests**:
  - HTTP/HTTPS requests from web applications, mobile apps, GIS tools
  - GraphQL queries for flexible data retrieval
  - WebSocket connections for real-time data streams
  - SDK calls from Python, JavaScript, R, and CLI applications
  - Webhook subscriptions for event notifications

- **Backend Module Services**:
  - Data services from GEO-INFER-DATA (spatial datasets, metadata)
  - Analysis services from GEO-INFER-SPACE, TIME, AI modules
  - Processing workflows from GEO-INFER-ACT, SIM, AGENT
  - Configuration and monitoring from GEO-INFER-OPS
  - Security policies from GEO-INFER-SEC

- **Configuration Requirements**:
  - `api_config.yaml`: Server settings, rate limits, authentication
  - `endpoints.yaml`: API route definitions and permissions
  - OpenAPI specifications for automated documentation generation
  - Authentication provider configurations (OAuth, JWT)

- **Dependencies**:
  - **Required**: All GEO-INFER modules (for service exposure), GEO-INFER-SEC (authentication)
  - **Optional**: GEO-INFER-OPS (monitoring), GEO-INFER-INTRA (documentation)

### Processes
- **Request Processing & Routing**:
  - Authentication and authorization validation
  - Rate limiting and request throttling
  - Input validation and sanitization
  - Request routing to appropriate backend services
  - Load balancing across service instances

- **Data Transformation & Serialization**:
  - Format conversion (GeoJSON, WKT, raster formats)
  - Response pagination and streaming for large datasets
  - Coordinate reference system transformations
  - Error handling and standardized error responses

- **Standards Compliance & Interoperability**:
  - OGC API standards implementation (Features, Processes, Maps, Tiles)
  - STAC (SpatioTemporal Asset Catalog) compliance
  - OpenAPI specification generation and validation
  - Cross-origin resource sharing (CORS) handling

### Outputs
- **RESTful API Services**:
  - OGC-compliant endpoints for geospatial data access
  - CRUD operations for spatial features and datasets
  - Asynchronous processing endpoints for long-running analyses
  - File upload/download endpoints for data exchange

- **GraphQL Services**:
  - Flexible query interface for complex data relationships
  - Real-time subscriptions for live data updates
  - Type-safe schema with introspection capabilities
  - Efficient data fetching with custom resolvers

- **Documentation & Developer Tools**:
  - Interactive API documentation (Swagger UI, ReDoc)
  - Auto-generated client SDKs for multiple languages
  - Code examples and integration tutorials
  - API testing tools and validation utilities

- **Integration Points**:
  - Service endpoints for all GEO-INFER modules
  - Real-time data streams for GEO-INFER-APP dashboards
  - Webhook integrations for external system notifications
  - API gateway functionality for microservices orchestration

## API Gateway Architecture (Conceptual)

```mermaid
graph LR
    subgraph External_Clients as "External Clients & Users"
        WEB_APP[Web Applications]
        MOBILE_APP[Mobile Applications]
        GIS_TOOLS[Desktop GIS Tools]
        PYTHON_SDK[Python SDK Users]
        JS_SDK[JavaScript SDK Users]
        CLI[Command Line Interface Users]
    end

    subgraph API_Gateway as "GEO-INFER-API Gateway"
        direction LR
        ROUTER[API Router / Load Balancer]
        AUTH_N_Z[Authentication & Authorization Service]
        RATE_LIMIT[Rate Limiting & Throttling]
        DOCS_UI[API Documentation UI (Swagger/ReDoc)]
        TRANSFORM[Request/Response Transformation]
    end

    subgraph Backend_Modules as "GEO-INFER Backend Modules"
        direction TB
        DATA_API[GEO-INFER-DATA API]
        SPACE_API[GEO-INFER-SPACE API]
        TIME_API[GEO-INFER-TIME API]
        AI_API[GEO-INFER-AI API]
        ACT_API[GEO-INFER-ACT API]
        SIM_API[GEO-INFER-SIM API]
        AGENT_API[GEO-INFER-AGENT API]
        APP_SERVICES[GEO-INFER-APP Services]
        OTHER_MOD_APIs[Other Module APIs...]
    end
    
    %% Connections from Clients to Gateway
    WEB_APP --> ROUTER
    MOBILE_APP --> ROUTER
    GIS_TOOLS --> ROUTER
    PYTHON_SDK --> ROUTER
    JS_SDK --> ROUTER
    CLI --> ROUTER

    %% Gateway Internal Flow
    ROUTER --> AUTH_N_Z
    AUTH_N_Z -- Authenticated/Authorized --> RATE_LIMIT
    RATE_LIMIT -- Allowed --> TRANSFORM
    ROUTER -- Serves --> DOCS_UI

    %% Gateway to Backend Modules
    TRANSFORM -- Routes to --> DATA_API
    TRANSFORM -- Routes to --> SPACE_API
    TRANSFORM -- Routes to --> TIME_API
    TRANSFORM -- Routes to --> AI_API
    TRANSFORM -- Routes to --> ACT_API
    TRANSFORM -- Routes to --> SIM_API
    TRANSFORM -- Routes to --> AGENT_API
    TRANSFORM -- Routes to --> APP_SERVICES
    TRANSFORM -- Routes to --> OTHER_MOD_APIs

    classDef apiGateway fill:#e6faff,stroke:#00b8d4,stroke-width:2px;
    class API_Gateway apiGateway;
```

## Directory Structure
```
GEO-INFER-API/
├── config/              # Configuration for API server, rate limits, security providers
├── docs/                # Source for OpenAPI/Swagger specifications, usage guides for APIs
├── examples/            # Client-side example scripts for using the APIs (Python, JS, curl)
├── src/                 # Source code
│   └── geo_infer_api/   # Main Python package
│       ├── core/        # Core API logic, request handling, security implementations
│       ├── endpoints/   # Definitions of specific API routes and handlers (REST, GraphQL resolvers)
│       ├── models/      # Pydantic models for API request/response schemas
│       ├── standards/   # Implementations for OGC API standards, STAC, etc.
│       └── utils/       # Utility functions, error handlers, response formatters
└── tests/               # Unit and integration tests for API endpoints
```

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites Check
```bash
# Verify Python version
python --version  # Should be 3.9+

# Check web framework dependencies
python -c "import fastapi, uvicorn; print('✅ Web framework available')"

# Check required GEO-INFER modules
pip list | grep geo-infer
```

### 2. Installation
```bash
# Install GEO-INFER-API and dependencies
pip install -e ./GEO-INFER-API

# Install additional API dependencies
pip install fastapi uvicorn strawberry-graphql

# Verify installation
python -c "import geo_infer_api; print('✅ API installation successful')"
```

### 3. Basic Configuration
```bash
# Copy example configuration
cp config/example.yaml config/local.yaml

# Set environment variables
export GEO_INFER_API_HOST=localhost
export GEO_INFER_API_PORT=8000
export GEO_INFER_JWT_SECRET=your-secret-key

# Edit configuration with your settings
nano config/local.yaml
```

### 4. Start the API Server
```bash
# Start development server with auto-reload
uvicorn geo_infer_api.app:main_app --host 0.0.0.0 --port 8000 --reload

# Check server status
curl http://localhost:8000/health
```

### 5. Test API Endpoints
```bash
# Test basic endpoints
curl http://localhost:8000/api/v1/info

# Test OGC API compliance
curl http://localhost:8000/ogc/collections

# Test GraphQL endpoint
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ apiInfo { version } }"}'
```

### 6. Explore API Documentation
```bash
# Open interactive documentation
open http://localhost:8000/docs          # Swagger UI
open http://localhost:8000/redoc         # ReDoc
open http://localhost:8000/graphql       # GraphQL Playground

# Validate API endpoints
python -m geo_infer_api.cli validate-endpoints
```

### 7. Test with Python SDK
```python
# Test API with Python client
from geo_infer_api.client import GeoInferClient

# Initialize client
client = GeoInferClient(base_url="http://localhost:8000")

# Test basic functionality
info = client.get_api_info()
print(f"✅ API Info: {info['name']} v{info['version']}")

# Test spatial data access
collections = client.get_collections()
print(f"✅ Available collections: {len(collections)}")
```

### 8. Next Steps
- 📖 Explore [API documentation](http://localhost:8000/docs) 
- 🔧 Review [client SDKs](./examples/) for different languages
- 🛠️ See [integration examples](./examples/) for connecting with other modules
- 📋 Check [OGC compliance](./docs/ogc_standards.md) for standards implementation

## Getting Started (Detailed)

### Prerequisites
- Python 3.9+
- FastAPI, Uvicorn (or similar ASGI server)
- GraphQL libraries (e.g., Strawberry, Ariadne)
- Relevant database connectors if API directly queries data stores.

### Installation
```bash
# Clone the GEO-INFER repository if you haven't already
# git clone https://github.com/activeinference/GEO-INFER.git
# cd GEO-INFER/GEO-INFER-API

pip install -e .
# or poetry install if pyproject.toml is configured
```

### Configuration
API server settings (host, port), security parameters (e.g., JWT secrets, OAuth provider details), database connections, and upstream service endpoints are configured in `config/` files or environment variables.
```bash
# cp config/example_api_server.yaml config/local_api_server.yaml
# # Edit local_api_server.yaml
```

### Running Tests
```bash
pytest tests/
```

### Starting the API server
(Typically using an ASGI server like Uvicorn for FastAPI applications)
```bash
# Example using Uvicorn for a FastAPI app defined in geo_infer_api.app:main_app
uvicorn geo_infer_api.app:main_app --host 0.0.0.0 --port 8000 --reload
```

## API Standards Adherence

GEO-INFER-API strives to implement and promote the use of key industry and community standards:

-   **OGC API Suite:**
    -   `OGC API - Features`: For accessing vector feature data.
    -   `OGC API - Processes`: For executing geospatial processing tasks asynchronously.
    -   `OGC API - Maps` & `OGC API - Tiles`: For serving pre-rendered maps and map tiles.
    -   `OGC API - Environmental Data Retrieval (EDR)`: For accessing environmental data using spatio-temporal queries.
    -   `OGC SensorThings API`: For accessing observations and metadata from IoT sensors.
-   **SpatioTemporal Asset Catalog (STAC) API:** For discovering and accessing collections of Earth observation data and other spatio-temporal assets.
-   **GeoJSON & GeoJSON-LD:** For representing geospatial features and linked data.
-   **OpenAPI Specification (OAS v3+):** For designing, documenting, and testing RESTful APIs.
-   **GraphQL Best Practices:** For schema design, query optimization, and pagination.

## Authentication & Authorization

The module provides a comprehensive security layer for all API interactions:

-   **API Key Authentication:** Simple token-based authentication for basic access.
-   **OAuth 2.0 / OpenID Connect (OIDC):** Robust, standard-based authorization framework for delegated access and integration with identity providers.
-   **JSON Web Tokens (JWT):** Used for securely transmitting information between parties as a JSON object, commonly for stateless authentication.
-   **Role-Based Access Control (RBAC):** Defining roles and permissions to control access to specific API endpoints or data resources based on user identity and group membership.
-   **Rate Limiting & Throttling:** Protecting backend services from abuse and ensuring fair usage by limiting the number of requests a client can make in a given time period.
-   **Input Validation:** Rigorous validation of all incoming API request parameters and payloads to prevent injection attacks and ensure data integrity.
-   **HTTPS Enforcement:** All API traffic must be over HTTPS.

## API Documentation

Interactive and comprehensive API documentation is a priority:

-   **OpenAPI/Swagger UI:** Automatically generated interactive UI for RESTful APIs, typically available at a `/docs` or `/swagger` endpoint. Allows users to explore endpoints, view schemas, and test requests directly in the browser.
-   **ReDoc Interface:** Alternative, more static documentation format generated from OpenAPI specs, often available at a `/redoc` endpoint. Provides a clean, three-panel view of the API.
-   **GraphQL Playground/Explorer:** Interactive environments like GraphQL Playground or GraphiQL for exploring GraphQL schemas, writing queries, and viewing results, usually at `/graphql`.
-   **Dedicated Documentation Portal:** For more detailed guides, tutorials, authentication instructions, and SDK usage examples, often integrated with the main GEO-INFER-INTRA documentation system.

## Integration with Other Modules

GEO-INFER-API acts as the primary interface layer:

-   **GEO-INFER-OPS (Operations):** OPS may monitor API health, performance, and usage statistics. OPS might also manage the deployment and scaling of API gateway instances.
-   **GEO-INFER-DATA (Data Management):** API exposes data managed by DATA through standardized interfaces (e.g., OGC API Features for vector data, STAC for imagery).
-   **GEO-INFER-SEC (Security):** API implements the authentication and authorization policies defined and managed by SEC. It forwards security events to SEC for auditing.
-   **GEO-INFER-APP (Applications):** User-facing applications built with APP consume services exposed by API to fetch data, trigger analyses, and interact with backend functionalities.
-   **All Analytical Modules (SPACE, TIME, AI, ACT, SIM, AGENT, etc.):** The functionalities of these modules (e.g., running a spatial analysis, training a model, querying an agent's state) are often exposed via API, allowing them to be invoked programmatically or integrated into larger workflows.
-   **GEO-INFER-INTRA (Knowledge Management):** API specifications and documentation generated by API are managed and disseminated by INTRA.

## Client Libraries & SDKs

To facilitate easier integration, GEO-INFER-API aims to provide or support the development of:

-   **Python SDK:** A comprehensive Python library for interacting with all GEO-INFER APIs, simplifying request formation, authentication, and response parsing.
-   **JavaScript/TypeScript SDK:** For web frontend development and Node.js applications.
-   **R Package:** For data scientists and analysts working within the R environment.
-   **Command-Line Interface (CLI) Tools:** For scripting, automation, and quick interaction with API endpoints from the terminal.
-   **Cookbooks & Examples:** Extensive collections of code snippets and example applications demonstrating how to use the SDKs and APIs for common tasks.

## Contributing

Contributions are welcome in many areas:
-   Implementing new OGC or other standard API endpoints.
-   Improving API security features.
-   Developing or enhancing client SDKs.
-   Writing more comprehensive API documentation and examples.
-   Optimizing API performance and scalability.
-   Adding support for new authentication/authorization schemes.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and any specific guidelines for API development in `GEO-INFER-API/docs/CONTRIBUTING_API.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 