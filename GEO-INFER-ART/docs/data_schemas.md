# GEO-INFER-ART Data Schemas

This document describes the key data structures and schemas used in the GEO-INFER-ART module for artistic visualization of geospatial data.

## Geospatial Data Structures

### Vector Data (GeoDataFrame)

```json
{
  "type": "object",
  "required": ["geometry", "crs"],
  "properties": {
    "geometry": {
      "description": "Geometry column containing geographic features",
      "type": "array",
      "items": {
        "oneOf": [
          { "type": "object", "description": "Shapely geometry object (Point, LineString, Polygon, etc.)" }
        ]
      }
    },
    "crs": {
      "description": "Coordinate Reference System",
      "type": ["string", "object"],
      "examples": ["EPSG:4326", "EPSG:3857"]
    },
    "attributes": {
      "description": "Additional feature attributes (columns)",
      "type": "object"
    }
  }
}
```

### Raster Data (NumPy Array)

```json
{
  "type": "array",
  "description": "Raster data as 2D or 3D numpy array",
  "items": {
    "oneOf": [
      {
        "type": "array",
        "description": "2D array: Single band raster (height, width)",
        "items": {
          "type": "array",
          "items": { "type": "number" }
        }
      },
      {
        "type": "array",
        "description": "3D array: Multi-band raster (bands, height, width) or (height, width, bands)",
        "items": {
          "type": "array",
          "items": {
            "type": "array",
            "items": { "type": "number" }
          }
        }
      }
    ]
  }
}
```

## Style and Aesthetic Data

### ColorPalette

```json
{
  "type": "object",
  "required": ["name", "colors"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Name of the color palette",
      "examples": ["viridis", "sunset", "custom_palette"]
    },
    "colors": {
      "type": "array",
      "description": "List of color codes",
      "items": {
        "type": "string",
        "description": "Color in hex, RGB, or named format",
        "examples": ["#ff0000", "red", "rgb(255, 0, 0)"]
      },
      "minItems": 1
    },
    "n_colors": {
      "type": "integer",
      "description": "Number of colors to interpolate in the colormap",
      "default": 256,
      "minimum": 2
    }
  }
}
```

### StyleTransfer

```json
{
  "type": "object",
  "properties": {
    "style_image": {
      "oneOf": [
        { "type": "string", "description": "Path to style image file or predefined style name" },
        { "type": "array", "description": "Image data as numpy array" },
        { "type": "object", "description": "PIL Image object" }
      ]
    },
    "content_image": {
      "oneOf": [
        { "type": "string", "description": "Path to content image file" },
        { "type": "array", "description": "Image data as numpy array" },
        { "type": "object", "description": "PIL Image object" }
      ]
    },
    "style_weight": {
      "type": "number",
      "description": "Weight for style loss in the optimization",
      "default": 1e-2
    },
    "content_weight": {
      "type": "number",
      "description": "Weight for content loss in the optimization",
      "default": 1e4
    },
    "iterations": {
      "type": "integer",
      "description": "Number of optimization iterations",
      "default": 100,
      "minimum": 1
    }
  }
}
```

## Generative and Procedural Art Data

### GenerativeMap Parameters

```json
{
  "type": "object",
  "properties": {
    "region": {
      "oneOf": [
        { "type": "string", "description": "Named region (e.g., 'grand_canyon', 'everest')" },
        { 
          "type": "array", 
          "description": "Custom elevation data as 2D numpy array" 
        },
        {
          "type": "array",
          "description": "Bounding box coordinates (min_lon, min_lat, max_lon, max_lat)",
          "items": { "type": "number" },
          "minItems": 4,
          "maxItems": 4
        }
      ]
    },
    "resolution": {
      "type": "integer",
      "description": "Resolution of the output image",
      "default": 512,
      "minimum": 16
    },
    "abstraction_level": {
      "type": "number",
      "description": "Level of abstraction (0.0 to 1.0)",
      "default": 0.5,
      "minimum": 0.0,
      "maximum": 1.0
    },
    "style": {
      "type": "string",
      "description": "Style of the generative art",
      "enum": ["contour", "flow", "particles", "contour_flow"],
      "default": "contour"
    }
  }
}
```

### ProceduralArt Parameters

