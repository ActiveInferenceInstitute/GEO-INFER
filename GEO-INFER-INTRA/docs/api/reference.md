# API Reference

> **Technical Reference**: Complete API documentation for GEO-INFER-INTRA
> 
> This reference provides complete documentation for all GEO-INFER-INTRA APIs, including REST endpoints, GraphQL schemas, and client libraries.

## 🚀 Quick Start

### Base URL

```bash
# Production
https://api.geo-infer.org/v1

# Staging
https://staging-api.geo-infer.org/v1

# Development
http://localhost:8080/v1
```

### Authentication

```python
import requests

# API Key authentication
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

# OAuth 2.0 authentication
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
}
```

## 📚 Core APIs

### Knowledge Base API

#### Get Knowledge Base Articles

```http
GET /knowledge/articles
```

**Parameters:**
- `query` (string, optional): Search query
- `category` (string, optional): Article category
- `tags` (array, optional): Filter by tags
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)

**Response:**
```json
{
  "status": "success",
  "data": {
    "articles": [
      {
        "id": "kb_001",
        "title": "Spatial Analysis Best Practices",
        "content": "Complete guide to spatial analysis...",
        "category": "spatial_analysis",
        "tags": ["spatial", "analysis", "best_practices"],
        "created_at": "2023-06-15T10:30:00Z",
        "updated_at": "2023-06-15T10:30:00Z",
        "author": "geo-infer-team",
        "views": 1250,
        "rating": 4.8
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

#### Get Article by ID

```http
GET /knowledge/articles/{article_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "kb_001",
    "title": "Spatial Analysis Best Practices",
    "content": "Complete guide to spatial analysis...",
    "category": "spatial_analysis",
    "tags": ["spatial", "analysis", "best_practices"],
    "created_at": "2023-06-15T10:30:00Z",
    "updated_at": "2023-06-15T10:30:00Z",
    "author": "geo-infer-team",
    "views": 1250,
    "rating": 4.8,
    "related_articles": [
      {
        "id": "kb_002",
        "title": "Advanced Spatial Techniques",
        "url": "/knowledge/articles/kb_002"
      }
    ]
  }
}
```

#### Create Article

```http
POST /knowledge/articles
```

**Request Body:**
```json
{
  "title": "New Article Title",
  "content": "Article content in markdown format...",
  "category": "tutorial",
  "tags": ["tutorial", "beginner"],
  "author": "user_123"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "kb_003",
    "title": "New Article Title",
    "content": "Article content in markdown format...",
    "category": "tutorial",
    "tags": ["tutorial", "beginner"],
    "created_at": "2023-06-15T10:30:00Z",
    "updated_at": "2023-06-15T10:30:00Z",
    "author": "user_123",
    "views": 0,
    "rating": null
  }
}
```

### Ontology API

#### Get Ontology Concepts

```http
GET /ontology/concepts
```

**Parameters:**
- `domain` (string, optional): Domain filter
- `type` (string, optional): Concept type
- `search` (string, optional): Search query

**Response:**
```json
{
  "status": "success",
  "data": {
    "concepts": [
      {
        "id": "concept_001",
        "name": "SpatialFeature",
        "type": "class",
        "domain": "geospatial",
        "description": "A spatial feature in geographic space",
        "properties": [
          {
            "name": "geometry",
            "type": "Geometry",
            "description": "The geometric representation"
          },
          {
            "name": "attributes",
            "type": "AttributeSet",
            "description": "Feature attributes"
          }
        ],
        "relationships": [
          {
            "type": "subClassOf",
            "target": "GeographicObject"
          }
        ]
      }
    ]
  }
}
```

#### Get Concept by ID

```http
GET /ontology/concepts/{concept_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "concept_001",
    "name": "SpatialFeature",
    "type": "class",
    "domain": "geospatial",
    "description": "A spatial feature in geographic space",
    "properties": [
      {
        "name": "geometry",
        "type": "Geometry",
        "description": "The geometric representation",
        "required": true,
        "cardinality": "1"
      }
    ],
    "relationships": [
      {
        "type": "subClassOf",
        "target": "GeographicObject",
        "target_name": "GeographicObject"
      }
    ],
    "instances": [
      {
        "id": "instance_001",
        "name": "Golden Gate Bridge",
        "type": "SpatialFeature"
      }
    ]
  }
}
```

### Workflow API

#### List Workflows

```http
GET /workflows
```

**Parameters:**
- `status` (string, optional): Filter by status
- `type` (string, optional): Filter by workflow type
- `page` (integer, optional): Page number
- `limit` (integer, optional): Items per page

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflows": [
      {
        "id": "wf_001",
        "name": "Environmental Monitoring",
        "description": "Monitor environmental conditions",
        "type": "spatial_analysis",
        "status": "active",
        "created_at": "2023-06-15T10:30:00Z",
        "updated_at": "2023-06-15T10:30:00Z",
        "execution_count": 45,
        "last_execution": "2023-06-15T09:15:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 25,
      "pages": 2
    }
  }
}
```

