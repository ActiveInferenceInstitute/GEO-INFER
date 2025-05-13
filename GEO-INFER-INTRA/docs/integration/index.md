# Integration Guide

This document provides information about integrating GEO-INFER-INTRA with other GEO-INFER modules and external systems.

## Contents

- [Integration Overview](overview.md) - Introduction to integration capabilities
- [GEO-INFER Module Integration](geo_infer_modules.md) - Integration with other GEO-INFER modules
- [External System Integration](external_systems.md) - Integration with external systems
- [API Integration](api_integration.md) - Integrating via APIs
- [Data Integration](data_integration.md) - Integrating data from various sources
- [Authentication Integration](auth_integration.md) - Integrating authentication systems
- [Webhooks](webhooks.md) - Event-based integration with webhooks
- [Message Queues](message_queues.md) - Integration via message queues
- [Integration Patterns](patterns.md) - Common integration patterns and best practices

## Integration Architecture

The following diagram shows the high-level integration architecture of GEO-INFER-INTRA:

```mermaid
graph TB
    subgraph "GEO-INFER-INTRA"
        API_GATEWAY[API Gateway]
        INTEGRATION_LAYER[Integration Layer]
        MESSAGE_BROKER[Message Broker]
        EVENT_BUS[Event Bus]
        DOC_SERVICE[Documentation Service]
        KB_SERVICE[Knowledge Base Service]
        ONTO_SERVICE[Ontology Service]
        WORKFLOW_SERVICE[Workflow Service]
    end
    
    subgraph "Other GEO-INFER Modules"
        SPACE[GEO-INFER-SPACE]
        TIME[GEO-INFER-TIME]
        API_MODULE[GEO-INFER-API]
        APP[GEO-INFER-APP]
        OPS[GEO-INFER-OPS]
    end
    
    subgraph "External Systems"
        GIS[GIS Systems]
        DATA_CATALOG[Data Catalogs]
        IDENTITY[Identity Providers]
        CMS[Content Management]
        ML_PLATFORMS[ML Platforms]
    end
    
    API_GATEWAY --> INTEGRATION_LAYER
    INTEGRATION_LAYER --> MESSAGE_BROKER
    INTEGRATION_LAYER --> EVENT_BUS
    
    MESSAGE_BROKER --> DOC_SERVICE
    MESSAGE_BROKER --> KB_SERVICE
    MESSAGE_BROKER --> ONTO_SERVICE
    MESSAGE_BROKER --> WORKFLOW_SERVICE
    
    API_GATEWAY <--> SPACE
    API_GATEWAY <--> TIME
    API_GATEWAY <--> API_MODULE
    
    INTEGRATION_LAYER <--> APP
    INTEGRATION_LAYER <--> OPS
    
    API_GATEWAY <--> GIS
    API_GATEWAY <--> DATA_CATALOG
    API_GATEWAY <--> IDENTITY
    API_GATEWAY <--> CMS
    API_GATEWAY <--> ML_PLATFORMS
    
    EVENT_BUS --> MESSAGE_BROKER
    
    classDef intra fill:#f9f,stroke:#333,stroke-width:1px
    classDef geo_infer fill:#bbf,stroke:#333,stroke-width:1px
    classDef external fill:#dfd,stroke:#333,stroke-width:1px
    
    class API_GATEWAY,INTEGRATION_LAYER,MESSAGE_BROKER,EVENT_BUS,DOC_SERVICE,KB_SERVICE,ONTO_SERVICE,WORKFLOW_SERVICE intra
    class SPACE,TIME,API_MODULE,APP,OPS geo_infer
    class GIS,DATA_CATALOG,IDENTITY,CMS,ML_PLATFORMS external
```

## Integration with GEO-INFER Modules

GEO-INFER-INTRA integrates with other GEO-INFER modules as follows:

