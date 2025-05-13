# Workflow API

The Workflow API provides programmatic access to create, manage, and execute geospatial data processing workflows.

## API Endpoints

### Workflow Management

#### List Workflows

```
GET /api/v1/workflows
```

Retrieves a list of all available workflows.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number for pagination (default: 1) |
| `page_size` | integer | No | Number of items per page (default: 20) |
| `sort_by` | string | No | Field to sort by (default: "created_at") |
| `sort_dir` | string | No | Sort direction ("asc" or "desc", default: "desc") |
| `tags` | string | No | Filter by tags (comma-separated) |
| `status` | string | No | Filter by status (e.g., "draft", "published") |

**Response:**

```json
{
  "items": [
    {
      "id": "wf-123e4567-e89b-12d3-a456-426614174000",
      "name": "Land Cover Classification",
      "description": "Workflow for classifying land cover from satellite imagery",
      "tags": ["classification", "landsat", "machine-learning"],
      "status": "published",
      "created_at": "2023-03-15T10:30:00Z",
      "updated_at": "2023-03-16T14:20:00Z",
      "created_by": "user-123",
      "node_count": 5,
      "execution_count": 12
    },
    // Additional workflow items...
  ],
  "pagination": {
    "total_items": 45,
    "total_pages": 3,
    "current_page": 1,
    "page_size": 20
  }
}
```

#### Get Workflow

```
GET /api/v1/workflows/{workflow_id}
```

Retrieves a specific workflow by ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Unique identifier of the workflow |

**Response:**

```json
{
  "id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "Land Cover Classification",
  "description": "Workflow for classifying land cover from satellite imagery",
  "tags": ["classification", "landsat", "machine-learning"],
  "status": "published",
  "created_at": "2023-03-15T10:30:00Z",
  "updated_at": "2023-03-16T14:20:00Z",
  "created_by": "user-123",
  "nodes": [
    {
      "id": "node-1",
      "type": "DataSource",
      "name": "Landsat Data",
      "parameters": {
        "source_type": "raster",
        "path": "landsat.tif"
      },
      "position": {
        "x": 100,
        "y": 100
      }
    },
    // Additional nodes...
  ],
  "edges": [
    {
      "id": "edge-1",
      "source_node": "node-1",
      "source_port": "output",
      "target_node": "node-2",
      "target_port": "input"
    },
    // Additional edges...
  ],
  "parameters": {
    "classification_algorithm": "random_forest",
    "training_percentage": 0.7
  }
}
```

#### Create Workflow

```
POST /api/v1/workflows
```

Creates a new workflow.

**Request Body:**

```json
{
  "name": "Land Cover Classification",
  "description": "Workflow for classifying land cover from satellite imagery",
  "tags": ["classification", "landsat", "machine-learning"],
  "nodes": [
    {
      "id": "node-1",
      "type": "DataSource",
      "name": "Landsat Data",
      "parameters": {
        "source_type": "raster",
        "path": "landsat.tif"
      },
      "position": {
        "x": 100,
        "y": 100
      }
    },
    // Additional nodes...
  ],
  "edges": [
    {
      "id": "edge-1",
      "source_node": "node-1",
      "source_port": "output",
      "target_node": "node-2",
      "target_port": "input"
    },
    // Additional edges...
  ],
  "parameters": {
    "classification_algorithm": "random_forest",
    "training_percentage": 0.7
  }
}
```

**Response:**

```json
{
  "id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "name": "Land Cover Classification",
  "description": "Workflow for classifying land cover from satellite imagery",
  "tags": ["classification", "landsat", "machine-learning"],
  "status": "draft",
  "created_at": "2023-03-15T10:30:00Z",
  "updated_at": "2023-03-15T10:30:00Z",
  "created_by": "user-123",
  // Additional workflow properties...
}
```

#### Update Workflow

```
PUT /api/v1/workflows/{workflow_id}
```

Updates an existing workflow.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Unique identifier of the workflow |

**Request Body:** Same as the Create Workflow endpoint.

**Response:** Same as the Get Workflow endpoint.

#### Delete Workflow

```
DELETE /api/v1/workflows/{workflow_id}
```

Deletes a workflow.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Unique identifier of the workflow |

**Response:**

```json
{
  "success": true,
  "message": "Workflow deleted successfully"
}
```

### Workflow Execution

#### Execute Workflow

```
POST /api/v1/workflows/{workflow_id}/execute
```

Executes a workflow.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Unique identifier of the workflow |

**Request Body:**

```json
{
  "parameters": {
    "classification_algorithm": "random_forest",
    "training_percentage": 0.8
  },
  "inputs": {
    "landsat_data": "s3://geo-infer-data/landsat/scene123.tif"
  }
}
```

**Response:**

```json
{
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "started_at": "2023-03-16T15:00:00Z",
  "parameters": {
    "classification_algorithm": "random_forest",
    "training_percentage": 0.8
  },
  "inputs": {
    "landsat_data": "s3://geo-infer-data/landsat/scene123.tif"
  }
}
```

#### Get Execution Status

```
GET /api/v1/executions/{execution_id}
```

Gets the status of a workflow execution.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `execution_id` | string | Yes | Unique identifier of the execution |

**Response:**

