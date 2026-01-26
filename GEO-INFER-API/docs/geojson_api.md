# GeoJSON API Reference

## Introduction

This document describes the GeoJSON API endpoints provided by GEO-INFER-API for handling geospatial data in GeoJSON format.

## Base URL

```
https://api.geo-infer.org/v1/geojson
```

## Endpoints

### Create Feature

```http
POST /features
Content-Type: application/json
```

**Request Body:**

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  },
  "properties": {
    "name": "San Francisco",
    "population": 883305
  }
}
```

**Response:**

```json
{
  "id": "feat_abc123",
  "status": "created",
  "feature": { ... }
}
```

### Get Feature

```http
GET /features/{id}
```

**Response:**

```json
{
  "type": "Feature",
  "id": "feat_abc123",
  "geometry": { ... },
  "properties": { ... }
}
```

### Query Features

```http
GET /features?bbox=-123,37,-122,38&properties.type=city
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `bbox` | string | Bounding box (west,south,east,north) |
| `within` | GeoJSON | Features within geometry |
| `properties.*` | any | Filter by property values |

### Spatial Operations

#### Buffer

```http
POST /operations/buffer
```

```json
{
  "feature": { ... },
  "distance": 1000,
  "units": "meters"
}
```

#### Intersect

```http
POST /operations/intersect
```

```json
{
  "feature1": { ... },
  "feature2": { ... }
}
```

## Response Formats

All endpoints support:

- `application/geo+json` (default)
- `application/json`

## Error Responses

```json
{
  "error": "invalid_geometry",
  "message": "Invalid GeoJSON geometry",
  "details": { ... }
}
```

---

**Last Updated**: 2026-01-26