```mermaid
graph TD
    subgraph "GEO-INFER-INTRA"
        INTRA_DOC[Documentation Service]
        INTRA_KB[Knowledge Base Service]
        INTRA_ONTO[Ontology Service]
        INTRA_WF[Workflow Service]
    end
    
    subgraph "GEO-INFER-SPACE"
        SPACE_DATA[Spatial Data Service]
        SPACE_PROC[Spatial Processing]
        SPACE_VIZ[Spatial Visualization]
    end
    
    subgraph "GEO-INFER-TIME"
        TIME_DATA[Temporal Data Service]
        TIME_PROC[Temporal Processing]
        TIME_VIZ[Temporal Visualization]
    end
    
    subgraph "GEO-INFER-API"
        API_REST[REST API]
        API_GRAPH[GraphQL API]
        API_DOC[API Documentation]
    end
    
    subgraph "GEO-INFER-APP"
        APP_UI[User Interface]
        APP_MOBILE[Mobile App]
        APP_COMP[UI Components]
    end
    
    subgraph "GEO-INFER-OPS"
        OPS_MONITOR[Monitoring]
        OPS_DEPLOY[Deployment]
        OPS_LOG[Logging]
    end
    
    %% INTRA to SPACE
    INTRA_DOC --> SPACE_DATA
    INTRA_ONTO --> SPACE_DATA
    INTRA_KB --> SPACE_PROC
    INTRA_WF --> SPACE_PROC
    
    %% INTRA to TIME
    INTRA_DOC --> TIME_DATA
    INTRA_ONTO --> TIME_DATA
    INTRA_KB --> TIME_PROC
    INTRA_WF --> TIME_PROC
    
    %% INTRA to API
    INTRA_DOC --> API_DOC
    INTRA_KB --> API_REST
    INTRA_ONTO --> API_GRAPH
    INTRA_WF --> API_REST
    
    %% INTRA to APP
    INTRA_DOC --> APP_UI
    INTRA_KB --> APP_UI
    INTRA_KB --> APP_MOBILE
    INTRA_ONTO --> APP_COMP
    INTRA_WF --> APP_UI
    
    %% INTRA to OPS
    INTRA_DOC --> OPS_DEPLOY
    INTRA_KB --> OPS_MONITOR
    INTRA_WF --> OPS_LOG
    OPS_MONITOR --> INTRA_WF
    
    %% SPACE to INTRA
    SPACE_DATA --> INTRA_DOC
    SPACE_DATA --> INTRA_ONTO
    SPACE_PROC --> INTRA_KB
    
    %% TIME to INTRA
    TIME_DATA --> INTRA_DOC
    TIME_DATA --> INTRA_ONTO
    TIME_PROC --> INTRA_KB
    
    classDef intra fill:#f9f,stroke:#333,stroke-width:1px
    classDef space fill:#bbf,stroke:#333,stroke-width:1px
    classDef time fill:#dfd,stroke:#333,stroke-width:1px
    classDef api fill:#ffd,stroke:#333,stroke-width:1px
    classDef app fill:#fdb,stroke:#333,stroke-width:1px
    classDef ops fill:#ddf,stroke:#333,stroke-width:1px
    
    class INTRA_DOC,INTRA_KB,INTRA_ONTO,INTRA_WF intra
    class SPACE_DATA,SPACE_PROC,SPACE_VIZ space
    class TIME_DATA,TIME_PROC,TIME_VIZ time
    class API_REST,API_GRAPH,API_DOC api
    class APP_UI,APP_MOBILE,APP_COMP app
    class OPS_MONITOR,OPS_DEPLOY,OPS_LOG ops
```

## Integration Mechanisms

GEO-INFER-INTRA provides several mechanisms for integration:

### API-Based Integration

The REST and GraphQL APIs allow for programmatic integration:

```mermaid
sequenceDiagram
    participant Client
    participant APIGateway as API Gateway
    participant Auth as Authentication
    participant Service as INTRA Service
    participant DB as Database
    
    Client->>APIGateway: API Request
    APIGateway->>Auth: Authenticate
    Auth->>APIGateway: Authentication Result
    APIGateway->>Service: Forward Request
    Service->>DB: Query Data
    DB->>Service: Return Data
    Service->>APIGateway: Service Response
    APIGateway->>Client: API Response
```

