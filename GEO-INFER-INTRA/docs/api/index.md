# API Reference

The GEO-INFER-INTRA API provides programmatic access to all features and functionalities of the GEO-INFER-INTRA system. This document serves as the central reference for understanding and using the API.

## Contents

- [API Overview](overview.md) - Introduction to the API
- [Authentication](authentication.md) - API authentication methods
- [API Architecture](architecture.md) - Architecture and design principles
- [REST API](rest/index.md) - REST API reference
- [GraphQL API](graphql/index.md) - GraphQL API reference
- [Webhooks](webhooks.md) - Webhook integration
- [API Clients](clients.md) - Client libraries for various languages
- [Rate Limiting](rate_limiting.md) - API usage limits
- [Error Handling](error_handling.md) - API error codes and handling
- [Versioning](versioning.md) - API versioning strategy

## API Architecture

The GEO-INFER-INTRA API follows a layered architecture with both REST and GraphQL interfaces:

```mermaid
graph TD
    subgraph "Client Applications"
        WEB[Web Applications]
        MOBILE[Mobile Apps]
        CLI[Command Line Tools]
        SCRIPT[Scripts]
        THIRD_PARTY[Third-party Systems]
    end
    
    subgraph "API Gateway"
        REST[REST API]
        GRAPHQL[GraphQL API]
        AUTH[Authentication]
        RATE_LIMIT[Rate Limiting]
        CACHE[Response Cache]
    end
    
    subgraph "API Services"
        DOC_API[Documentation API]
        KB_API[Knowledge Base API]
        ONTO_API[Ontology API]
        WORKFLOW_API[Workflow API]
    end
    
    subgraph "Core Services"
        DOC_SERVICE[Documentation Service]
        KB_SERVICE[Knowledge Base Service]
        ONTO_SERVICE[Ontology Service]
        WORKFLOW_SERVICE[Workflow Service]
    end
    
    WEB --> REST
    WEB --> GRAPHQL
    MOBILE --> REST
    MOBILE --> GRAPHQL
    CLI --> REST
    SCRIPT --> REST
    THIRD_PARTY --> REST
    
    REST --> AUTH
    GRAPHQL --> AUTH
    AUTH --> RATE_LIMIT
    RATE_LIMIT --> CACHE
    
    CACHE --> DOC_API
    CACHE --> KB_API
    CACHE --> ONTO_API
    CACHE --> WORKFLOW_API
    
    DOC_API --> DOC_SERVICE
    KB_API --> KB_SERVICE
    ONTO_API --> ONTO_SERVICE
    WORKFLOW_API --> WORKFLOW_SERVICE
    
    classDef client fill:#bbf,stroke:#333,stroke-width:1px
    classDef gateway fill:#f9f,stroke:#333,stroke-width:1px
    classDef api fill:#dfd,stroke:#333,stroke-width:1px
    classDef service fill:#ffd,stroke:#333,stroke-width:1px
    
    class WEB,MOBILE,CLI,SCRIPT,THIRD_PARTY client
    class REST,GRAPHQL,AUTH,RATE_LIMIT,CACHE gateway
    class DOC_API,KB_API,ONTO_API,WORKFLOW_API api
    class DOC_SERVICE,KB_SERVICE,ONTO_SERVICE,WORKFLOW_SERVICE service
```

## API Resources

The GEO-INFER-INTRA API provides access to the following primary resources:

### Documentation

Resources related to the documentation system:

- `/api/v1/docs` - Documentation resources
- `/api/v1/docs/search` - Search documentation
- `/api/v1/docs/{id}` - Get specific document
- `/api/v1/docs/categories` - Get documentation categories
- `/api/v1/docs/formats` - Get available documentation formats

### Knowledge Base

Resources related to the knowledge base:

- `/api/v1/kb` - Knowledge base resources
- `/api/v1/kb/search` - Search knowledge base
- `/api/v1/kb/articles/{id}` - Get specific article
- `/api/v1/kb/categories` - Get knowledge base categories
- `/api/v1/kb/tags` - Get knowledge base tags

### Ontology

Resources related to the ontology system:

- `/api/v1/ontology` - Ontology resources
- `/api/v1/ontology/search` - Search ontology
- `/api/v1/ontology/concepts/{id}` - Get specific concept
- `/api/v1/ontology/relations` - Get relationships
- `/api/v1/ontology/domains` - Get domains

### Workflows

Resources related to the workflow system:

