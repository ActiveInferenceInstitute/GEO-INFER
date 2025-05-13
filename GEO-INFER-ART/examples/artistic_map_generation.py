#!/usr/bin/env python
"""
Example script demonstrating core functionality of GEO-INFER-ART.

This script showcases various features including artistic map visualization,
style transfer, generative maps, procedural art, place-based art, and cultural mapping.
"""

import os
import sys
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

from geo_infer_art import (
    GeoArt,
    ColorPalette,
    StyleTransfer,
    GenerativeMap,
    ProceduralArt,
    PlaceArt,
    CulturalMap
)


def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_sample_geo_data():
    """Create a sample GeoDataFrame for examples."""
    # Create a simple polygonal dataset
    geometries = [
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        Polygon([(1, 0), (1, 1), (2, 1), (2, 0)]),
        Polygon([(0, 1), (0, 2), (1, 2), (1, 1)]),
        Polygon([(1, 1), (1, 2), (2, 2), (2, 1)]),
    ]
    
    # Create GeoDataFrame with associated data
    data = {
        'region': ['A', 'B', 'C', 'D'],
        'value': [10, 20, 30, 40]
    }
    
    gdf = gpd.GeoDataFrame(data, geometry=geometries, crs="EPSG:4326")
    return gdf


def example_1_basic_geo_art():
    """Example 1: Creating basic artistic visualizations using GeoArt."""
    print("\nExample 1: Basic GeoArt")
    print("-----------------------")
    
    # Create sample geodata
    geo_data = create_sample_geo_data()
    print(f"Created sample GeoDataFrame with {len(geo_data)} features")
    
    # Create GeoArt visualization with default settings
    geo_art = GeoArt(data=geo_data)
    
    # Apply different styles
    styles = ["default", "watercolor", "minimal", "blueprint"]
    
    for style in styles:
        print(f"Applying {style} style...")
        
        # Apply the style
        geo_art.apply_style(
            style=style,
            color_palette="earth" if style == "watercolor" else None,
            line_width=1.5,
            alpha=0.7
        )
        
        # Save the output
        output_path = f"output/geo_art_{style}.png"
        geo_art._figure.savefig(output_path)
        print(f"Saved to {output_path}")
    
    print("Basic GeoArt example completed")