### Event-Based Integration

The event bus enables asynchronous, event-driven integration:

```mermaid
graph LR
    subgraph "Publisher"
        P_SERVICE[Service]
        P_EVENT[Event Publisher]
    end
    
    subgraph "Event Bus"
        TOPICS[Topics]
        QUEUE[Message Queue]
    end
    
    subgraph "Subscribers"
        S1_EVENT[Event Subscriber]
        S1_SERVICE[Service 1]
        
        S2_EVENT[Event Subscriber]
        S2_SERVICE[Service 2]
        
        S3_EVENT[Event Subscriber]
        S3_SERVICE[Service 3]
    end
    
    P_SERVICE --> P_EVENT
    P_EVENT --> TOPICS
    TOPICS --> QUEUE
    
    QUEUE --> S1_EVENT
    QUEUE --> S2_EVENT
    QUEUE --> S3_EVENT
    
    S1_EVENT --> S1_SERVICE
    S2_EVENT --> S2_SERVICE
    S3_EVENT --> S3_SERVICE
    
    classDef publisher fill:#bbf,stroke:#333,stroke-width:1px
    classDef bus fill:#f9f,stroke:#333,stroke-width:1px
    classDef subscriber fill:#dfd,stroke:#333,stroke-width:1px
    
    class P_SERVICE,P_EVENT publisher
    class TOPICS,QUEUE bus
    class S1_EVENT,S1_SERVICE,S2_EVENT,S2_SERVICE,S3_EVENT,S3_SERVICE subscriber
```

### Webhook Integration

Webhooks enable external systems to receive real-time notifications:

```mermaid
sequenceDiagram
    participant INTRA as GEO-INFER-INTRA
    participant EventManager as Event Manager
    participant WebhookManager as Webhook Manager
    participant ExternalSystem as External System
    
    Note over INTRA: Event occurs
    INTRA->>EventManager: Publish Event
    EventManager->>WebhookManager: Process Event
    WebhookManager->>WebhookManager: Find registered webhooks
    WebhookManager->>ExternalSystem: HTTP POST with event data
    ExternalSystem->>WebhookManager: HTTP 200 OK
    WebhookManager->>EventManager: Delivery status
```

### File-Based Integration

Integration through file exchange:

```mermaid
graph TD
    subgraph "GEO-INFER-INTRA"
        FILE_EXPORT[File Export]
        FILE_IMPORT[File Import]
        VALIDATOR[Data Validator]
    end
    
    subgraph "Storage Systems"
        LOCAL[Local Storage]
        S3[S3 Compatible]
        FTP[FTP/SFTP]
        CLOUD[Cloud Storage]
    end
    
    subgraph "External Tools"
        GIS_TOOL[GIS Software]
        SPREADSHEET[Spreadsheet]
        OTHER_TOOL[Other Tools]
    end
    
    FILE_EXPORT --> LOCAL
    FILE_EXPORT --> S3
    FILE_EXPORT --> FTP
    FILE_EXPORT --> CLOUD
    
    LOCAL --> FILE_IMPORT
    S3 --> FILE_IMPORT
    FTP --> FILE_IMPORT
    CLOUD --> FILE_IMPORT
    
    FILE_IMPORT --> VALIDATOR
    
    LOCAL <--> GIS_TOOL
    LOCAL <--> SPREADSHEET
    LOCAL <--> OTHER_TOOL
    
    classDef intra fill:#f9f,stroke:#333,stroke-width:1px
    classDef storage fill:#bbf,stroke:#333,stroke-width:1px
    classDef tools fill:#dfd,stroke:#333,stroke-width:1px
    
    class FILE_EXPORT,FILE_IMPORT,VALIDATOR intra
    class LOCAL,S3,FTP,CLOUD storage
    class GIS_TOOL,SPREADSHEET,OTHER_TOOL tools
```