```json
{
  "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
  "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "started_at": "2023-03-16T15:00:00Z",
  "completed_at": "2023-03-16T15:05:30Z",
  "duration_seconds": 330,
  "node_statuses": [
    {
      "node_id": "node-1",
      "status": "completed",
      "started_at": "2023-03-16T15:00:05Z",
      "completed_at": "2023-03-16T15:01:00Z",
      "duration_seconds": 55
    },
    // Additional node statuses...
  ],
  "outputs": {
    "classified_image": "s3://geo-infer-data/results/classification123.tif",
    "accuracy_report": "s3://geo-infer-data/results/accuracy123.json"
  }
}
```

#### List Executions

```
GET /api/v1/workflows/{workflow_id}/executions
```

Lists all executions for a specific workflow.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Unique identifier of the workflow |

**Query Parameters:** Same as the List Workflows endpoint, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by execution status (e.g., "running", "completed", "failed") |

**Response:**

```json
{
  "items": [
    {
      "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
      "workflow_id": "wf-123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "started_at": "2023-03-16T15:00:00Z",
      "completed_at": "2023-03-16T15:05:30Z",
      "duration_seconds": 330
    },
    // Additional execution items...
  ],
  "pagination": {
    "total_items": 12,
    "total_pages": 1,
    "current_page": 1,
    "page_size": 20
  }
}
```

## Node Types

The Workflow API supports the following node types:

| Type | Description | Inputs | Outputs | Parameters |
|------|-------------|--------|---------|------------|
| `DataSource` | Input data source | None | `output` | `source_type`, `path` |
| `DataSink` | Output data destination | `input` | None | `destination` |
| `Preprocessing` | Data preprocessing operations | `input` | `output` | `method`, `parameters` |
| `Classification` | Image classification | `input` | `output`, `metrics` | `algorithm`, `parameters` |
| `Segmentation` | Image segmentation | `input` | `output`, `metrics` | `algorithm`, `parameters` |
| `ChangeDetection` | Change detection | `before`, `after` | `output`, `metrics` | `method`, `threshold` |
| `Evaluation` | Result evaluation | `predictions`, `ground_truth` | `metrics` | `metrics` |
| `Visualization` | Result visualization | `input` | `visualization` | `type`, `parameters` |
| `Transform` | Coordinate transformation | `input` | `output` | `source_crs`, `target_crs` |
| `Filter` | Data filtering | `input` | `output` | `filter_type`, `parameters` |
| `Join` | Data joining | `left`, `right` | `output` | `join_type`, `join_attributes` |
| `Aggregation` | Data aggregation | `input` | `output` | `group_by`, `aggregations` |
| `Script` | Custom script execution | varies | varies | `script`, `language` |

## Client Libraries

### Python Client

```python
from geo_infer_intra.client import WorkflowClient

# Initialize the client
workflow_client = WorkflowClient(api_key="your-api-key")

# List workflows
workflows = workflow_client.list_workflows(tags=["classification"])

# Get a specific workflow
workflow = workflow_client.get_workflow("wf-123e4567-e89b-12d3-a456-426614174000")

# Create a new workflow
new_workflow = workflow_client.create_workflow(
    name="Land Cover Classification",
    description="Workflow for classifying land cover from satellite imagery",
    tags=["classification", "landsat", "machine-learning"],
    nodes=[...],
    edges=[...],
    parameters={...}
)

# Execute a workflow
execution = workflow_client.execute_workflow(
    workflow_id="wf-123e4567-e89b-12d3-a456-426614174000",
    parameters={
        "classification_algorithm": "random_forest",
        "training_percentage": 0.8
    },
    inputs={
        "landsat_data": "s3://geo-infer-data/landsat/scene123.tif"
    }
)

# Check execution status
status = workflow_client.get_execution_status("exec-123e4567-e89b-12d3-a456-426614174000")
```

### JavaScript Client

```javascript
import { WorkflowClient } from 'geo-infer-intra-client';

// Initialize the client
const workflowClient = new WorkflowClient({
  apiKey: 'your-api-key'
});

// List workflows
workflowClient.listWorkflows({ tags: ['classification'] })
  .then(workflows => console.log(workflows))
  .catch(error => console.error(error));

// Get a specific workflow
workflowClient.getWorkflow('wf-123e4567-e89b-12d3-a456-426614174000')
  .then(workflow => console.log(workflow))
  .catch(error => console.error(error));

// Create a new workflow
workflowClient.createWorkflow({
  name: 'Land Cover Classification',
  description: 'Workflow for classifying land cover from satellite imagery',
  tags: ['classification', 'landsat', 'machine-learning'],
  nodes: [...],
  edges: [...],
  parameters: {...}
})
  .then(newWorkflow => console.log(newWorkflow))
  .catch(error => console.error(error));

// Execute a workflow
workflowClient.executeWorkflow({
  workflowId: 'wf-123e4567-e89b-12d3-a456-426614174000',
  parameters: {
    classification_algorithm: 'random_forest',
    training_percentage: 0.8
  },
  inputs: {
    landsat_data: 's3://geo-infer-data/landsat/scene123.tif'
  }
})
  .then(execution => console.log(execution))
  .catch(error => console.error(error));

// Check execution status
workflowClient.getExecutionStatus('exec-123e4567-e89b-12d3-a456-426614174000')
  .then(status => console.log(status))
  .catch(error => console.error(error));
``` 