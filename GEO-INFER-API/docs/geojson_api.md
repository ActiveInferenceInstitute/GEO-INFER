# GeoJSON Polygon API

This document provides an overview of the GeoJSON Polygon API endpoints available in the GEO-INFER-API module.

## Base URL

All API endpoints are relative to the base URL: `http://your-server:port/api/v1`

## OGC API - Features Compliant Endpoints

The API follows the [OGC API Features](https://ogcapi.ogc.org/features/) standard for accessing geospatial data.

### List Collections

```
GET /collections
```

Returns a list of available feature collections.

**Example Response:**
```json
{
  "collections": [
    {
      "id": "polygons",
      "title": "GeoJSON Polygons",
      "description": "Collection of polygon features",
      "links": [
        {
          "href": "/api/v1/collections/polygons",
          "rel": "self",
          "type": "application/json",
          "title": "This collection"
        },
        {
          "href": "/api/v1/collections/polygons/items",
          "rel": "items",
          "type": "application/geo+json",
          "title": "Items in this collection"
        }
      ]
    }
  ],
  "links": [
    {
      "href": "/api/v1/collections",
      "rel": "self",
      "type": "application/json",
      "title": "Collections"
    }
  ]
}
```

### Get Polygon Collection Metadata

```
GET /collections/polygons
```

Returns metadata about the polygon collection.

**Example Response:**
```json
{
  "id": "polygons",
  "title": "GeoJSON Polygons",
  "description": "Collection of polygon features",
  "extent": {
    "spatial": {
      "bbox": [[-180, -90, 180, 90]]
    },
    "temporal": {
      "interval": [["2020-01-01T00:00:00Z", "2025-01-01T00:00:00Z"]]
    }
  },
  "links": [
    {
      "href": "/api/v1/collections/polygons",
      "rel": "self",
      "type": "application/json",
      "title": "This collection"
    },
    {
      "href": "/api/v1/collections/polygons/items",
      "rel": "items",
      "type": "application/geo+json",
      "title": "Items in this collection"
    }
  ]
}
```

### List Polygon Features

```
GET /collections/polygons/items
```

Returns a GeoJSON FeatureCollection of polygon features.

**Query Parameters:**
- `bbox` (optional): Bounding box filter in format "minLon,minLat,maxLon,maxLat"
- `limit` (optional): Maximum number of features to return (default: 10, max: 1000)

**Example Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "sf-triangle-demo",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-122.51, 37.77],
            [-122.42, 37.81],
            [-122.37, 37.73],
            [-122.51, 37.77]
          ]
        ]
      },
      "properties": {
        "name": "San Francisco Triangle",
        "description": "A triangular area in San Francisco",
        "tags": ["example", "demo", "triangle"]
      }
    }
  ]
}
```

### Get a Specific Polygon Feature

```
GET /collections/polygons/items/{feature_id}
```

Returns a specific GeoJSON Feature with Polygon geometry.

**Example Response:**
```json
{
  "type": "Feature",
  "id": "sf-triangle-demo",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.51, 37.77],
        [-122.42, 37.81],
        [-122.37, 37.73],
        [-122.51, 37.77]
      ]
    ]
  },
  "properties": {
    "name": "San Francisco Triangle",
    "description": "A triangular area in San Francisco",
    "tags": ["example", "demo", "triangle"]
  }
}
```

### Create a New Polygon Feature

```
POST /collections/polygons/items
```

Creates a new GeoJSON Feature with Polygon geometry.

**Request Body:**
```json
{
  "type": "Feature",
  "id": "sf-triangle-demo",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.51, 37.77],
        [-122.42, 37.81],
        [-122.37, 37.73],
        [-122.51, 37.77]
      ]
    ]
  },
  "properties": {
    "name": "San Francisco Triangle",
    "description": "A triangular area in San Francisco",
    "tags": ["example", "demo", "triangle"]
  }
}
```

**Response:**
The created feature is returned with a 201 status code.

### Update a Polygon Feature

```
PUT /collections/polygons/items/{feature_id}
```

Updates an existing GeoJSON Feature with Polygon geometry.

**Request Body:**
Same as for creating a new feature.

**Response:**
The updated feature is returned with a 200 status code.

### Delete a Polygon Feature

```
DELETE /collections/polygons/items/{feature_id}
```

Deletes a specific polygon feature.

**Response:**
Returns a 204 status code on successful deletion.

## Extended Operations

In addition to the standard OGC API Features endpoints, the API provides the following operations for polygon features:

### Calculate Polygon Area

```
POST /operations/polygon/area
```

Calculates the approximate area of a polygon in square kilometers.

**Request Body:**
A GeoJSON Feature with Polygon geometry.

**Example Response:**
```json
{
  "area_sq_km": 123.45,
  "feature_id": "sf-triangle-demo"
}
```

### Simplify a Polygon

```
POST /operations/polygon/simplify
```

Simplifies a polygon using the Ramer-Douglas-Peucker algorithm.

**Query Parameters:**
- `tolerance` (optional): Simplification tolerance (default: 0.01, range: 0.001-1.0)

**Request Body:**
A GeoJSON Feature with Polygon geometry.

**Response:**
Returns the simplified polygon as a GeoJSON Feature.

### Check if a Point is Inside a Polygon

```
POST /operations/polygon/contains
```

Checks if a point is inside a polygon.

**Query Parameters:**
- `lon`: Longitude of the point (required)
- `lat`: Latitude of the point (required)

**Request Body:**
A GeoJSON Feature with Polygon geometry.

**Example Response:**
```json
{
  "contains": true,
  "feature_id": "sf-triangle-demo",
  "point": [-122.42, 37.78]
}
```

## Error Responses

The API returns appropriate HTTP status codes and error messages for various error conditions:

- `400 Bad Request`: Invalid input data (e.g., malformed GeoJSON, invalid coordinates)
- `404 Not Found`: Requested feature not found
- `409 Conflict`: Feature ID already exists (for create operations)
- `422 Unprocessable Entity`: Validation error (e.g., invalid polygon geometry)

Example error response:
```json
{
  "detail": "Polygon feature with ID nonexistent not found"
}
``` 