```json
{
  "type": "object",
  "properties": {
    "algorithm": {
      "type": "string",
      "description": "Procedural algorithm to use",
      "enum": ["l_system", "cellular_automata", "reaction_diffusion", "noise_field", "voronoi", "fractal_tree"],
      "default": "noise_field"
    },
    "params": {
      "type": "object",
      "description": "Algorithm-specific parameters",
      "properties": {
        "seed": {
          "type": "integer",
          "description": "Random seed for reproducibility"
        },
        "color_palette": {
          "type": "string",
          "description": "Color palette name",
          "examples": ["viridis", "ocean", "sunset"]
        }
      },
      "additionalProperties": true
    },
    "resolution": {
      "type": "array",
      "description": "Output image resolution (width, height)",
      "items": { "type": "integer", "minimum": 16 },
      "minItems": 2,
      "maxItems": 2,
      "default": [800, 800]
    }
  },
  "required": ["algorithm"]
}
```

## Place-Based Art Data

### PlaceArt Location

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Name of the location"
    },
    "coordinates": {
      "type": "array",
      "description": "Geographic coordinates (latitude, longitude)",
      "items": { "type": "number" },
      "minItems": 2,
      "maxItems": 2
    },
    "radius_km": {
      "type": "number",
      "description": "Radius in kilometers to consider around the point",
      "minimum": 0.1,
      "default": 1.0
    },
    "style": {
      "type": "string",
      "description": "Artistic style to apply",
      "enum": ["abstract", "topographic", "cultural", "mixed_media"],
      "default": "abstract"
    }
  },
  "required": ["coordinates"]
}
```

### CulturalMap Data

```json
{
  "type": "object",
  "properties": {
    "region_name": {
      "type": "string",
      "description": "Name of the region"
    },
    "bbox": {
      "type": "array",
      "description": "Bounding box (min_lon, min_lat, max_lon, max_lat)",
      "items": { "type": "number" },
      "minItems": 4,
      "maxItems": 4
    },
    "cultural_theme": {
      "type": "string",
      "description": "Cultural theme to highlight",
      "enum": ["historical", "linguistic"],
      "default": "historical"
    },
    "cultural_style": {
      "type": "string",
      "description": "Cultural style of the visualization",
      "examples": ["classical", "east_asian", "indigenous", "eurasian", "oceanic"]
    },
    "cultural_data": {
      "type": "array",
      "description": "Cultural data elements",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "location": { 
            "type": "array",
            "items": { "type": "number" },
            "minItems": 2,
            "maxItems": 2,
            "description": "Coordinates (longitude, latitude)"
          },
          "additionalProperties": true
        }
      }
    }
  }
}
```

## Utility Data Structures

### GeoArt Metadata

```json
{
  "type": "object",
  "properties": {
    "source": {
      "type": "string",
      "description": "Source of the data (file path, API, etc.)"
    },
    "type": {
      "type": "string",
      "description": "Type of data",
      "enum": ["vector", "raster"]
    },
    "features": {
      "type": "integer",
      "description": "Number of features (for vector data)"
    },
    "attributes": {
      "type": "array",
      "description": "List of attribute names (for vector data)",
      "items": { "type": "string" }
    },
    "shape": {
      "type": "array",
      "description": "Shape of the data (for raster data)",
      "items": { "type": "integer" }
    },
    "bounds": {
      "type": "object",
      "description": "Geographic bounds of the data",
      "properties": {
        "minx": { "type": "number" },
        "miny": { "type": "number" },
        "maxx": { "type": "number" },
        "maxy": { "type": "number" }
      }
    },
    "transform": {
      "type": "object",
      "description": "Affine transformation matrix (for raster data)"
    }
  }
}
```

## File Output Formats

### Image Output

```json
{
  "type": "object",
  "properties": {
    "format": {
      "type": "string",
      "description": "Image file format",
      "enum": ["png", "jpg", "jpeg", "tiff", "pdf", "svg"],
      "default": "png"
    },
    "dpi": {
      "type": "integer",
      "description": "Resolution in dots per inch",
      "default": 300,
      "minimum": 72
    },
    "quality": {
      "type": "integer",
      "description": "Image quality for lossy formats (JPEG)",
      "minimum": 1,
      "maximum": 100,
      "default": 95
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata to embed in the image file"
    }
  }
}
```

## API Response Schema

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "Status of the operation",
      "enum": ["success", "error"]
    },
    "data": {
      "type": "object",
      "description": "Result data (for successful operations)"
    },
    "image_url": {
      "type": "string",
      "description": "URL to the generated image (if applicable)"
    },
    "metadata": {
      "type": "object",
      "description": "Metadata about the generation process"
    },
    "error": {
      "type": "object",
      "description": "Error information (for failed operations)",
      "properties": {
        "code": { "type": "string" },
        "message": { "type": "string" },
        "details": { "type": "object" }
      }
    }
  },
  "required": ["status"]
}
``` 