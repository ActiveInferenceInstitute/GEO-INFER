# GEO-INFER-ART User Guide

## Introduction

GEO-INFER-ART is a specialized Python module for creating artistic visualizations of geospatial data. This library enables users to transform geographic information into visually compelling artistic expressions, apply aesthetic styles to maps, generate procedural art based on geographic features, and create place-based artistic representations.

This user guide provides comprehensive instructions for working with the GEO-INFER-ART module.

## Installation

### Prerequisites

GEO-INFER-ART requires Python 3.9 or later and depends on several packages:

- numpy
- matplotlib
- geopandas
- rasterio
- pillow
- scipy
- colour
- scikit-image

For neural style transfer functionality, TensorFlow is required:

- tensorflow (optional)

### Install from PyPI

```bash
pip install geo-infer-art
```

### Install from Source

```bash
git clone https://github.com/activeinference/GEO-INFER.git
cd GEO-INFER/GEO-INFER-ART
pip install -e .
```

## Core Components

### GeoArt

The `GeoArt` class provides methods for creating artistic visualizations of geospatial data, including both vector and raster formats.

#### Loading Data

```python
from geo_infer_art import GeoArt

# Load from GeoJSON
geo_art = GeoArt.load_geojson("path/to/data.geojson")

# Load from raster
geo_art = GeoArt.load_raster("path/to/data.tif")

# Create from existing data
import geopandas as gpd
gdf = gpd.read_file("path/to/data.shp")
geo_art = GeoArt(data=gdf)
```

#### Applying Styles

```python
# Apply default style
geo_art.apply_style()

# Apply watercolor style with autumn color palette
geo_art.apply_style(
    style="watercolor", 
    color_palette="autumn"
)

# Apply minimal style with custom parameters
geo_art.apply_style(
    style="minimal",
    line_width=2.0,
    alpha=0.7,
    background_color="#f0f0f0"
)
```

Available styles:
- `"default"`: Standard visualization
- `"watercolor"`: Soft, artistic watercolor effect
- `"topographic"`: Emphasis on terrain features
- `"neon"`: Bright, high-contrast colors
- `"minimal"`: Clean, simplified presentation
- `"blueprint"`: Technical, blueprint-style presentation

#### Saving and Displaying

```python
# Save to file
geo_art.save("output/artistic_map.png", dpi=300)

# Display in a notebook or interactive environment
geo_art.show()
```

### ColorPalette

The `ColorPalette` class provides tools for creating and managing color schemes for geospatial visualizations.

#### Using Predefined Palettes

```python
from geo_infer_art import ColorPalette

# Get a predefined palette
palette = ColorPalette.get_palette("sunset")

# Use in GeoArt
geo_art.apply_style(color_palette=palette)
```

Available predefined palettes:
- `"viridis"`: Purple to yellow gradient (default)
- `"pastel"`: Soft pastel colors
- `"earth"`: Natural earth tones
- `"bright"`: Vibrant, high-saturation colors
- `"grayscale"`: Black to white gradient
- `"blue"`: Blue-focused gradient
- `"autumn"`: Warm autumn colors
- `"sunset"`: Sunset-inspired colors
- `"ocean"`: Ocean-inspired blue and green tones
- `"forest"`: Forest-inspired green gradient

#### Creating Custom Palettes

```python
# From color theory
palette = ColorPalette.from_color_theory(
    base_color="#1a5276",  # Deep blue
    scheme="complementary",
    n_colors=6
)

# From an image
palette = ColorPalette.from_image(
    image_path="path/to/image.jpg",
    n_colors=8
)

# Inverting a palette
inverted = palette.invert()

# Visualize a palette
palette.show()
```

Available color schemes:
- `"complementary"`: Colors opposite on the color wheel
- `"analogous"`: Colors adjacent on the color wheel
- `"triadic"`: Three colors evenly spaced around the color wheel
- `"monochromatic"`: Variations of a single hue

### StyleTransfer

The `StyleTransfer` class applies neural style transfer to geospatial visualizations, allowing maps to adopt the artistic style of a reference image.