- `/api/v1/workflows` - Workflow resources
- `/api/v1/workflows/{id}` - Get specific workflow
- `/api/v1/workflows/{id}/execute` - Execute a workflow
- `/api/v1/workflows/{id}/status` - Check workflow execution status
- `/api/v1/workflows/{id}/results` - Get workflow execution results
- `/api/v1/workflows/templates` - Get workflow templates

## API Endpoints

### REST API

The REST API follows RESTful principles and provides endpoints for CRUD operations on all resources. Each endpoint supports standard HTTP methods:

- `GET` - Retrieve resources
- `POST` - Create new resources
- `PUT` - Update existing resources
- `PATCH` - Partially update resources
- `DELETE` - Delete resources

Example endpoints with HTTP methods:

```
GET    /api/v1/kb/articles         - List articles
GET    /api/v1/kb/articles/{id}    - Get a specific article
POST   /api/v1/kb/articles         - Create a new article
PUT    /api/v1/kb/articles/{id}    - Update an article
PATCH  /api/v1/kb/articles/{id}    - Partially update an article
DELETE /api/v1/kb/articles/{id}    - Delete an article
```

### GraphQL API

The GraphQL API provides a single endpoint for all operations:

```
POST /api/v1/graphql
```

With this endpoint, clients can query exactly the data they need using GraphQL queries and mutations. Example GraphQL operations:

**Query**:
```graphql
query {
  knowledgeBase {
    articles(limit: 5, offset: 0) {
      id
      title
      summary
      tags
      createdAt
    }
  }
}
```

**Mutation**:
```graphql
mutation {
  createArticle(input: {
    title: "Understanding Spatial Indexing",
    summary: "An overview of spatial indexing methods",
    content: "Spatial indexing is crucial for...",
    tags: ["spatial", "indexing", "performance"]
  }) {
    id
    title
    createdAt
  }
}
```

## Authentication

The API supports multiple authentication methods:

- **API Keys** - For server-to-server communication
- **OAuth 2.0** - For user authentication
- **JWT Tokens** - For session management

Example of API key authentication:

```bash
curl -X GET "https://api.geo-infer.org/intra/v1/kb/articles" \
  -H "X-API-Key: your_api_key_here"
```

Example of OAuth 2.0 authentication:

```bash
# Step 1: Get an access token
curl -X POST "https://api.geo-infer.org/intra/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user@example.com&password=password123"

# Step 2: Use the access token for API requests
curl -X GET "https://api.geo-infer.org/intra/v1/kb/articles" \
  -H "Authorization: Bearer your_access_token_here"
```

## Request and Response Format

### REST API

The REST API accepts and returns data in JSON format by default, but also supports other formats like XML when specified in the `Accept` header.

**Request Example:**

```bash
curl -X POST "https://api.geo-infer.org/intra/v1/kb/articles" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "title": "Understanding Spatial Indexing",
    "summary": "An overview of spatial indexing methods",
    "content": "Spatial indexing is crucial for...",
    "tags": ["spatial", "indexing", "performance"],
    "category": "algorithms"
  }'
```

**Response Example:**

```json
{
  "id": "kb-123456",
  "title": "Understanding Spatial Indexing",
  "summary": "An overview of spatial indexing methods",
  "content": "Spatial indexing is crucial for...",
  "tags": ["spatial", "indexing", "performance"],
  "category": "algorithms",
  "createdAt": "2023-04-15T10:30:45Z",
  "updatedAt": "2023-04-15T10:30:45Z",
  "author": "user@example.com"
}
```

### GraphQL API

The GraphQL API accepts and returns data in JSON format.

**Request Example:**

```bash
curl -X POST "https://api.geo-infer.org/intra/v1/graphql" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "query": "query { knowledgeBase { articles(limit: 5) { id title summary tags } } }"
  }'
```

**Response Example:**

```json
{
  "data": {
    "knowledgeBase": {
      "articles": [
        {
          "id": "kb-123456",
          "title": "Understanding Spatial Indexing",
          "summary": "An overview of spatial indexing methods",
          "tags": ["spatial", "indexing", "performance"]
        },
        {
          "id": "kb-123457",
          "title": "Geospatial Data Formats",
          "summary": "A comparison of common geospatial data formats",
          "tags": ["geospatial", "data", "formats"]
        }
      ]
    }
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request:

- `2xx` - Success
- `4xx` - Client errors
- `5xx` - Server errors

Detailed error information is provided in the response body:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested article was not found",
    "details": {
      "resourceType": "article",
      "resourceId": "kb-123456"
    }
  }
}
```

