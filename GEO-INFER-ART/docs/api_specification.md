# GEO-INFER-ART API Specification

This document provides a comprehensive overview of the public interfaces for each major component in the GEO-INFER-ART module.

## Table of Contents

- [GeoArt](#geoart)
- [ColorPalette](#colorpalette)
- [StyleTransfer](#styletransfer)
- [GenerativeMap](#generativemap)
- [ProceduralArt](#proceduralart)
- [PlaceArt](#placeart)
- [CulturalMap](#culturalmap)

## GeoArt

The `GeoArt` class provides methods for loading, transforming, and visualizing geospatial data with artistic elements.

### Constructor

```python
GeoArt(data=None, metadata=None, crs="EPSG:4326")
```

**Parameters:**
- `data` (GeoDataFrame or numpy.ndarray, optional): Geospatial data
- `metadata` (dict, optional): Additional information about the data
- `crs` (str, optional): Coordinate reference system identifier

### Methods

#### `load_geojson`

```python
@classmethod
def load_geojson(cls, file_path)
```

Loads geospatial data from a GeoJSON file.

**Parameters:**
- `file_path` (str): Path to the GeoJSON file

**Returns:**
- `GeoArt`: New GeoArt object with loaded data

#### `load_raster`

```python
@classmethod
def load_raster(cls, file_path)
```

Loads geospatial data from a raster file (e.g., GeoTIFF).

**Parameters:**
- `file_path` (str): Path to the raster file

**Returns:**
- `GeoArt`: New GeoArt object with loaded data

#### `apply_style`

```python
def apply_style(self, style="default", color_palette=None, line_width=1.0, alpha=0.8, background_color="white")
```

Applies an artistic style to the geospatial data.

**Parameters:**
- `style` (str): Name of the style to apply ('default', 'watercolor', 'minimal', 'blueprint')
- `color_palette` (str or ColorPalette): Color palette to use
- `line_width` (float): Width of lines for vector data
- `alpha` (float): Transparency level (0.0 to 1.0)
- `background_color` (str): Background color of the visualization

**Returns:**
- `self`: For method chaining

#### `save`

```python
def save(self, file_path, dpi=300)
```

Saves the visualization to a file.

**Parameters:**
- `file_path` (str): Output file path
- `dpi` (int): Resolution in dots per inch

**Returns:**
- `str`: File path of the saved image

#### `show`

```python
def show(self)
```

Displays the visualization using matplotlib.

## ColorPalette

The `ColorPalette` class manages color schemes for maps and visualizations.

### Constructor

```python
ColorPalette(name="viridis", colors=None, n_colors=256)
```

**Parameters:**
- `name` (str): Name of the palette
- `colors` (list, optional): List of color codes (hex, RGB, or named)
- `n_colors` (int): Number of colors to generate in the colormap

### Methods

#### `get_palette`

```python
@classmethod
def get_palette(cls, name)
```

Get a predefined color palette by name.

**Parameters:**
- `name` (str): Name of the predefined palette

**Returns:**
- `ColorPalette`: A ColorPalette object with the requested palette

#### `from_color_theory`

```python
@classmethod
def from_color_theory(cls, base_color, scheme="complementary", n_colors=6)
```

Create a palette based on color theory relationships.

**Parameters:**
- `base_color` (str): The base color to build the palette from
- `scheme` (str): The color scheme to use ('complementary', 'analogous', 'triadic', 'monochromatic')
- `n_colors` (int): Number of colors to generate

**Returns:**
- `ColorPalette`: A new ColorPalette object

#### `from_image`

```python
@classmethod
def from_image(cls, image_path, n_colors=6)
```

Extract a color palette from an image.

**Parameters:**
- `image_path` (str): Path to the image file
- `n_colors` (int): Number of colors to extract

**Returns:**
- `ColorPalette`: A new ColorPalette with colors extracted from the image

#### `invert`

```python
def invert(self)
```

Creates an inverted version of the color palette.

**Returns:**
- `ColorPalette`: A new ColorPalette with inverted colors

#### `show`

```python
def show(self, figsize=(10, 2))
```

Displays a visualization of the color palette.

**Parameters:**
- `figsize` (tuple): Figure size in inches

## StyleTransfer

The `StyleTransfer` class applies artistic styles to geospatial visualizations.

### Constructor

```python
StyleTransfer(style_image=None, content_image=None)
```

**Parameters:**
- `style_image` (str, numpy.ndarray, or PIL.Image, optional): Style image
- `content_image` (str, numpy.ndarray, or PIL.Image, optional): Content image

### Methods

#### `apply`

```python
@classmethod
def apply(cls, geo_data, style, content_image=None, iterations=1000, style_weight=1e-2, content_weight=1e4)
```

Apply style transfer to geospatial data.

**Parameters:**
- `geo_data` (GeoDataFrame): Geospatial data to stylize
- `style` (str or PIL.Image): Style name or image
- `content_image` (str or PIL.Image, optional): Content image
- `iterations` (int): Number of optimization iterations
- `style_weight` (float): Weight of style loss
- `content_weight` (float): Weight of content loss

**Returns:**
- `PIL.Image`: Stylized image

#### `load_style_image`

```python
def load_style_image(self, image)
```

Load a style image from various formats.

**Parameters:**
- `image` (str or numpy.ndarray or PIL.Image): Style image

#### `get_predefined_style_path`

```python
@classmethod
def get_predefined_style_path(cls, style_name)
```

Get the file path for a predefined style.

**Parameters:**
- `style_name` (str): Name of the predefined style

**Returns:**
- `str`: Path to the style image file

## GenerativeMap

The `GenerativeMap` class creates generative art from elevation data.

### Constructor

```python
GenerativeMap(data=None, metadata=None)
```

**Parameters:**
- `data` (numpy.ndarray, optional): Elevation data as a numpy array
- `metadata` (dict, optional): Additional information about the data

### Methods

#### `from_elevation`

```python
@classmethod
def from_elevation(cls, region, resolution=512, abstraction_level=0.5, style="contour")
```

Create a generative map from elevation data.

**Parameters:**
- `region` (str or tuple or numpy.ndarray): Named region, bounding box, or array
- `resolution` (int): Output resolution
- `abstraction_level` (float): Level of abstraction (0.0 to 1.0)
- `style` (str): Visualization style ('contour', 'flow', 'particles', 'contour_flow')

**Returns:**
- `GenerativeMap`: A new GenerativeMap object

#### `save`

```python
def save(self, file_path)
```

Save the generative map to a file.

**Parameters:**
- `file_path` (str): Output file path

**Returns:**
- `str`: Path to the saved file

#### `show`

```python
def show(self)
```

Display the generative map.

## ProceduralArt

The `ProceduralArt` class generates procedural art based on geographic features.

### Constructor

```python
ProceduralArt(algorithm="noise_field", params=None, resolution=(800, 800))
```

**Parameters:**
- `algorithm` (str): Procedural algorithm to use
- `params` (dict, optional): Parameters for the algorithm
- `resolution` (tuple): Output resolution (width, height)

### Methods

#### `from_geo_coordinates`

```python
@classmethod
def from_geo_coordinates(cls, lat, lon, algorithm="noise_field", additional_params=None, resolution=(800, 800))
```

Create procedural art from geographic coordinates.

**Parameters:**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)
- `algorithm` (str): Procedural algorithm to use
- `additional_params` (dict, optional): Additional parameters for the algorithm
- `resolution` (tuple): Output resolution (width, height)

**Returns:**
- `ProceduralArt`: A new ProceduralArt object

#### `from_geo_features`

```python
@classmethod
def from_geo_features(cls, feature_type, feature_count=1, algorithm="l_system", additional_params=None, resolution=(800, 800))
```

Create procedural art from geographic features.

**Parameters:**
- `feature_type` (str): Type of geographic feature ('rivers', 'mountains', 'coastlines')
- `feature_count` (int): Number of features to include
- `algorithm` (str): Procedural algorithm to use
- `additional_params` (dict, optional): Additional parameters for the algorithm
- `resolution` (tuple): Output resolution (width, height)

**Returns:**
- `ProceduralArt`: A new ProceduralArt object

#### `generate`

```python
def generate(self)
```

Generate the procedural art image.

**Returns:**
- `self`: For method chaining

#### `save`

```python
def save(self, file_path)
```

Save the procedural art to a file.

**Parameters:**
- `file_path` (str): Output file path

**Returns:**
- `str`: Path to the saved file

#### `show`

```python
def show(self)
```

Display the procedural art.

## PlaceArt

The `PlaceArt` class creates art based on specific locations.

### Constructor

```python
PlaceArt(location=None, data=None, image=None)
```

**Parameters:**
- `location` (dict, optional): Location information
- `data` (GeoDataFrame, optional): Geospatial data for the location
- `image` (PIL.Image, optional): Generated image

### Methods

#### `from_coordinates`

```python
@classmethod
def from_coordinates(cls, lat, lon, name=None, radius_km=10.0, style="abstract", include_data=False)
```

Create place art from geographic coordinates.

**Parameters:**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)
- `name` (str, optional): Name for the location
- `radius_km` (float): Radius around the coordinates to include
- `style` (str): Art style ('abstract', 'topographic', 'cultural', 'mixed_media')
- `include_data` (bool): Whether to include full geospatial data

**Returns:**
- `PlaceArt`: A new PlaceArt object

#### `from_place_name`

```python
@classmethod
def from_place_name(cls, place_name, style="abstract", include_data=False)
```

Create place art from a place name.

**Parameters:**
- `place_name` (str): Name of the place
- `style` (str): Art style ('abstract', 'topographic', 'cultural', 'mixed_media')
- `include_data` (bool): Whether to include full geospatial data

**Returns:**
- `PlaceArt`: A new PlaceArt object

#### `add_metadata_overlay`

```python
def add_metadata_overlay(self, position="bottom", opacity=0.7)
```

Add location metadata as an overlay on the image.

**Parameters:**
- `position` (str): Position of the overlay ('top', 'bottom', 'left', 'right')
- `opacity` (float): Opacity of the overlay (0.0 to 1.0)

**Returns:**
- `self`: For method chaining

#### `save`

```python
def save(self, file_path)
```

Save the place art to a file.

**Parameters:**
- `file_path` (str): Output file path

**Returns:**
- `str`: Path to the saved file

#### `show`

```python
def show(self)
```

Display the place art.

## CulturalMap

The `CulturalMap` class creates maps with cultural and historical context.

### Constructor

```python
CulturalMap(data=None, metadata=None, image=None)
```

**Parameters:**
- `data` (GeoDataFrame, optional): Geospatial data with cultural features
- `metadata` (dict, optional): Cultural and contextual metadata
- `image` (PIL.Image, optional): Generated image

### Methods

#### `from_region`

```python
@classmethod
def from_region(cls, region_name, cultural_theme="historical", style="artistic")
```

Create a cultural map from a region name.

**Parameters:**
- `region_name` (str): Name of the geographic region
- `cultural_theme` (str): Cultural theme ('historical', 'linguistic', etc.)
- `style` (str): Visual style ('artistic', 'minimalist', 'detailed', 'abstract')

**Returns:**
- `CulturalMap`: A new CulturalMap object

#### `from_coordinates`

```python
@classmethod
def from_coordinates(cls, lat, lon, radius_km=100.0, cultural_theme="historical", style="artistic")
```

Create a cultural map from geographic coordinates.

**Parameters:**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)
- `radius_km` (float): Radius around the coordinates to include
- `cultural_theme` (str): Cultural theme ('historical', 'linguistic', etc.)
- `style` (str): Visual style ('artistic', 'minimalist', 'detailed', 'abstract')

**Returns:**
- `CulturalMap`: A new CulturalMap object

#### `add_narrative`

```python
def add_narrative(self, narrative, position="bottom")
```

Add a narrative description to the cultural map.

**Parameters:**
- `narrative` (str): Text narrative to add
- `position` (str): Position of the narrative ('top', 'bottom', 'left', 'right')

**Returns:**
- `self`: For method chaining

#### `apply_cultural_style`

```python
def apply_cultural_style(self, style="artistic")
```

Apply a cultural style to the map.

**Parameters:**
- `style` (str): Visual style ('artistic', 'minimalist', 'detailed', 'abstract')

**Returns:**
- `self`: For method chaining

#### `save`

```python
def save(self, file_path)
```

Save the cultural map to a file.

**Parameters:**
- `file_path` (str): Output file path

**Returns:**
- `str`: Path to the saved file

#### `show`

```python
def show(self)
```

Display the cultural map. 