```python
from geo_infer_art import StyleTransfer, GeoArt

# Load geospatial data
geo_data = GeoArt.load_geojson("path/to/data.geojson")

# Apply style transfer
styled_image = StyleTransfer.apply(
    geo_data=geo_data,
    style="watercolor",  # Predefined style
    iterations=100,
    color_palette="autumn"
)

# Save the result
styled_image.save("output/styled_map.png")

# Alternatively, use a custom style image
styled_image = StyleTransfer.apply(
    geo_data=geo_data,
    style_image="path/to/style_image.jpg",
    content_weight=1e4,
    style_weight=1e-2
)
```

Available predefined styles:
- `"watercolor"`: Watercolor painting effect
- `"oil_painting"`: Oil painting texture
- `"sketch"`: Pencil sketch style
- `"abstract"`: Abstract geometric style
- `"impressionist"`: Impressionist painting style
- `"ukiyo_e"`: Japanese ukiyo-e style

### GenerativeMap

The `GenerativeMap` class creates generative art based on geographic features, particularly elevation data.

```python
from geo_infer_art import GenerativeMap

# Generate art from a named region
terrain_art = GenerativeMap.from_elevation(
    region="grand_canyon",
    resolution=512,
    abstraction_level=0.7,
    style="contour_flow"
)

# Generate art from custom coordinates (bounding box)
# (min_lon, min_lat, max_lon, max_lat)
bbox_art = GenerativeMap.from_elevation(
    region=(-112.4, 36.0, -111.9, 36.5),  # Grand Canyon area
    resolution=800,
    abstraction_level=0.3,
    style="flow"
)

# Save the result
terrain_art.save("output/terrain_art.png")
```

Available styles:
- `"contour"`: Contour lines visualization
- `"flow"`: Flow field visualization
- `"particles"`: Particle-based visualization
- `"contour_flow"`: Combined contour and flow visualization

### ProceduralArt

The `ProceduralArt` class generates art through rule-based algorithms that can be seeded with geospatial parameters.

```python
from geo_infer_art import ProceduralArt

# Generate from coordinates
art = ProceduralArt.from_geo_coordinates(
    lat=40.7128,
    lon=-74.0060,  # New York City
    algorithm="noise_field",
    additional_params={
        "color_palette": "sunset",
        "octaves": 8
    }
)

# Generate from geographic features
art = ProceduralArt.from_geo_features(
    feature_type="rivers",
    feature_count=5,
    algorithm="l_system",
    additional_params={
        "color_palette": "blue"
    }
)

# Custom generation
art = ProceduralArt(
    algorithm="fractal_tree",
    params={
        "depth": 9,
        "branch_angle": 20,
        "color_palette": "forest"
    }
)
art.generate()

# Save the result
art.save("output/procedural_art.png")
```

Available algorithms:
- `"l_system"`: Lindenmayer system for fractal patterns
- `"cellular_automata"`: Rule-based grid evolution
- `"reaction_diffusion"`: Chemical reaction simulation
- `"noise_field"`: Perlin or Simplex noise-based patterns
- `"voronoi"`: Voronoi diagram patterns
- `"fractal_tree"`: Recursive tree-like structures

### PlaceArt

The `PlaceArt` class creates art based on the unique characteristics of geographic locations.

```python
from geo_infer_art import PlaceArt

# Generate from coordinates
art = PlaceArt.from_coordinates(
    lat=48.8566,
    lon=2.3522,  # Paris
    name="Paris",
    style="abstract"
)

# Generate from place name
art = PlaceArt.from_place_name(
    place_name="tokyo",
    style="topographic"
)

# Add location metadata overlay
art.add_metadata_overlay(position="bottom", opacity=0.7)

# Save the result
art.save("output/place_art.png")
```

Available styles:
- `"abstract"`: Abstract representation
- `"topographic"`: Terrain-focused representation
- `"cultural"`: Culture-inspired patterns
- `"mixed_media"`: Combination of multiple styles

### CulturalMap

The `CulturalMap` class creates maps that integrate cultural and historical contexts of places.