## Authentication Integration

Integration with authentication systems:

```mermaid
graph TD
    subgraph "GEO-INFER-INTRA"
        AUTH_GATEWAY[Auth Gateway]
        TOKEN_VALIDATOR[Token Validator]
        PERMISSIONS[Permission Manager]
    end
    
    subgraph "Identity Providers"
        OAUTH[OAuth Provider]
        SAML[SAML Provider]
        LDAP[LDAP Directory]
        LOCAL_AUTH[Local Auth]
    end
    
    OAUTH --> AUTH_GATEWAY
    SAML --> AUTH_GATEWAY
    LDAP --> AUTH_GATEWAY
    LOCAL_AUTH --> AUTH_GATEWAY
    
    AUTH_GATEWAY --> TOKEN_VALIDATOR
    TOKEN_VALIDATOR --> PERMISSIONS
    
    classDef intra fill:#f9f,stroke:#333,stroke-width:1px
    classDef idp fill:#bbf,stroke:#333,stroke-width:1px
    
    class AUTH_GATEWAY,TOKEN_VALIDATOR,PERMISSIONS intra
    class OAUTH,SAML,LDAP,LOCAL_AUTH idp
```

## Data Integration Patterns

Common data integration patterns for GEO-INFER-INTRA:

### ETL (Extract, Transform, Load)

```mermaid
graph LR
    subgraph "Extract"
        DATA_SOURCE[Data Source]
        CONNECTOR[Connector]
        EXTRACT[Extraction Logic]
    end
    
    subgraph "Transform"
        CLEANING[Data Cleaning]
        VALIDATION[Data Validation]
        TRANSFORMATION[Transformation Logic]
        ENRICHMENT[Data Enrichment]
    end
    
    subgraph "Load"
        LOADER[Data Loader]
        TARGET[Target Store]
    end
    
    DATA_SOURCE --> CONNECTOR
    CONNECTOR --> EXTRACT
    EXTRACT --> CLEANING
    CLEANING --> VALIDATION
    VALIDATION --> TRANSFORMATION
    TRANSFORMATION --> ENRICHMENT
    ENRICHMENT --> LOADER
    LOADER --> TARGET
    
    classDef extract fill:#bbf,stroke:#333,stroke-width:1px
    classDef transform fill:#f9f,stroke:#333,stroke-width:1px
    classDef load fill:#dfd,stroke:#333,stroke-width:1px
    
    class DATA_SOURCE,CONNECTOR,EXTRACT extract
    class CLEANING,VALIDATION,TRANSFORMATION,ENRICHMENT transform
    class LOADER,TARGET load
```

### Event Sourcing

```mermaid
graph LR
    subgraph "Event Sources"
        SOURCE1[Source 1]
        SOURCE2[Source 2]
        SOURCE3[Source 3]
    end
    
    subgraph "Event Processing"
        EVENT_STORE[Event Store]
        EVENT_PROCESSOR[Event Processor]
    end
    
    subgraph "Materialized Views"
        VIEW1[View 1]
        VIEW2[View 2]
        VIEW3[View 3]
    end
    
    SOURCE1 --> EVENT_STORE
    SOURCE2 --> EVENT_STORE
    SOURCE3 --> EVENT_STORE
    
    EVENT_STORE --> EVENT_PROCESSOR
    
    EVENT_PROCESSOR --> VIEW1
    EVENT_PROCESSOR --> VIEW2
    EVENT_PROCESSOR --> VIEW3
    
    classDef source fill:#bbf,stroke:#333,stroke-width:1px
    classDef processing fill:#f9f,stroke:#333,stroke-width:1px
    classDef view fill:#dfd,stroke:#333,stroke-width:1px
    
    class SOURCE1,SOURCE2,SOURCE3 source
    class EVENT_STORE,EVENT_PROCESSOR processing
    class VIEW1,VIEW2,VIEW3 view
```

