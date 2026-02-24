# GEO-INFER-ART API Specification

## Core Classes

### CartographicDesigner

```python
class CartographicDesigner:
    """Create beautiful cartographic maps."""
    
    def __init__(self, style: str = "default"):
        """
        Initialize designer with style.
        
        Args:
            style: Style preset name
        """
    
    def create(
        self,
        data: GeoDataFrame,
        style: str = None,
        colors: str = "earth_tones",
        **kwargs
    ) -> MapImage:
        """
        Create styled map from data.
        
        Args:
            data: Input geospatial data
            style: Override style
            colors: Color palette name
            
        Returns:
            MapImage object
        """
```

### GeoVisualizer

```python
class GeoVisualizer:
    """3D and animated visualizations."""
    
    def render_3d(
        self,
        dem: Raster,
        texture: Raster = None,
        exaggeration: float = 1.0
    ) -> Scene3D:
        """Render 3D terrain."""
    
    def animate(
        self,
        data: TemporalDataset,
        fps: int = 30,
        duration: float = None
    ) -> Animation:
        """Create animated visualization."""
```

### GenerativeArtist

```python
class GenerativeArtist:
    """Algorithmic art generation."""
    
    def generate(
        self,
        source: GeoDataFrame,
        style: str = "abstract",
        randomness: float = 0.5,
        seed: int = None
    ) -> Artwork:
        """Generate art from geo data."""
```

## Style Presets

| Preset | Description |
|--------|-------------|
| `watercolor` | Soft, artistic effect |
| `minimalist` | Clean, simple lines |
| `vintage` | Retro cartography |
| `neon` | Bright, glowing |
| `blueprint` | Technical drawing |

## Color Palettes

| Palette | Colors |
|---------|--------|
| `earth_tones` | Browns, greens, blues |
| `ocean` | Blues, teals |
| `sunset` | Oranges, pinks, purples |
| `monochrome` | Grayscale variations |

---

**Last Updated**: 2026-02-24