## Pagination

List endpoints support pagination through query parameters:

- `limit` - Maximum number of items to return
- `offset` - Number of items to skip
- `page` - Page number (alternative to offset)
- `per_page` - Number of items per page (alternative to limit)

Example:

```
GET /api/v1/kb/articles?limit=10&offset=20
```

The response includes pagination metadata:

```json
{
  "data": [...],
  "pagination": {
    "total": 135,
    "limit": 10,
    "offset": 20,
    "next": "/api/v1/kb/articles?limit=10&offset=30",
    "previous": "/api/v1/kb/articles?limit=10&offset=10"
  }
}
```

## Filtering and Sorting

List endpoints support filtering and sorting through query parameters:

- `filter[field]=value` - Filter by field value
- `sort=field` - Sort by field (ascending)
- `sort=-field` - Sort by field (descending)

Example:

```
GET /api/v1/kb/articles?filter[category]=algorithms&sort=-createdAt
```

## API Client Libraries

Official client libraries are available for popular programming languages:

### Python

```python
from geo_infer.client import IntraClient

# Initialize the client
client = IntraClient(api_url="https://api.geo-infer.org/intra/v1", api_key="your_api_key")

# Use the client to interact with the API
articles = client.knowledge_base.list_articles(
    limit=10,
    filter={"category": "algorithms"},
    sort="-createdAt"
)

for article in articles:
    print(f"{article.title} - {article.summary}")

# Create a new article
new_article = client.knowledge_base.create_article(
    title="New Article",
    summary="Article summary",
    content="Article content",
    tags=["tag1", "tag2"],
    category="category1"
)
```

### JavaScript

```javascript
import { IntraClient } from 'geo-infer-client';

// Initialize the client
const client = new IntraClient({
  apiUrl: 'https://api.geo-infer.org/intra/v1',
  apiKey: 'your_api_key'
});

// Use the client to interact with the API
async function getArticles() {
  const articles = await client.knowledgeBase.listArticles({
    limit: 10,
    filter: { category: 'algorithms' },
    sort: '-createdAt'
  });
  
  articles.forEach(article => {
    console.log(`${article.title} - ${article.summary}`);
  });
}

// Create a new article
async function createArticle() {
  const newArticle = await client.knowledgeBase.createArticle({
    title: 'New Article',
    summary: 'Article summary',
    content: 'Article content',
    tags: ['tag1', 'tag2'],
    category: 'category1'
  });
  
  console.log(`Created article with ID: ${newArticle.id}`);
}
```

## API Versioning

The API uses URL-based versioning with the format `/api/v{version_number}/`. The current stable version is `v1`.

When a new version of the API is released, the previous version continues to be supported for a deprecation period. Deprecation notices are provided in the response headers and documentation.

## Rate Limiting

API requests are subject to rate limiting to ensure fair usage and system stability. The current limits are:

- **Basic tier**: 100 requests per minute
- **Standard tier**: 1,000 requests per minute
- **Enterprise tier**: 10,000 requests per minute

Rate limit information is provided in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1618495430
```

## Webhooks

The API supports webhooks for event-driven integration. Webhooks can be registered for various events:

```json
{
  "url": "https://example.com/webhook",
  "events": [
    "kb.article.created",
    "kb.article.updated",
    "workflow.execution.completed"
  ],
  "secret": "webhook_secret"
}
```

When an event occurs, the API sends an HTTP POST request to the registered URL with event details:

```json
{
  "event": "kb.article.created",
  "timestamp": "2023-04-15T10:30:45Z",
  "data": {
    "id": "kb-123456",
    "title": "Understanding Spatial Indexing",
    "summary": "An overview of spatial indexing methods",
    "tags": ["spatial", "indexing", "performance"]
  }
}
```

## OpenAPI Specification

The complete REST API is documented using the [OpenAPI Specification](https://swagger.io/specification/):

- [OpenAPI Specification](openapi.json)
- [API Explorer](explorer.md)

## GraphQL Schema

The complete GraphQL API is documented using the GraphQL Schema Definition Language:

- [GraphQL Schema](schema.graphql)
- [GraphQL Playground](graphql/playground.md)

## Related Resources

- [API Client Libraries](clients.md)
- [API Examples](examples/index.md)
- [API Best Practices](best_practices.md)
- [Integration Guide](../integration/index.md)
- [Troubleshooting](../troubleshooting/api_issues.md) 