# H3 Visualization Techniques

This document presents various approaches and techniques for visualizing H3 data effectively across different platforms and tools, with example implementations and best practices.

## Core Visualization Challenges

H3 visualization has several inherent challenges:

1. **Hexagonal Geometry**: Rendering hexagons requires more computation than rectangles
2. **Large Datasets**: Visualizing millions of H3 cells efficiently
3. **Multi-Resolution Data**: Representing different resolutions simultaneously
4. **Pentagon Handling**: Special cases for the 12 pentagons in the grid system
5. **Projection Distortion**: Maintaining hexagonal appearance in different map projections

## Web-Based Visualization

### Deck.gl

[Deck.gl](https://deck.gl/) from Uber provides specialized layers for H3 visualization that offer exceptional performance for large datasets.

#### H3HexagonLayer

```javascript
import {H3HexagonLayer} from '@deck.gl/geo-layers';

const layer = new H3HexagonLayer({
  id: 'h3-hexagon-layer',
  data: [
    {hex: '89283082837ffff', value: 73},
    {hex: '89283082833ffff', value: 42},
    // More hexagons...
  ],
  pickable: true,
  wireframe: false,
  filled: true,
  extruded: true,
  elevationScale: 20,
  getHexagon: d => d.hex,
  getFillColor: d => [255, (1 - d.value / 100) * 255, 0],
  getElevation: d => d.value,
  onHover: ({object, x, y}) => {
    // Handle hover events
  }
});
```

#### Key Features

- **WebGL Acceleration**: Uses GPU for rendering large H3 datasets
- **Extrusion**: Supports 3D visualization based on data values
- **Interaction**: Built-in hover and click interactions
- **Customization**: Extensive styling options

### Kepler.gl

[Kepler.gl](https://kepler.gl/) provides a user-friendly interface for H3 visualization without requiring coding.

#### Example Configuration

```javascript
const keplerConfig = {
  visState: {
    layers: [{
      id: 'h3-layer',
      type: 'hexagonId',
      config: {
        dataId: 'my_data',
        label: 'H3 Hexagons',
        color: [18, 147, 154],
        columns: {
          hex_id: 'h3_index'
        },
        isVisible: true
      }
    }]
  }
};
```

#### Key Features

- **UI-Based Configuration**: No coding required for basic visualizations
- **Time Series Support**: Animate H3 data over time
- **Export Options**: Share as images or interactive applications
- **Filter Capabilities**: Dynamically filter H3 cells based on attributes

### Leaflet + H3

For lighter-weight applications, Leaflet with a custom H3 plugin provides an efficient solution.

#### Example with leaflet-h3

```javascript
import L from 'leaflet';
import 'leaflet-h3';

const map = L.map('map').setView([37.7749, -122.4194], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add H3 hexagons
const hexagons = [
  {id: '89283082837ffff', value: 73},
  {id: '89283082833ffff', value: 42},
  // More hexagons...
];

hexagons.forEach(hex => {
  const polygon = L.h3.h3ToGeoBoundary(hex.id);
  const color = getColorForValue(hex.value);
  
  L.polygon(polygon, {
    color: '#000',
    weight: 1,
    fillColor: color,
    fillOpacity: 0.7
  }).addTo(map)
    .bindPopup(`Value: ${hex.value}`);
});

function getColorForValue(value) {
  // Return color based on value
  return value > 70 ? '#ff0000' : 
         value > 40 ? '#ffaa00' : 
         '#00ff00';
}
```

#### Key Features

- **Lightweight**: Less resource-intensive than WebGL solutions
- **Compatibility**: Works on most browsers and devices
- **Familiar API**: Uses standard Leaflet patterns
- **Interactivity**: Built-in popup and event handling

### Mapbox GL + H3

Mapbox GL offers high-performance vector rendering suitable for H3 visualization.

```javascript
import mapboxgl from 'mapbox-gl';
import h3 from 'h3-js';

mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/light-v10',
  center: [-122.4194, 37.7749],
  zoom: 11
});

map.on('load', () => {
  // Convert H3 indices to GeoJSON
  const hexagons = [
    {id: '89283082837ffff', value: 73},
    {id: '89283082833ffff', value: 42},
    // More hexagons...
  ];
  
  const features = hexagons.map(hex => {
    const coordinates = h3.h3ToGeoBoundary(hex.id, true);
    return {
      type: 'Feature',
      properties: {
        value: hex.value,
        color: getColorForValue(hex.value)
      },
      geometry: {
        type: 'Polygon',
        coordinates: [coordinates]
      }
    };
  });
  
  map.addSource('h3-hexagons', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: features
    }
  });
  
  map.addLayer({
    id: 'h3-fill',
    type: 'fill',
    source: 'h3-hexagons',
    paint: {
      'fill-color': ['get', 'color'],
      'fill-opacity': 0.7
    }
  });
  
  map.addLayer({
    id: 'h3-outline',
    type: 'line',
    source: 'h3-hexagons',
    paint: {
      'line-color': '#000',
      'line-width': 1
    }
  });
});

function getColorForValue(value) {
  return value > 70 ? '#ff0000' : 
         value > 40 ? '#ffaa00' : 
         '#00ff00';
}
```

#### Key Features

- **Vector Rendering**: High-quality rendering at any zoom level
- **Styling Options**: Extensive control over visual properties
- **Performance**: Efficient rendering of large datasets
- **3D Capabilities**: Support for extrusion and 3D effects

### Observable + H3

[Observable](https://observablehq.com/) notebooks provide an excellent environment for exploratory H3 visualization.

#### Example Observable Cell

```javascript
// Import libraries
h3 = require("h3-js@3.7.2")
d3 = require("d3@6")

// Generate some H3 hexagons
center = h3.geoToH3(37.7749, -122.4194, 9)
hexagons = [center, ...h3.kRing(center, 3)]

// Create SVG
width = 800
height = 600
svg = d3.create("svg")
  .attr("viewBox", [0, 0, width, height])
  .attr("width", width)
  .attr("height", height)

// Project coordinates
projection = d3.geoMercator()
  .center([-122.4194, 37.7749])
  .scale(200000)
  .translate([width / 2, height / 2])

// Draw hexagons
hexagons.forEach(h => {
  let boundary = h3.h3ToGeoBoundary(h, true)
  let path = d3.line()
    .x(d => projection([d[1], d[0]])[0])
    .y(d => projection([d[1], d[0]])[1])
  
  svg.append("path")
    .attr("d", path(boundary))
    .attr("fill", "#69b3a2")
    .attr("stroke", "#000")
    .attr("opacity", 0.7)
})

return svg.node()
```

#### Key Features

- **Interactive Development**: Real-time feedback during visualization creation
- **Sharing**: Easy to share and collaborate
- **Integration**: Combine with other visualizations and analyses
- **Educational Value**: Self-documenting code for learning purposes

## Desktop GIS Integration

### QGIS

QGIS can visualize H3 data through several approaches:

#### Using H3 Plugin

```python
# Example Processing script
from qgis.core import QgsVectorLayer, QgsProject, QgsSymbol, QgsSimpleFillSymbolLayer

# Assuming your data has h3_index and value fields
layer = QgsVectorLayer("path_to_your_data.shp", "H3 Data", "ogr")

# Apply styling
symbol = QgsSymbol.defaultSymbol(layer.geometryType())
symbol_layer = QgsSimpleFillSymbolLayer.create({})
symbol_layer.setStrokeColor(QColor('#000000'))
symbol_layer.setFillColor(QColor('#69b3a2'))
symbol_layer.setStrokeWidth(0.5)
symbol.changeSymbolLayer(0, symbol_layer)

# Apply data-defined color
# This requires field mapping and appropriate expression
# ...

# Add to project
QgsProject.instance().addMapLayer(layer)
```

#### Key Features

- **Desktop Integration**: Use within comprehensive GIS workflows
- **Advanced Styling**: Sophisticated symbology options
- **Analysis Integration**: Combine with other spatial analysis tools
- **Export Options**: Various output formats for publication

### ArcGIS Pro

ArcGIS Pro 3.1+ includes native H3 functionality.

Example Python for ArcGIS:

```python
import arcpy
from arcpy import env

# Set workspace
env.workspace = "C:/data"

# Create H3 hexagons from points
arcpy.h3.PointsToH3("input_points.shp", "output_hexagons", 
                     "value_field", "9", "H3_INDEX")

# Symbolize by value
aprx = arcpy.mp.ArcGISProject("current")
map_obj = aprx.listMaps()[0]
layer = map_obj.listLayers("output_hexagons")[0]

# Apply symbology
sym = layer.symbology
sym.updateRenderer("GraduatedColorsRenderer")
sym.renderer.classificationField = "value_field"
sym.renderer.colorRamp = aprx.listColorRamps("Viridis")[0]
layer.symbology = sym
```

#### Key Features

- **Enterprise Integration**: Fits into organizational GIS infrastructure
- **Cartographic Excellence**: Professional cartographic capabilities
- **Geoprocessing**: Integrated analysis workflows
- **3D Visualization**: Support for 3D extrusion and visualization

## Custom Visualization Approaches

### D3.js Custom Rendering

For maximum control, D3.js offers flexible rendering options.

```javascript
import * as d3 from 'd3';
import * as h3 from 'h3-js';

// Define projection
const projection = d3.geoMercator()
  .center([-122.4194, 37.7749])
  .scale(200000)
  .translate([width / 2, height / 2]);

// Create color scale
const colorScale = d3.scaleLinear()
  .domain([0, 50, 100])
  .range(['#00ff00', '#ffaa00', '#ff0000']);

// Setup SVG
const svg = d3.select('#visualization')
  .append('svg')
  .attr('width', width)
  .attr('height', height);

// Draw hexagons
hexagons.forEach(hex => {
  const boundary = h3.h3ToGeoBoundary(hex.id, true);
  const polygonPath = d3.line()
    .x(d => projection([d[1], d[0]])[0])
    .y(d => projection([d[1], d[0]])[1]);
    
  svg.append('path')
    .attr('d', polygonPath(boundary))
    .attr('fill', colorScale(hex.value))
    .attr('stroke', '#000')
    .attr('stroke-width', 1)
    .attr('opacity', 0.7)
    .on('mouseover', function() {
      d3.select(this)
        .attr('stroke-width', 2)
        .attr('opacity', 1);
    })
    .on('mouseout', function() {
      d3.select(this)
        .attr('stroke-width', 1)
        .attr('opacity', 0.7);
    });
});
```

#### Key Features

- **Complete Control**: Fully customizable visual representation
- **Animation**: Custom transitions and animations
- **Interaction**: Rich interactive capabilities
- **Integration**: Seamless integration with web applications

### WebGL Custom Shaders

For high-performance specialized visualizations, custom WebGL shaders offer maximum efficiency.

```javascript
// Example vertex shader
const vertexShader = `
  attribute vec2 position;
  attribute vec3 color;
  attribute float value;
  
  uniform mat4 projection;
  uniform float elevationScale;
  
  varying vec3 vColor;
  
  void main() {
    vColor = color;
    vec3 pos = vec3(position, value * elevationScale);
    gl_Position = projection * vec4(pos, 1.0);
  }
`;

// Example fragment shader
const fragmentShader = `
  precision mediump float;
  varying vec3 vColor;
  
  void main() {
    gl_FragColor = vec4(vColor, 0.8);
  }
`;

// Shader setup and rendering code would continue...
```

#### Key Features

- **Maximum Performance**: Direct GPU utilization for millions of hexagons
- **Visual Effects**: Special visual effects like glow, animation, and texture
- **Level of Detail**: Dynamic level of detail based on zoom
- **Real-time Updates**: Efficient updates for time-series data

## Multi-Resolution Visualization Techniques

### Compact Representation

Using H3's `compact` and `uncompact` functions to optimize visualization at different zoom levels:

```javascript
import * as h3 from 'h3-js';

// Start with high-resolution hexagons
const highResHexagons = [
  '89283082837ffff', '89283082833ffff', '89283082833bfff',
  '8928308283fffff', '8928308283bffff', '89283082839ffff',
  // Many more hexagons...
];

// Compact to create a mixed-resolution set
const compactedHexagons = h3.compact(highResHexagons);

// Render these instead - much more efficient
// Note that different resolutions need different rendering approaches
```

### Level-of-Detail (LOD) Management

Implementing LOD for H3 visualization:

```javascript
function getAppropriateLOD(zoomLevel) {
  // Map zoom levels to H3 resolutions
  if (zoomLevel > 15) return 10;
  if (zoomLevel > 12) return 9;
  if (zoomLevel > 9) return 8;
  if (zoomLevel > 6) return 7;
  if (zoomLevel > 4) return 5;
  return 3;
}

map.on('zoom', () => {
  const currentZoom = map.getZoom();
  const requiredResolution = getAppropriateLOD(currentZoom);
  
  if (currentResolution !== requiredResolution) {
    currentResolution = requiredResolution;
    updateVisualization(currentResolution);
  }
});

function updateVisualization(resolution) {
  // Either:
  // 1. Use pre-computed data at this resolution
  // 2. Use h3.uncompact and h3.compact to generate appropriate resolution
  // 3. Query backend for data at this resolution
  
  // Then update the visualization layer
}
```

## Special Visualization Use Cases

### Time Series Data

```javascript
// Assuming data structure with timestamped hexagons
const timeSeriesData = {
  '2023-01-01': [
    {hex: '89283082837ffff', value: 73},
    {hex: '89283082833ffff', value: 42},
    // More hexagons...
  ],
  '2023-01-02': [
    {hex: '89283082837ffff', value: 75},
    {hex: '89283082833ffff', value: 45},
    // More hexagons...
  ],
  // More timestamps...
};

// Animation controls
let currentDateIndex = 0;
const dates = Object.keys(timeSeriesData).sort();

function updateToDate(dateStr) {
  const hexagons = timeSeriesData[dateStr];
  // Update visualization with new data
  map.getSource('h3-hexagons').setData({
    type: 'FeatureCollection',
    features: hexagonsToGeoJSON(hexagons)
  });
  
  // Update date display
  document.getElementById('date-display').textContent = dateStr;
}

function animateTimeSeries() {
  const animationInterval = setInterval(() => {
    currentDateIndex = (currentDateIndex + 1) % dates.length;
    updateToDate(dates[currentDateIndex]);
    
    if (currentDateIndex === dates.length - 1) {
      clearInterval(animationInterval);
    }
  }, 1000); // 1 second per frame
}

// Convert hexagons to GeoJSON
function hexagonsToGeoJSON(hexagons) {
  // Implementation as shown in previous examples
}
```

### Flow Visualization

Visualizing flows between H3 cells:

```javascript
// Flow data structure
const flows = [
  {from: '89283082837ffff', to: '89283082833ffff', value: 150},
  {from: '89283082833ffff', to: '8928308283bffff', value: 75},
  // More flows...
];

// Generate flow lines
const flowFeatures = flows.map(flow => {
  const fromCenter = h3.h3ToGeo(flow.from);
  const toCenter = h3.h3ToGeo(flow.to);
  
  // Swap lat/lng for GeoJSON
  return {
    type: 'Feature',
    properties: {
      value: flow.value,
      width: Math.sqrt(flow.value) / 10, // Scale width by flow magnitude
      color: getColorForValue(flow.value)
    },
    geometry: {
      type: 'LineString',
      coordinates: [
        [fromCenter[1], fromCenter[0]],
        [toCenter[1], toCenter[0]]
      ]
    }
  };
});

// Add to map
map.addSource('flow-lines', {
  type: 'geojson',
  data: {
    type: 'FeatureCollection',
    features: flowFeatures
  }
});

map.addLayer({
  id: 'flows',
  type: 'line',
  source: 'flow-lines',
  paint: {
    'line-color': ['get', 'color'],
    'line-width': ['get', 'width'],
    'line-opacity': 0.7
  }
});
```

### Aggregate Statistics

Visualizing aggregate statistics:

```javascript
// Original data with many cells
const detailedData = [/* many H3 cells with values */];

// Create aggregated visualization by H3 parent
const aggregated = {};

detailedData.forEach(cell => {
  // Get parent at resolution 7
  const parent = h3.h3ToParent(cell.hex, 7);
  
  if (!aggregated[parent]) {
    aggregated[parent] = {
      count: 0,
      total: 0,
      min: Infinity,
      max: -Infinity
    };
  }
  
  aggregated[parent].count++;
  aggregated[parent].total += cell.value;
  aggregated[parent].min = Math.min(aggregated[parent].min, cell.value);
  aggregated[parent].max = Math.max(aggregated[parent].max, cell.value);
});

// Convert to array with averages
const aggregatedHexagons = Object.entries(aggregated).map(([hex, stats]) => ({
  hex,
  average: stats.total / stats.count,
  count: stats.count,
  min: stats.min,
  max: stats.max
}));

// Render with appropriate symbology
// e.g., color by average, size/height by count
```

## Best Practices

### Color Selection

1. **Perceptually Uniform Colorscales**: Use colorscales like Viridis, Plasma, or Cividis that maintain perceptual uniformity.

```javascript
// Example with d3 colorscales
const colorScale = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100]);
```

2. **Diverging Scales**: For data with a meaningful center point or when showing deviation.

```javascript
const divergingScale = d3.scaleDiverging()
  .domain([-100, 0, 100])
  .interpolator(d3.interpolateRdBu);
```

3. **Categorical Maps**: For discrete categories, use colorblind-friendly palettes.

```javascript
const categoricalScale = d3.scaleOrdinal()
  .domain(['A', 'B', 'C', 'D'])
  .range(['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']);
```

### Visual Hierarchy

1. **Resolution Indication**: Visually indicate the resolution of hexagons.

```javascript
// Set border width based on resolution
function getBorderWidth(h3Index) {
  const res = h3.getResolution(h3Index);
  return res < 7 ? 2 : 1;
}
```

2. **Focus Area Highlighting**: Highlight relevant hexagons while de-emphasizing others.

```javascript
// Set opacity based on relevance
hexagons.forEach(hex => {
  const opacity = isRelevant(hex.id) ? 0.9 : 0.3;
  // Apply to visualization
});
```

### Performance Optimization

1. **Clustering**: Cluster small neighboring hexagons at lower zoom levels.

```javascript
function clusterHexagons(hexagons, threshold) {
  // Implementation of clustering algorithm
  // Return fewer, aggregate hexagons
}
```

2. **Data Culling**: Only render hexagons within the current viewport plus a buffer.

```javascript
function getVisibleHexagons(bounds, hexagons) {
  return hexagons.filter(hex => {
    const center = h3.h3ToGeo(hex.id);
    return bounds.contains([center[0], center[1]]);
  });
}
```

3. **Level of Detail (LOD)**: Adjust resolution based on zoom level.

```javascript
// See LOD example above
```

4. **Web Workers**: Offload computation to background threads.

```javascript
// In main thread
const worker = new Worker('h3-worker.js');

worker.postMessage({
  action: 'generateHexagons',
  bounds: mapBounds,
  resolution: 9
});

worker.onmessage = function(e) {
  // Update visualization with e.data.hexagons
};

// In h3-worker.js
importScripts('h3-js.js');

self.onmessage = function(e) {
  if (e.data.action === 'generateHexagons') {
    // Compute hexagons
    const hexagons = computeHexagons(e.data.bounds, e.data.resolution);
    self.postMessage({hexagons});
  }
};
```

## Accessibility Considerations

1. **Color Blindness**: Ensure visualizations work for color blind users.

```javascript
// Use colorblind-friendly palettes
const accessibleColors = [
  '#1b9e77', '#d95f02', '#7570b3', '#e7298a',
  '#66a61e', '#e6ab02', '#a6761d', '#666666'
];
```

2. **Contrast**: Maintain sufficient contrast for borders and text.

```javascript
// Ensure border contrast
const borderColor = isDarkMode ? '#ffffff' : '#000000';
const textColor = isDarkMode ? '#ffffff' : '#000000';
```

3. **Text Labels**: Include text labels for important hexagons.

```javascript
// Add text labels to significant hexagons
significantHexagons.forEach(hex => {
  const center = projection(h3.h3ToGeo(hex.id).reverse());
  
  svg.append('text')
    .attr('x', center[0])
    .attr('y', center[1])
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .text(hex.label)
    .attr('fill', getContrastColor(hex.color));
});
```

## Conclusion

H3 visualization techniques span a wide range of approaches, from high-performance WebGL rendering to traditional GIS integration. The choice of technique depends on:

1. **Dataset Size**: From thousands to millions of hexagons
2. **Performance Requirements**: Static visualization vs. real-time updates
3. **Interactivity Needs**: Simple tooltips vs. complex interactions
4. **Platform Constraints**: Web, desktop, or mobile deployment
5. **User Expertise**: Developer-centric vs. analyst-friendly tools

By choosing the appropriate technique and following the best practices outlined above, developers can create effective, efficient, and accessible H3 visualizations.

## References

1. [H3 Documentation - Visualization](https://h3geo.org/docs/highlights/visualization)
2. [Deck.gl H3 Layers](https://deck.gl/docs/api-reference/geo-layers/h3-layers)
3. [Observable H3 Notebooks](https://observablehq.com/collection/@nrabinowitz/h3-tutorials)
4. [CARTO - H3 Best Practices](https://carto.com/blog/spatial-indexes-spatial-analytics-h3/)
5. [Color Brewer - Colorblind-Safe Palettes](https://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3)
6. [Uber Engineering Blog: Visualization](https://eng.uber.com/movement-visualization/) 