#### Get Workflow by ID

```http
GET /workflows/{workflow_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "wf_001",
    "name": "Environmental Monitoring",
    "description": "Monitor environmental conditions",
    "type": "spatial_analysis",
    "status": "active",
    "created_at": "2023-06-15T10:30:00Z",
    "updated_at": "2023-06-15T10:30:00Z",
    "execution_count": 45,
    "last_execution": "2023-06-15T09:15:00Z",
    "nodes": [
      {
        "id": "node_001",
        "type": "data_input",
        "name": "Sensor Data",
        "config": {
          "source": "sensor_network",
          "format": "json"
        }
      },
      {
        "id": "node_002",
        "type": "spatial_analysis",
        "name": "Spatial Clustering",
        "config": {
          "method": "kmeans",
          "n_clusters": 5
        }
      }
    ],
    "edges": [
      {
        "source": "node_001",
        "target": "node_002"
      }
    ]
  }
}
```

#### Execute Workflow

```http
POST /workflows/{workflow_id}/execute
```

**Request Body:**
```json
{
  "parameters": {
    "spatial_resolution": 0.01,
    "temporal_resolution": "1H",
    "analysis_method": "kmeans"
  },
  "input_data": {
    "sensor_data": "s3://bucket/sensor_data.json",
    "boundary_data": "s3://bucket/boundaries.geojson"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "execution_id": "exec_001",
    "workflow_id": "wf_001",
    "status": "running",
    "created_at": "2023-06-15T10:30:00Z",
    "estimated_completion": "2023-06-15T10:35:00Z",
    "progress": 0.0
  }
}
```

#### Get Execution Status

```http
GET /workflows/{workflow_id}/executions/{execution_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "execution_id": "exec_001",
    "workflow_id": "wf_001",
    "status": "completed",
    "created_at": "2023-06-15T10:30:00Z",
    "completed_at": "2023-06-15T10:32:00Z",
    "progress": 1.0,
    "results": {
      "output_files": [
        "s3://bucket/results/clusters.geojson",
        "s3://bucket/results/analysis_report.pdf"
      ],
      "metrics": {
        "processing_time": 120.5,
        "data_points_processed": 15000,
        "clusters_found": 5
      }
    }
  }
}
```

### Spatial Analysis API

#### Analyze Spatial Data

```http
POST /spatial/analyze
```

**Request Body:**
```json
{
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [-122.4194, 37.7749]
        },
        "properties": {
          "temperature": 22.5,
          "humidity": 65.0
        }
      }
    ]
  },
  "analysis_type": "clustering",
  "parameters": {
    "method": "kmeans",
    "n_clusters": 5,
    "spatial_resolution": 0.01
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_001",
    "type": "clustering",
    "results": {
      "clusters": [
        {
          "id": "cluster_001",
          "centroid": [-122.4194, 37.7749],
          "size": 150,
          "properties": {
            "avg_temperature": 22.5,
            "avg_humidity": 65.0
          }
        }
      ],
      "metrics": {
        "silhouette_score": 0.75,
        "inertia": 1250.5
      }
    },
    "processing_time": 2.5
  }
}
```