## Integration Examples

### Integrating GEO-INFER-INTRA with QGIS

```python
from qgis.core import QgsVectorLayer, QgsProject
import requests

# GEO-INFER-INTRA API endpoint
api_endpoint = "https://api.geo-infer.org/intra/v1"
auth_token = "your_api_token"

# Get workflow results from GEO-INFER-INTRA
headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

response = requests.get(
    f"{api_endpoint}/workflows/results/123",
    headers=headers
)

if response.status_code == 200:
    # Save the GeoJSON result to a temporary file
    result_data = response.json()
    with open("/tmp/result.geojson", "w") as f:
        f.write(json.dumps(result_data))
    
    # Load the GeoJSON into QGIS
    layer = QgsVectorLayer("/tmp/result.geojson", "Workflow Result", "ogr")
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)
    else:
        print("Failed to load the layer")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Integrating GEO-INFER-INTRA with Python Data Science Tools

```python
import pandas as pd
import geopandas as gpd
import requests
from geo_infer.client import IntraClient

# Initialize the GEO-INFER-INTRA client
client = IntraClient(api_url="https://api.geo-infer.org/intra/v1", api_key="your_api_key")

# Fetch a knowledge base article on spatial interpolation
article = client.knowledge_base.get_article("spatial_interpolation_kriging")
print(f"Article: {article.title}")
print(f"Content: {article.content[:100]}...")

# Get ontology concepts related to kriging
concepts = client.ontology.search("kriging")
for concept in concepts:
    print(f"Concept: {concept.name} - {concept.definition}")

# Load spatial data from GEO-INFER-SPACE through GEO-INFER-INTRA
dataset = client.space.get_dataset("rainfall_measurements")
gdf = gpd.GeoDataFrame.from_features(dataset.features)

# Perform analysis using Python data science tools
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Prepare data
X = np.column_stack([gdf.geometry.x, gdf.geometry.y])
y = gdf["rainfall"]

# Train a model
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Make predictions on a grid
x_min, y_min, x_max, y_max = gdf.total_bounds
x_grid = np.linspace(x_min, x_max, 100)
y_grid = np.linspace(y_min, y_max, 100)
XX, YY = np.meshgrid(x_grid, y_grid)
grid_points = np.column_stack([XX.ravel(), YY.ravel()])
predictions = model.predict(grid_points)

# Create a result geodataframe
result_gdf = gpd.GeoDataFrame(
    {"predicted_rainfall": predictions},
    geometry=gpd.points_from_xy(grid_points[:, 0], grid_points[:, 1]),
    crs=gdf.crs
)

# Export the result
result_gdf.to_file("predicted_rainfall.geojson", driver="GeoJSON")

# Upload the result back to GEO-INFER-INTRA
with open("predicted_rainfall.geojson", "rb") as f:
    client.data.upload_dataset(
        name="Predicted Rainfall",
        description="Random Forest prediction of rainfall",
        data=f,
        format="geojson"
    )
```

## Integration Best Practices

- **Use standard protocols** - Prefer standard protocols like HTTP, MQTT, AMQP
- **Implement proper error handling** - Handle and report integration errors
- **Secure all integration points** - Use authentication and encryption
- **Design for resilience** - Implement retry logic and circuit breakers
- **Monitor integration health** - Track integration performance and errors
- **Version your APIs** - Use proper versioning for API endpoints
- **Document integration points** - Maintain clear documentation
- **Validate data** - Validate data at integration boundaries
- **Use message queues** - Decouple systems with message queues for reliability
- **Follow the principle of least privilege** - Restrict access to necessary resources only

## Related Resources

- [API Documentation](../api/index.md)
- [Authentication](../security/authentication.md)
- [Data Exchange Formats](../data/formats.md)
- [Integration Examples](examples/index.md)
- [Troubleshooting Guide](../troubleshooting/integration_issues.md) 