```python
from geo_infer_art import CulturalMap

# Create from region name
cultural_map = CulturalMap.from_region(
    region_name="mediterranean",
    cultural_theme="historical",
    style="artistic"
)

# Create from coordinates
cultural_map = CulturalMap.from_coordinates(
    lat=41.9028,
    lon=12.4964,  # Rome
    radius_km=200,
    cultural_theme="historical"
)

# Add narrative text
cultural_map.add_narrative(
    "The Mediterranean region has been a cradle of civilization, " 
    "with numerous ancient cultures developing along its shores."
)

# Apply styling
cultural_map.apply_cultural_style()

# Save the result
cultural_map.save("output/cultural_map.png")
```

Available cultural themes:
- `"historical"`: Historical sites and periods
- `"linguistic"`: Language distribution and families

## Advanced Usage

### Combining Multiple Components

The different components of GEO-INFER-ART can be combined to create complex artistic representations:

```python
from geo_infer_art import GeoArt, StyleTransfer, GenerativeMap, PlaceArt

# 1. Start with geospatial data
geo_art = GeoArt.load_geojson("path/to/data.geojson")
geo_art.apply_style(style="watercolor", color_palette="ocean")

# 2. Convert to image
import io
from PIL import Image
buf = io.BytesIO()
geo_art._figure.savefig(buf, format='png', dpi=300)
buf.seek(0)
base_image = Image.open(buf)

# 3. Apply style transfer
styled_image = StyleTransfer.apply(
    geo_data=None,  # Using existing image
    style="ukiyo_e",
    content_image=base_image
)

# 4. Save the final result
styled_image.save("output/combined_art.png")
```

### Creating Custom Styles

You can create custom visualization styles by combining different parameters:

```python
# Custom style with transparent background and specific color mapping
geo_art.apply_style(
    color_palette=ColorPalette.from_color_theory("#3498db", "monochromatic"),
    line_width=0.8,
    alpha=0.9,
    background_color="none"  # Transparent background
)
```

### Working with Large Datasets

For large geospatial datasets, consider these optimization strategies:

```python
# Simplify geometries before visualization
import geopandas as gpd
gdf = gpd.read_file("path/to/large_data.geojson")
simplified_gdf = gdf.simplify(tolerance=0.001)
geo_art = GeoArt(data=simplified_gdf)

# Reduce style transfer iterations for faster processing
styled_image = StyleTransfer.apply(
    geo_data=geo_art.data,
    style="watercolor",
    iterations=50,  # Reduced from default 100
)
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**

   Error: `ImportError: No module named 'tensorflow'`

   Solution: Install TensorFlow for style transfer functionality:
   ```bash
   pip install tensorflow
   ```

2. **Memory issues with large datasets**

   Error: `MemoryError` or application crashes

   Solution: Simplify geometries or reduce resolution:
   ```python
   # Simplify geometries
   simplified_gdf = gdf.simplify(tolerance=0.001)
   
   # Reduce resolution for raster data
   gen_map = GenerativeMap.from_elevation(
       region=bbox,
       resolution=256  # Lower resolution
   )
   ```

3. **Style transfer not working**

   Issue: Style transfer has no effect or produces unexpected results

   Solution: Adjust style and content weights:
   ```python
   styled_image = StyleTransfer.apply(
       geo_data=geo_data,
       style="watercolor",
       style_weight=1e-1,  # Increased from default
       content_weight=1e3,  # Decreased from default
   )
   ```

## Reference

### File Formats

GEO-INFER-ART supports the following file formats:

- **Vector data**: GeoJSON (.geojson, .json), Shapefile (.shp)
- **Raster data**: GeoTIFF (.tif, .tiff), JPEG (.jpg), PNG (.png)
- **Style images**: JPEG (.jpg), PNG (.png)

### Coordinate Systems

By default, GEO-INFER-ART uses the WGS84 coordinate reference system (EPSG:4326) for geographic data. Other coordinate systems are supported but may require explicit conversion.

### Command-Line Interface

GEO-INFER-ART includes a basic command-line interface for simple operations:

```bash
# Generate art from GeoJSON file
python -m geo_infer_art.cli --input data.geojson --style watercolor --output map_art.png

# Generate place-based art
python -m geo_infer_art.cli --place "Paris" --style abstract --output paris_art.png

# Apply style transfer
python -m geo_infer_art.cli --input data.geojson --style-transfer ukiyo_e --output styled_map.png
```

Run `python -m geo_infer_art.cli --help` for full documentation of the command-line options. 