#### Get Spatial Analysis Results

```http
GET /spatial/analysis/{analysis_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_001",
    "type": "clustering",
    "status": "completed",
    "created_at": "2023-06-15T10:30:00Z",
    "results": {
      "clusters": [
        {
          "id": "cluster_001",
          "centroid": [-122.4194, 37.7749],
          "size": 150,
          "properties": {
            "avg_temperature": 22.5,
            "avg_humidity": 65.0
          },
          "geojson": {
            "type": "Feature",
            "geometry": {
              "type": "Polygon",
              "coordinates": [[...]]
            },
            "properties": {
              "cluster_id": "cluster_001"
            }
          }
        }
      ],
      "metrics": {
        "silhouette_score": 0.75,
        "inertia": 1250.5
      }
    }
  }
}
```

### Active Inference API

#### Create Active Inference Model

```http
POST /active-inference/models
```

**Request Body:**
```json
{
  "name": "Environmental Model",
  "description": "Model for environmental monitoring",
  "state_space": ["temperature", "humidity", "air_quality"],
  "observation_space": ["sensor_reading"],
  "precision": 1.0,
  "config": {
    "learning_rate": 0.01,
    "planning_horizon": 5
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "model_id": "model_001",
    "name": "Environmental Model",
    "description": "Model for environmental monitoring",
    "state_space": ["temperature", "humidity", "air_quality"],
    "observation_space": ["sensor_reading"],
    "precision": 1.0,
    "status": "created",
    "created_at": "2023-06-15T10:30:00Z",
    "updated_at": "2023-06-15T10:30:00Z"
  }
}
```

#### Update Model Beliefs

```http
POST /active-inference/models/{model_id}/update
```

**Request Body:**
```json
{
  "observation": {
    "sensor_reading": 25.5
  },
  "context": {
    "location": [-122.4194, 37.7749],
    "timestamp": "2023-06-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "model_id": "model_001",
    "beliefs_updated": true,
    "current_beliefs": {
      "temperature": 22.5,
      "humidity": 65.0,
      "air_quality": 45.0
    },
    "free_energy": 0.125,
    "updated_at": "2023-06-15T10:30:00Z"
  }
}
```

#### Make Predictions

```http
POST /active-inference/models/{model_id}/predict
```

**Request Body:**
```json
{
  "input": {
    "temperature": 25.0,
    "humidity": 60.0,
    "air_quality": 40.0
  },
  "prediction_type": "observation",
  "uncertainty_samples": 1000
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "model_id": "model_001",
    "prediction": {
      "sensor_reading": 24.8
    },
    "uncertainty": {
      "mean": 24.8,
      "std": 1.2,
      "ci_lower": 22.4,
      "ci_upper": 27.2,
      "samples": [24.1, 25.2, 24.8, ...]
    },
    "free_energy": 0.098,
    "predicted_at": "2023-06-15T10:30:00Z"
  }
}
```

## 🔧 Client Libraries

### Python Client

```python
from geo_infer_api import GeoInferClient

# Initialize client
client = GeoInferClient(
    api_key="YOUR_API_KEY",
    base_url="https://api.geo-infer.org/v1"
)

# Knowledge Base operations
articles = client.knowledge.get_articles(query="spatial analysis")
article = client.knowledge.get_article("kb_001")

# Workflow operations
workflows = client.workflows.list()
workflow = client.workflows.get("wf_001")
execution = client.workflows.execute("wf_001", parameters={...})

# Spatial analysis
analysis = client.spatial.analyze(data=geojson_data, analysis_type="clustering")

# Active inference
model = client.active_inference.create_model(
    name="Environmental Model",
    state_space=["temperature", "humidity"],
    observation_space=["sensor_reading"]
)
client.active_inference.update_beliefs("model_001", observation={"sensor_reading": 25.5})
prediction = client.active_inference.predict("model_001", input={"temperature": 25.0})
```

