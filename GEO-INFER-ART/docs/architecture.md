# GEO-INFER-ART Architecture

This document provides an overview of the GEO-INFER-ART module architecture, component relationships, and data flow.

## Component Structure

The GEO-INFER-ART module is organized into the following core components:

```mermaid
classDiagram
    class GeoArt {
        +data: GeoDataFrame
        +metadata: Dict
        +load_geojson()
        +load_raster()
        +apply_style()
        +save()
        +show()
    }

    class ColorPalette {
        +name: str
        +colors: List[str]
        +cmap: LinearSegmentedColormap
        +get_palette()
        +from_color_theory()
        +from_image()
        +invert()
        +show()
    }

    class StyleTransfer {
        +style_image: np.ndarray
        +content_image: np.ndarray
        +apply()
        +load_style_image()
        +get_predefined_style_path()
    }

    class GenerativeMap {
        +data: np.ndarray
        +image: PIL.Image
        +metadata: Dict
        +from_elevation()
        +save()
        +show()
    }

    class ProceduralArt {
        +algorithm: str
        +params: Dict
        +image: PIL.Image
        +from_geo_coordinates()
        +from_geo_features()
        +generate()
        +save()
        +show()
    }

    class PlaceArt {
        +location: Dict
        +data: GeoDataFrame
        +image: PIL.Image
        +from_coordinates()
        +from_place_name()
        +add_metadata_overlay()
        +save()
        +show()
    }

    class CulturalMap {
        +data: GeoDataFrame
        +metadata: Dict
        +image: PIL.Image
        +from_region()
        +from_coordinates()
        +add_narrative()
        +apply_cultural_style()
        +save()
        +show()
    }

    GeoArt --> ColorPalette: uses
    StyleTransfer --> GeoArt: applies to
    StyleTransfer --> ColorPalette: uses
    GenerativeMap --> ColorPalette: uses
    ProceduralArt --> ColorPalette: uses
    PlaceArt --> ColorPalette: uses
    CulturalMap --> ColorPalette: uses
    PlaceArt --> GenerativeMap: uses for terrain
```

## Module Structure

The overall module structure is organized as follows:

```mermaid
graph TD
    subgraph geo_infer_art
        API[api/]
        Core[core/]
        Models[models/]
        Utils[utils/]
    end

    subgraph Core
        Viz[visualization/]
        Gen[generation/]
        Aes[aesthetics/]
        Place[place/]
    end

    subgraph Viz
        GeoArt[geo_art.py]
    end

    subgraph Aes
        ColorPalette[color_palette.py]
        StyleTransfer[style_transfer.py]
    end

    subgraph Gen
        GenerativeMap[generative_map.py]
        ProceduralArt[procedural_art.py]
    end

    subgraph Place
        PlaceArt[place_art.py]
        CulturalMap[cultural_map.py]
    end

    subgraph Utils
        Validators[validators.py]
    end

    Core --> API
    Viz --> Core
    Aes --> Core
    Gen --> Core
    Place --> Core
    Utils --> Core
    Models --> Core
```

## Data Flow

The following diagram illustrates the typical data flow through the GEO-INFER-ART components:

```mermaid
flowchart TD
    GeoData[(Geospatial Data)] --> GeoArt
    GeoArt --> Viz[Visualization]
    
    StyleImg[(Style Image)] --> StyleTransfer
    GeoArt --> StyleTransfer
    StyleTransfer --> StyledImg[Styled Visualization]
    
    ElevationData[(Elevation Data)] --> GenerativeMap
    GenerativeMap --> GenImg[Generative Image]
    
    Coordinates[(Geographic Coordinates)] --> ProceduralArt
    ProceduralArt --> ProcImg[Procedural Art]
    
    Location[(Location Data)] --> PlaceArt
    PlaceArt --> PlaceImg[Place-Based Art]
    
    RegionData[(Region & Cultural Data)] --> CulturalMap
    CulturalMap --> CultureImg[Cultural Map]
```

## Component Interactions

The interactions between different components in the system:

```mermaid
sequenceDiagram
    participant User
    participant GeoArt
    participant StyleTransfer
    participant ColorPalette
    
    User->>GeoArt: load_geojson(file_path)
    GeoArt-->>User: GeoArt object
    
    User->>GeoArt: apply_style(style="watercolor")
    GeoArt->>ColorPalette: get_palette("earth")
    ColorPalette-->>GeoArt: ColorPalette object
    GeoArt-->>User: Styled GeoArt object
    
    User->>StyleTransfer: apply(geo_data, style="watercolor")
    StyleTransfer->>StyleTransfer: get_predefined_style_path("watercolor")
    StyleTransfer->>StyleTransfer: load_style_image(style_path)
    StyleTransfer-->>User: Styled PIL.Image
```

## Implementation Details

### Core Components

- **GeoArt**: Responsible for loading, visualizing, and styling geospatial data (vector and raster).
- **ColorPalette**: Manages color schemes based on predefined palettes, color theory, or extracted from images.
- **StyleTransfer**: Applies artistic styles to geospatial visualizations using neural style transfer.
- **GenerativeMap**: Creates artistic visualizations from elevation data with various styles.
- **ProceduralArt**: Generates procedural art using geographic coordinates or features as seeds.
- **PlaceArt**: Creates art based on specific locations and their characteristics.
- **CulturalMap**: Integrates cultural and historical contexts into artistic map representations.

### Utility Components

- **validators.py**: Provides input validation functions for file paths, geospatial data, coordinates, etc.

## External Dependencies

- **geopandas**: Handling geospatial vector data
- **numpy**: Numerical operations and array handling
- **matplotlib**: Visualization and color management
- **PIL/Pillow**: Image processing
- **tensorflow**: Neural style transfer implementation
- **rasterio**: Handling geospatial raster data
- **scipy**: Various scientific computing utilities
- **scikit-image**: Image processing algorithms 