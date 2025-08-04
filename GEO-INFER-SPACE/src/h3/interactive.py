#!/usr/bin/env python3
"""
H3 Interactive Module

Provides interactive visualization capabilities for H3 geospatial data.
Generates HTML dashboards, web maps, and interactive plots using folium, plotly, and other libraries.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import json
import html
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    get_resolution, is_valid_cell
)

from conversion import (
    cells_to_geojson, cells_to_csv
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics
)

from constants import (
    MAX_H3_RES, MIN_H3_RES
)


def create_interactive_map(cells: List[str],
                          title: str = "H3 Interactive Map",
                          output_path: Optional[Path] = None,
                          center_lat: float = 37.7749,
                          center_lng: float = -122.4194,
                          zoom: int = 10) -> Dict[str, Any]:
    """
    Create an interactive map using folium.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the map
        output_path: Path to save the HTML file (optional)
        center_lat: Center latitude
        center_lng: Center longitude
        zoom: Initial zoom level
        
    Returns:
        Dictionary with map metadata
    """
    try:
        import folium
        from folium import plugins
    except ImportError:
        print("⚠️  Folium not available, creating HTML map without folium")
        return create_simple_html_map(cells, title, output_path)
    
    # Create the map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
    
    # Add tile layers
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    
    # Colors for different resolutions
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen']
    
    # Group layers by resolution
    layer_groups = {}
    
    for cell in cells:
        if not is_valid_cell(cell):
            continue
            
        resolution = get_resolution(cell)
        area = cell_area(cell, 'km^2')
        center_lat, center_lng = cell_to_latlng(cell)
        
        # Get boundary coordinates
        boundary = cell_to_boundary(cell)
        boundary_coords = [[coord[0], coord[1]] for coord in boundary]
        
        # Create polygon
        color = colors[resolution % len(colors)]
        
        # Create popup content
        popup_content = f"""
        <div style="width: 200px;">
            <h4>H3 Cell</h4>
            <p><strong>Index:</strong> {cell}</p>
            <p><strong>Resolution:</strong> {resolution}</p>
            <p><strong>Area:</strong> {area:.6f} km²</p>
            <p><strong>Center:</strong> ({center_lat:.4f}, {center_lng:.4f})</p>
        </div>
        """
        
        # Add polygon to map
        folium.Polygon(
            locations=boundary_coords,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"R{resolution}: {area:.4f} km²",
            color=color,
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.3
        ).add_to(m)
        
        # Add to layer group
        if resolution not in layer_groups:
            layer_groups[resolution] = folium.FeatureGroup(name=f"Resolution {resolution}")
            layer_groups[resolution].add_to(m)
        
        folium.Polygon(
            locations=boundary_coords,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"R{resolution}: {area:.4f} km²",
            color=color,
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.3
        ).add_to(layer_groups[resolution])
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Add measure tool
    plugins.MeasureControl(position='topleft').add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Save the map
    if output_path:
        m.save(str(output_path))
        print(f"✅ Saved interactive map to {output_path}")
    
    # Get map data
    map_data = {
        'title': title,
        'center': [center_lat, center_lng],
        'zoom': zoom,
        'cell_count': len([c for c in cells if is_valid_cell(c)]),
        'resolutions': list(set(get_resolution(c) for c in cells if is_valid_cell(c))),
        'total_area_km2': sum(cell_area(c, 'km^2') for c in cells if is_valid_cell(c))
    }
    
    return map_data


def create_simple_html_map(cells: List[str],
                          title: str = "H3 Simple HTML Map",
                          output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Create a simple HTML map without external dependencies.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the map
        output_path: Path to save the HTML file (optional)
        
    Returns:
        Dictionary with map metadata
    """
    # Generate GeoJSON
    geojson_data = cells_to_geojson(cells)
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {{
                padding: 0;
                margin: 0;
            }}
            html, body, #map {{
                height: 100%;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([37.7749, -122.4194], 10);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);
            
            var geojsonData = {json.dumps(geojson_data)};
            
            L.geoJSON(geojsonData, {{
                style: function(feature) {{
                    var resolution = feature.properties.resolution;
                    var colors = ['#ff0000', '#0000ff', '#00ff00', '#ff00ff', '#ffff00', '#00ffff'];
                    return {{
                        fillColor: colors[resolution % colors.length],
                        weight: 2,
                        opacity: 1,
                        color: 'black',
                        fillOpacity: 0.3
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    var popupContent = '<div style="width: 200px;">' +
                        '<h4>H3 Cell</h4>' +
                        '<p><strong>Index:</strong> ' + feature.properties.h3_index + '</p>' +
                        '<p><strong>Resolution:</strong> ' + feature.properties.resolution + '</p>' +
                        '<p><strong>Area:</strong> ' + feature.properties.area_km2.toFixed(6) + ' km²</p>' +
                        '</div>';
                    layer.bindPopup(popupContent);
                    layer.bindTooltip('R' + feature.properties.resolution + ': ' + feature.properties.area_km2.toFixed(4) + ' km²');
                }}
            }}).addTo(map);
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"✅ Saved simple HTML map to {output_path}")
    
    # Get map data
    map_data = {
        'title': title,
        'cell_count': len([c for c in cells if is_valid_cell(c)]),
        'resolutions': list(set(get_resolution(c) for c in cells if is_valid_cell(c))),
        'total_area_km2': sum(cell_area(c, 'km^2') for c in cells if is_valid_cell(c))
    }
    
    return map_data


def create_interactive_dashboard(cells: List[str],
                               title: str = "H3 Interactive Dashboard",
                               output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Create an interactive HTML dashboard with charts and maps.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the dashboard
        output_path: Path to save the HTML file (optional)
        
    Returns:
        Dictionary with dashboard metadata
    """
    # Analyze cell data
    distribution = analyze_cell_distribution(cells)
    stats = calculate_spatial_statistics(cells)
    
    # Generate GeoJSON for map
    geojson_data = cells_to_geojson(cells)
    
    # Create dashboard HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #007bff;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #007bff;
            }}
            .stat-label {{
                color: #666;
                margin-top: 5px;
            }}
            .chart-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .chart {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .map-container {{
                height: 500px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            #map {{
                height: 100%;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <p>Interactive H3 Geospatial Analysis Dashboard</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{distribution['total_cells']}</div>
                    <div class="stat-label">Total Cells</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{distribution['total_area_km2']:.2f}</div>
                    <div class="stat-label">Total Area (km²)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(distribution['resolutions'])}</div>
                    <div class="stat-label">Resolutions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{distribution['pentagons']}</div>
                    <div class="stat-label">Pentagons</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart">
                    <h3>Resolution Distribution</h3>
                    <div id="resolutionChart"></div>
                </div>
                <div class="chart">
                    <h3>Area Distribution</h3>
                    <div id="areaChart"></div>
                </div>
            </div>
            
            <div class="map-container">
                <div id="map"></div>
            </div>
        </div>
        
        <script>
            // Map setup
            var map = L.map('map').setView([37.7749, -122.4194], 10);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetmap contributors'
            }}).addTo(map);
            
            var geojsonData = {json.dumps(geojson_data)};
            
            L.geoJSON(geojsonData, {{
                style: function(feature) {{
                    var resolution = feature.properties.resolution;
                    var colors = ['#ff0000', '#0000ff', '#00ff00', '#ff00ff', '#ffff00', '#00ffff'];
                    return {{
                        fillColor: colors[resolution % colors.length],
                        weight: 2,
                        opacity: 1,
                        color: 'black',
                        fillOpacity: 0.3
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    var popupContent = '<div style="width: 200px;">' +
                        '<h4>H3 Cell</h4>' +
                        '<p><strong>Index:</strong> ' + feature.properties.h3_index + '</p>' +
                        '<p><strong>Resolution:</strong> ' + feature.properties.resolution + '</p>' +
                        '<p><strong>Area:</strong> ' + feature.properties.area_km2.toFixed(6) + ' km²</p>' +
                        '</div>';
                    layer.bindPopup(popupContent);
                    layer.bindTooltip('R' + feature.properties.resolution + ': ' + feature.properties.area_km2.toFixed(4) + ' km²');
                }}
            }}).addTo(map);
            
            // Resolution distribution chart
            var resolutionData = {json.dumps(distribution['resolutions'])};
            var resolutionCounts = {{}};
            resolutionData.forEach(function(res) {{
                resolutionCounts[res] = (resolutionCounts[res] || 0) + 1;
            }});
            
            var resolutionChart = {{
                x: Object.keys(resolutionCounts),
                y: Object.values(resolutionCounts),
                type: 'bar',
                marker: {{
                    color: 'rgb(55, 83, 109)'
                }}
            }};
            
            var resolutionLayout = {{
                title: 'Cells by Resolution',
                xaxis: {{ title: 'Resolution' }},
                yaxis: {{ title: 'Number of Cells' }}
            }};
            
            Plotly.newPlot('resolutionChart', [resolutionChart], resolutionLayout);
            
            // Area distribution chart
            var areas = {json.dumps([cell_area(c, 'km^2') for c in cells if is_valid_cell(c)])};
            
            var areaChart = {{
                x: areas,
                type: 'histogram',
                marker: {{
                    color: 'rgb(158, 202, 225)',
                    line: {{
                        color: 'rgb(8, 48, 107)',
                        width: 1.5
                    }}
                }}
            }};
            
            var areaLayout = {{
                title: 'Area Distribution',
                xaxis: {{ title: 'Area (km²)' }},
                yaxis: {{ title: 'Frequency' }}
            }};
            
            Plotly.newPlot('areaChart', [areaChart], areaLayout);
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"✅ Saved interactive dashboard to {output_path}")
    
    # Get dashboard data
    dashboard_data = {
        'title': title,
        'cell_count': distribution['total_cells'],
        'total_area_km2': distribution['total_area_km2'],
        'resolutions': distribution['resolutions'],
        'pentagons': distribution['pentagons'],
        'statistics': stats
    }
    
    return dashboard_data


def create_zoomable_map(cells: List[str],
                       title: str = "H3 Zoomable Map",
                       output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Create a zoomable map with different detail levels.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the map
        output_path: Path to save the HTML file (optional)
        
    Returns:
        Dictionary with map metadata
    """
    # Group cells by resolution
    cells_by_resolution = {}
    for cell in cells:
        if not is_valid_cell(cell):
            continue
        resolution = get_resolution(cell)
        if resolution not in cells_by_resolution:
            cells_by_resolution[resolution] = []
        cells_by_resolution[resolution].append(cell)
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {{
                padding: 0;
                margin: 0;
            }}
            html, body, #map {{
                height: 100%;
                width: 100%;
            }}
            .legend {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                z-index: 1000;
            }}
            .legend-item {{
                margin: 5px 0;
            }}
            .legend-color {{
                display: inline-block;
                width: 20px;
                height: 20px;
                margin-right: 5px;
                border: 1px solid black;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="legend">
            <h4>Resolutions</h4>
            <div id="legend-content"></div>
        </div>
        
        <script>
            var map = L.map('map').setView([37.7749, -122.4194], 10);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);
            
            var layers = {{}};
            var colors = ['#ff0000', '#0000ff', '#00ff00', '#ff00ff', '#ffff00', '#00ffff', '#ff8800', '#8800ff'];
            
            var cellsByResolution = {json.dumps(cells_by_resolution)};
            
            Object.keys(cellsByResolution).forEach(function(resolution) {{
                var color = colors[parseInt(resolution) % colors.length];
                var layer = L.layerGroup();
                
                cellsByResolution[resolution].forEach(function(cell) {{
                    // Create a simple polygon for the cell (simplified)
                    var center = [37.7749, -122.4194]; // This should be calculated from cell
                    var size = 0.01 / Math.pow(2, parseInt(resolution));
                    
                    var polygon = L.polygon([
                        [center[0] - size, center[1] - size],
                        [center[0] + size, center[1] - size],
                        [center[0] + size, center[1] + size],
                        [center[0] - size, center[1] + size]
                    ], {{
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.3,
                        weight: 2
                    }});
                    
                    polygon.bindPopup('<strong>H3 Cell</strong><br>Resolution: ' + resolution + '<br>Index: ' + cell);
                    polygon.addTo(layer);
                }});
                
                layers[resolution] = layer;
                layer.addTo(map);
                
                // Add to legend
                var legendItem = document.createElement('div');
                legendItem.className = 'legend-item';
                legendItem.innerHTML = '<span class="legend-color" style="background-color: ' + color + '"></span>Resolution ' + resolution;
                document.getElementById('legend-content').appendChild(legendItem);
            }});
            
            // Add zoom control
            var zoomControl = L.control.zoom({{
                position: 'bottomright'
            }});
            zoomControl.addTo(map);
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    if output_path:
        with open(output_path, 'w') as f:
            f.write(html_content)
        print(f"✅ Saved zoomable map to {output_path}")
    
    # Get map data
    map_data = {
        'title': title,
        'cell_count': len([c for c in cells if is_valid_cell(c)]),
        'resolutions': list(cells_by_resolution.keys()),
        'layers': len(cells_by_resolution)
    }
    
    return map_data


def create_interactive_report(cells: List[str],
                            output_dir: Path,
                            title: str = "H3 Interactive Report") -> Dict[str, Any]:
    """
    Generate a comprehensive interactive report for H3 cells.
    
    Args:
        cells: List of H3 cell indices
        output_dir: Directory to save interactive files
        title: Title for the report
        
    Returns:
        Dictionary with report metadata
    """
    output_dir.mkdir(exist_ok=True)
    
    report_data = {
        'title': title,
        'total_cells': len(cells),
        'interactive_files': {}
    }
    
    if cells:
        # Generate interactive map
        map_path = output_dir / "interactive_map.html"
        map_data = create_interactive_map(cells, output_path=map_path)
        report_data['interactive_files']['interactive_map'] = map_data
        
        # Generate dashboard
        dashboard_path = output_dir / "interactive_dashboard.html"
        dashboard_data = create_interactive_dashboard(cells, output_path=dashboard_path)
        report_data['interactive_files']['dashboard'] = dashboard_data
        
        # Generate zoomable map
        zoomable_path = output_dir / "zoomable_map.html"
        zoomable_data = create_zoomable_map(cells, output_path=zoomable_path)
        report_data['interactive_files']['zoomable_map'] = zoomable_data
    
    # Save report metadata
    report_path = output_dir / "interactive_report.json"
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"✅ Generated interactive report with {len(report_data['interactive_files'])} interactive files")
    return report_data