def example_2_color_palettes():
    """Example 2: Creating and using color palettes."""
    print("\nExample 2: Color Palettes")
    print("------------------------")
    
    # Create predefined color palettes
    palettes = ["viridis", "earth", "sunset", "ocean", "forest"]
    
    for palette_name in palettes:
        print(f"Creating {palette_name} palette...")
        palette = ColorPalette(palette_name)
        
        # Visualize and save the palette
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 2))
        
        # Display color swatches
        for i, color in enumerate(palette.colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
        
        ax.set_xlim(0, len(palette.colors))
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"Color Palette: {palette_name}")
        
        # Save the output
        output_path = f"output/color_palette_{palette_name}.png"
        fig.savefig(output_path)
        plt.close(fig)
        print(f"Saved to {output_path}")
    
    # Create a color palette using color theory
    print("Creating color palette from color theory...")
    theory_palette = ColorPalette.from_color_theory(
        base_color="#1E88E5",
        scheme="analogous",
        n_colors=6
    )
    
    # Save theory-based palette
    fig, ax = plt.subplots(figsize=(10, 2))
    for i, color in enumerate(theory_palette.colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
    
    ax.set_xlim(0, len(theory_palette.colors))
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Color Palette: Analogous (from #1E88E5)")
    
    output_path = "output/color_palette_theory.png"
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved to {output_path}")
    
    print("Color palette example completed")


def example_3_style_transfer():
    """Example 3: Applying style transfer to geospatial visualizations."""
    print("\nExample 3: Style Transfer")
    print("-----------------------")
    
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
    except ImportError:
        print("TensorFlow not available, skipping style transfer example")
        return
    
    # Create sample geodata
    geo_data = create_sample_geo_data()
    
    # Apply style transfer with a predefined style
    styles = ["watercolor", "sketch", "abstract"]
    
    for style in styles:
        try:
            print(f"Applying {style} style transfer...")
            
            # Apply style transfer (with reduced iterations for example)
            styled_image = StyleTransfer.apply(
                geo_data=geo_data,
                style=style,
                iterations=5,  # Low iterations for example speed
                content_weight=1e3,
                style_weight=1e-2
            )
            
            # Save the styled image
            output_path = f"output/style_transfer_{style}.png"
            styled_image.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error applying {style} style: {str(e)}")
    
    print("Style transfer example completed")


def example_4_generative_maps():
    """Example 4: Creating generative maps from elevation data."""
    print("\nExample 4: Generative Maps")
    print("------------------------")
    
    # Create synthetic elevation data for demonstration
    print("Creating synthetic elevation data...")
    shape = (256, 256)
    x, y = np.meshgrid(np.linspace(-3, 3, shape[0]), np.linspace(-3, 3, shape[1]))
    
    # Create a complex terrain with multiple peaks and valleys
    terrain = np.zeros(shape)
    for cx, cy, amplitude in [(-1, -1, 1.0), (1.5, 1.5, 0.8), (0, 2, 0.6), (2, 0, 0.7)]:
        terrain += amplitude * np.exp(-((x - cx)**2 + (y - cy)**2) / 1.0)
    
    # Create generative maps with different styles
    styles = ["contour", "flow", "particles", "contour_flow"]
    
    for style in styles:
        print(f"Generating {style} map...")
        
        # Create the generative map
        gen_map = GenerativeMap.from_elevation(
            region=terrain,
            resolution=512,
            abstraction_level=0.5,
            style=style
        )
        
        # Save the output
        output_path = f"output/generative_map_{style}.png"
        gen_map.save(output_path)
        print(f"Saved to {output_path}")
    
    # Create maps with different abstraction levels
    print("Generating maps with different abstraction levels...")
    for level in [0.1, 0.5, 0.9]:
        gen_map = GenerativeMap.from_elevation(
            region=terrain,
            resolution=512,
            abstraction_level=level,
            style="contour"
        )
        
        output_path = f"output/generative_map_abstract_{level}.png"
        gen_map.save(output_path)
        print(f"Saved to {output_path}")
    
    print("Generative maps example completed")


def example_5_procedural_art():
    """Example 5: Creating procedural art based on geographic features."""
    print("\nExample 5: Procedural Art")
    print("-----------------------")
    
    # Create procedural art using geographic coordinates
    print("Creating procedural art from geographic coordinates...")
    coordinates = [
        (40.7128, -74.0060, "New York"),  # New York
        (37.7749, -122.4194, "San Francisco"),  # San Francisco
        (51.5074, -0.1278, "London"),  # London
        (35.6762, 139.6503, "Tokyo"),  # Tokyo
    ]
    
    for lat, lon, name in coordinates:
        print(f"Generating art for {name}...")
        proc_art = ProceduralArt.from_geo_coordinates(
            lat=lat,
            lon=lon,
            resolution=(600, 600)
        )
        
        # Save the output
        output_path = f"output/procedural_art_{name.lower().replace(' ', '_')}.png"
        proc_art.save(output_path)
        print(f"Saved to {output_path}")
    
    # Create procedural art with different algorithms
    algorithms = [
        "noise_field",
        "l_system",
        "cellular_automata",
        "reaction_diffusion",
        "voronoi",
        "fractal_tree"
    ]
    
    lat, lon = 40.7128, -74.0060  # Use New York as the base
    
    for algorithm in algorithms:
        try:
            print(f"Generating art with {algorithm} algorithm...")
            proc_art = ProceduralArt.from_geo_coordinates(
                lat=lat,
                lon=lon,
                algorithm=algorithm,
                resolution=(600, 600)
            )
            
            # Save the output
            output_path = f"output/procedural_art_algorithm_{algorithm}.png"
            proc_art.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error generating art with {algorithm}: {str(e)}")
    
    print("Procedural art example completed")


def example_6_place_art():
    """Example 6: Creating location-based art with PlaceArt."""
    print("\nExample 6: Place Art")
    print("-----------------")
    
    # Create place art for notable locations
    places = [
        (40.7128, -74.0060, "New York", None),  # New York
        (48.8566, 2.3522, "Paris", None),  # Paris
        (37.7749, -122.4194, "San Francisco", None),  # San Francisco
        # If you have feature names registered in the system:
        # (None, None, None, "grand_canyon")  # Use named feature instead of coordinates
    ]
    
    styles = ["abstract", "topographic", "cultural", "mixed_media"]
    
    # For each place, try different styles
    for i, (lat, lon, name, feature) in enumerate(places):
        # Select different style for each place
        style = styles[i % len(styles)]
        
        print(f"Creating {style} place art for {name}...")
        
        try:
            # Create from coordinates or feature name
            if feature is not None:
                place_art = PlaceArt.from_place_name(
                    place_name=feature,
                    style=style
                )
            else:
                place_art = PlaceArt.from_coordinates(
                    lat=lat,
                    lon=lon,
                    name=name,
                    style=style,
                    radius_km=5.0
                )
            
            # Add metadata overlay
            place_art.add_metadata_overlay(position="bottom")
            
            # Save the output
            output_path = f"output/place_art_{name.lower().replace(' ', '_')}.png"
            place_art.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error creating place art for {name}: {str(e)}")
    
    print("Place art example completed")


def example_7_cultural_maps():
    """Example 7: Creating cultural maps with the CulturalMap class."""
    print("\nExample 7: Cultural Maps")
    print("---------------------")
    
    # Create cultural maps for regions
    regions = [
        ("mediterranean", "historical"),
        ("east_asia", "linguistic"),
    ]
    
    styles = ["artistic", "minimalist", "detailed", "abstract"]
    
    # For each region, create a cultural map
    for i, (region, theme) in enumerate(regions):
        # Select different style for each region
        style = styles[i % len(styles)]
        
        print(f"Creating {style} cultural map for {region} with {theme} theme...")
        
        try:
            # Create from region name
            cultural_map = CulturalMap.from_region(
                region_name=region,
                cultural_theme=theme,
                style=style
            )
            
            # Add narrative
            narrative = f"This map depicts the {theme} context of the {region} region."
            cultural_map.add_narrative(narrative=narrative, position="bottom")
            
            # Save the output
            output_path = f"output/cultural_map_{region}_{theme}.png"
            cultural_map.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error creating cultural map for {region}: {str(e)}")
    
    # Also create a map from coordinates
    try:
        print("Creating cultural map for Rome from coordinates...")
        cultural_map = CulturalMap.from_coordinates(
            lat=41.9028,  # Rome
            lon=12.4964,
            radius_km=50.0,
            cultural_theme="historical",
            style="artistic"
        )
        
        # Add narrative
        narrative = "This map depicts the historical context of Rome and its surroundings."
        cultural_map.add_narrative(narrative=narrative, position="bottom")
        
        # Save the output
        output_path = "output/cultural_map_rome.png"
        cultural_map.save(output_path)
        print(f"Saved to {output_path}")
        
    except Exception as e:
        print(f"Error creating cultural map for Rome: {str(e)}")
    
    print("Cultural maps example completed")


def run_all():
    """Run all examples in this script."""
    example_1_basic_geo_art()
    example_2_color_palettes()
    example_3_style_transfer()
    example_4_generative_maps()
    example_5_procedural_art()
    example_6_place_art()
    example_7_cultural_maps()


if __name__ == "__main__":
    print("GEO-INFER-ART Example: Artistic Map Generation")
    print("==============================================")
    
    # Create output directory
    output_dir = "output"
    ensure_directory(output_dir)
    
    # Run examples
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        if example_num == 1:
            example_1_basic_geo_art()
        elif example_num == 2:
            example_2_color_palettes()
        elif example_num == 3:
            example_3_style_transfer()
        elif example_num == 4:
            example_4_generative_maps()
        elif example_num == 5:
            example_5_procedural_art()
        elif example_num == 6:
            example_6_place_art()
        elif example_num == 7:
            example_7_cultural_maps()
        else:
            print(f"Unknown example number: {example_num}")
            print("Available examples: 1-7")
    else:
        run_all()
    
    print("\nAll examples completed. Check the 'output' directory for results.") 