### JavaScript Client

```javascript
import { GeoInferClient } from '@geo-infer/api-client';

// Initialize client
const client = new GeoInferClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.geo-infer.org/v1'
});

// Knowledge Base operations
const articles = await client.knowledge.getArticles({ query: 'spatial analysis' });
const article = await client.knowledge.getArticle('kb_001');

// Workflow operations
const workflows = await client.workflows.list();
const workflow = await client.workflows.get('wf_001');
const execution = await client.workflows.execute('wf_001', { parameters: {} });

// Spatial analysis
const analysis = await client.spatial.analyze({
  data: geojsonData,
  analysisType: 'clustering'
});

// Active inference
const model = await client.activeInference.createModel({
  name: 'Environmental Model',
  stateSpace: ['temperature', 'humidity'],
  observationSpace: ['sensor_reading']
});
await client.activeInference.updateBeliefs('model_001', { sensor_reading: 25.5 });
const prediction = await client.activeInference.predict('model_001', { temperature: 25.0 });
```

## 📊 Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "analysis_type",
      "issue": "Value must be one of: clustering, interpolation, buffer"
    }
  },
  "timestamp": "2023-06-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing authentication | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

### Rate Limiting

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 🔐 Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0 Authentication

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Scopes

- `read:knowledge` - Read knowledge base articles
- `write:knowledge` - Create and update articles
- `read:ontology` - Read ontology concepts
- `write:ontology` - Create and update concepts
- `read:workflows` - Read workflows
- `write:workflows` - Create and execute workflows
- `read:spatial` - Read spatial analysis results
- `write:spatial` - Perform spatial analysis
- `read:active-inference` - Read active inference models
- `write:active-inference` - Create and update models

## 📈 Pagination

### Pagination Headers

```http
X-Pagination-Page: 1
X-Pagination-Limit: 20
X-Pagination-Total: 150
X-Pagination-Pages: 8
```

### Pagination Parameters

- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

## 🔍 Filtering and Search

### Search Parameters

```http
GET /knowledge/articles?query=spatial analysis&category=tutorial&tags=beginner
```

### Filtering Options

- `query` (string): Full-text search
- `category` (string): Filter by category
- `tags` (array): Filter by tags
- `status` (string): Filter by status
- `type` (string): Filter by type
- `date_from` (datetime): Filter by start date
- `date_to` (datetime): Filter by end date

## 📋 Webhooks

### Webhook Events

```json
{
  "event": "workflow.completed",
  "data": {
    "workflow_id": "wf_001",
    "execution_id": "exec_001",
    "status": "completed",
    "results": {
      "output_files": ["s3://bucket/results/analysis.pdf"]
    }
  },
  "timestamp": "2023-06-15T10:30:00Z"
}
```

### Available Events

- `workflow.started` - Workflow execution started
- `workflow.completed` - Workflow execution completed
- `workflow.failed` - Workflow execution failed
- `analysis.completed` - Spatial analysis completed
- `model.updated` - Active inference model updated
- `article.created` - Knowledge base article created
- `article.updated` - Knowledge base article updated

## 🚀 SDK Examples

### Complete Python Example

```python
from geo_infer_api import GeoInferClient
import json

# Initialize client
client = GeoInferClient(
    api_key="YOUR_API_KEY",
    base_url="https://api.geo-infer.org/v1"
)

# Create environmental monitoring workflow
workflow_config = {
    "name": "Environmental Monitoring",
    "description": "Monitor environmental conditions",
    "nodes": [
        {
            "id": "data_input",
            "type": "data_input",
            "name": "Sensor Data",
            "config": {"source": "sensor_network"}
        },
        {
            "id": "spatial_analysis",
            "type": "spatial_analysis",
            "name": "Spatial Clustering",
            "config": {"method": "kmeans", "n_clusters": 5}
        },
        {
            "id": "active_inference",
            "type": "active_inference",
            "name": "Environmental Model",
            "config": {"state_space": ["temperature", "humidity"]}
        }
    ],
    "edges": [
        {"source": "data_input", "target": "spatial_analysis"},
        {"source": "spatial_analysis", "target": "active_inference"}
    ]
}

# Create workflow
workflow = client.workflows.create(workflow_config)

# Execute workflow
execution = client.workflows.execute(
    workflow["id"],
    parameters={
        "spatial_resolution": 0.01,
        "temporal_resolution": "1H"
    },
    input_data={
        "sensor_data": "s3://bucket/sensor_data.json"
    }
)

# Monitor execution
while execution["status"] == "running":
    execution = client.workflows.get_execution(
        workflow["id"], 
        execution["id"]
    )
    print(f"Progress: {execution['progress']:.1%}")
    time.sleep(5)

# Get results
if execution["status"] == "completed":
    results = execution["results"]
    print(f"Analysis completed in {execution['processing_time']:.1f} seconds")
    print(f"Output files: {results['output_files']}")
```

### Complete JavaScript Example

```javascript
import { GeoInferClient } from '@geo-infer/api-client';

// Initialize client
const client = new GeoInferClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.geo-infer.org/v1'
});

// Create environmental monitoring workflow
const workflowConfig = {
  name: 'Environmental Monitoring',
  description: 'Monitor environmental conditions',
  nodes: [
    {
      id: 'data_input',
      type: 'data_input',
      name: 'Sensor Data',
      config: { source: 'sensor_network' }
    },
    {
      id: 'spatial_analysis',
      type: 'spatial_analysis',
      name: 'Spatial Clustering',
      config: { method: 'kmeans', n_clusters: 5 }
    },
    {
      id: 'active_inference',
      type: 'active_inference',
      name: 'Environmental Model',
      config: { state_space: ['temperature', 'humidity'] }
    }
  ],
  edges: [
    { source: 'data_input', target: 'spatial_analysis' },
    { source: 'spatial_analysis', target: 'active_inference' }
  ]
};

// Create and execute workflow
async function runEnvironmentalAnalysis() {
  try {
    // Create workflow
    const workflow = await client.workflows.create(workflowConfig);
    
    // Execute workflow
    const execution = await client.workflows.execute(workflow.id, {
      parameters: {
        spatial_resolution: 0.01,
        temporal_resolution: '1H'
      },
      input_data: {
        sensor_data: 's3://bucket/sensor_data.json'
      }
    });
    
    // Monitor execution
    while (execution.status === 'running') {
      const updatedExecution = await client.workflows.getExecution(
        workflow.id, 
        execution.id
      );
      console.log(`Progress: ${(updatedExecution.progress * 100).toFixed(1)}%`);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
    
    // Get results
    if (execution.status === 'completed') {
      const results = execution.results;
      console.log(`Analysis completed in ${execution.processing_time}s`);
      console.log(`Output files: ${results.output_files}`);
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

runEnvironmentalAnalysis();
```

## 🔗 Related Documentation

- **[Getting Started](../getting_started/index.md)** - Quick start guide
- **[Authentication Guide](../security/authentication.md)** - Detailed authentication
- **[Webhook Guide](../integration/webhooks.md)** - Webhook setup and events
- **[SDK Documentation](../developer_guide/sdk.md)** - Client library documentation
- **[Rate Limiting](../api/rate_limiting.md)** - Rate limit policies

---

**Need help?** Check the [API FAQ](../support/api_issues.md) or ask on the [Community Forum](https://forum.geo-infer.org)! 