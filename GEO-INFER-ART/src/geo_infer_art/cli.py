#!/usr/bin/env python
"""
Command-line interface for GEO-INFER-ART.
"""

import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple, Union

from geo_infer_art import (
    GeoArt, 
    StyleTransfer, 
    ColorPalette,
    GenerativeMap, 
    ProceduralArt,
    PlaceArt, 
    CulturalMap
)


def ensure_directory(directory):
    """Create output directory if it doesn't exist."""
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def process_geo_art(args):
    """Process geospatial data with GeoArt."""
    print(f"Loading geospatial data from {args.input}...")
    
    # Load the data
    if args.input.lower().endswith(('.geojson', '.json')):
        geo_art = GeoArt.load_geojson(args.input)
    elif args.input.lower().endswith(('.tif', '.tiff', '.jpg', '.png')):
        geo_art = GeoArt.load_raster(args.input)
    else:
        print(f"Error: Unsupported input file format: {args.input}")
        print("Supported formats: .geojson, .json, .tif, .tiff, .jpg, .png")
        return 1
    
    # Apply style
    print(f"Applying style: {args.style}")
    geo_art.apply_style(
        style=args.style,
        color_palette=args.color_palette,
        line_width=args.line_width,
        alpha=args.alpha,
        background_color=args.background_color
    )
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    geo_art.save(args.output, dpi=args.dpi)
    
    print("Done!")
    return 0


def process_style_transfer(args):
    """Process style transfer on geospatial data."""
    print(f"Loading geospatial data from {args.input}...")
    
    # Load the data
    if args.input.lower().endswith(('.geojson', '.json')):
        geo_data = GeoArt.load_geojson(args.input).data
    elif args.input.lower().endswith(('.tif', '.tiff', '.jpg', '.png')):
        geo_data = GeoArt.load_raster(args.input).data
    else:
        print(f"Error: Unsupported input file format: {args.input}")
        print("Supported formats: .geojson, .json, .tif, .tiff, .jpg, .png")
        return 1
    
    # Check if TensorFlow is available
    try:
        import tensorflow as tf
    except ImportError:
        print("Error: TensorFlow is required for style transfer")
        print("Install it with 'pip install tensorflow'")
        return 1
    
    # Apply style transfer
    print(f"Applying style transfer: {args.style_transfer}")
    try:
        styled_image = StyleTransfer.apply(
            geo_data=geo_data,
            style=args.style_transfer,
            iterations=args.iterations,
            style_weight=args.style_weight,
            content_weight=args.content_weight,
            color_palette=args.color_palette
        )
    except Exception as e:
        print(f"Error during style transfer: {str(e)}")
        return 1
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    styled_image.save(args.output)
    
    print("Done!")
    return 0


def process_place_art(args):
    """Generate place-based art."""
    if args.place:
        print(f"Generating art for place: {args.place}")
        place_art = PlaceArt.from_place_name(
            place_name=args.place,
            style=args.style
        )
    elif args.coordinates:
        try:
            lat, lon = map(float, args.coordinates.split(','))
            print(f"Generating art for coordinates: {lat}, {lon}")
            place_art = PlaceArt.from_coordinates(
                lat=lat,
                lon=lon,
                style=args.style
            )
        except ValueError:
            print("Error: Invalid coordinates format. Use 'lat,lon' (e.g., '40.7128,-74.0060')")
            return 1
    else:
        print("Error: Either --place or --coordinates must be specified")
        return 1
    
    # Add metadata overlay if requested
    if args.add_metadata:
        place_art.add_metadata_overlay(position="bottom")
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    place_art.save(args.output)
    
    print("Done!")
    return 0


def process_generative_map(args):
    """Generate art from elevation data."""
    if args.region:
        print(f"Generating elevation art for region: {args.region}")
        gen_map = GenerativeMap.from_elevation(
            region=args.region,
            resolution=args.resolution,
            abstraction_level=args.abstraction_level,
            style=args.style
        )
    elif args.bbox:
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, args.bbox.split(','))
            bbox = (min_lon, min_lat, max_lon, max_lat)
            print(f"Generating elevation art for bbox: {bbox}")
            gen_map = GenerativeMap.from_elevation(
                region=bbox,
                resolution=args.resolution,
                abstraction_level=args.abstraction_level,
                style=args.style
            )
        except ValueError:
            print("Error: Invalid bbox format. Use 'min_lon,min_lat,max_lon,max_lat'")
            return 1
    else:
        print("Error: Either --region or --bbox must be specified")
        return 1
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    gen_map.save(args.output)
    
    print("Done!")
    return 0


def process_procedural_art(args):
    """Generate procedural art."""
    if args.coordinates:
        try:
            lat, lon = map(float, args.coordinates.split(','))
            print(f"Generating procedural art for coordinates: {lat}, {lon}")
            art = ProceduralArt.from_geo_coordinates(
                lat=lat,
                lon=lon,
                algorithm=args.algorithm,
                additional_params={
                    "color_palette": args.color_palette
                }
            )
        except ValueError:
            print("Error: Invalid coordinates format. Use 'lat,lon' (e.g., '40.7128,-74.0060')")
            return 1
    elif args.feature_type:
        print(f"Generating procedural art for feature type: {args.feature_type}")
        art = ProceduralArt.from_geo_features(
            feature_type=args.feature_type,
            feature_count=args.feature_count,
            algorithm=args.algorithm,
            additional_params={
                "color_palette": args.color_palette
            }
        )
    else:
        print(f"Generating procedural art with algorithm: {args.algorithm}")
        art = ProceduralArt(
            algorithm=args.algorithm,
            params={
                "color_palette": args.color_palette
            },
            resolution=(args.resolution, args.resolution)
        )
        art.generate()
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    art.save(args.output)
    
    print("Done!")
    return 0


def process_cultural_map(args):
    """Generate cultural maps."""
    if args.region:
        print(f"Generating cultural map for region: {args.region}")
        cultural_map = CulturalMap.from_region(
            region_name=args.region,
            cultural_theme=args.cultural_theme,
            style=args.style
        )
    elif args.coordinates:
        try:
            lat, lon = map(float, args.coordinates.split(','))
            print(f"Generating cultural map for coordinates: {lat}, {lon}")
            cultural_map = CulturalMap.from_coordinates(
                lat=lat,
                lon=lon,
                radius_km=args.radius_km,
                cultural_theme=args.cultural_theme,
                style=args.style
            )
        except ValueError:
            print("Error: Invalid coordinates format. Use 'lat,lon' (e.g., '40.7128,-74.0060')")
            return 1
    else:
        print("Error: Either --region or --coordinates must be specified")
        return 1
    
    # Add narrative if provided
    if args.narrative:
        cultural_map.add_narrative(args.narrative)
    
    # Apply cultural style
    if args.apply_cultural_style:
        cultural_map.apply_cultural_style()
    
    # Save the result
    output_dir = os.path.dirname(args.output)
    ensure_directory(output_dir)
    
    print(f"Saving result to {args.output}...")
    cultural_map.save(args.output)
    
    print("Done!")
    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="GEO-INFER-ART: Artistic visualization of geospatial data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # GeoArt command
    geo_art_parser = subparsers.add_parser(
        "geo-art", 
        help="Create artistic visualization of geospatial data"
    )
    geo_art_parser.add_argument("--input", required=True, help="Input geospatial file")
    geo_art_parser.add_argument("--output", required=True, help="Output image file")
    geo_art_parser.add_argument("--style", default="default", help="Visualization style")
    geo_art_parser.add_argument("--color-palette", help="Color palette name")
    geo_art_parser.add_argument("--line-width", type=float, default=1.0, help="Line width for vector data")
    geo_art_parser.add_argument("--alpha", type=float, default=0.8, help="Transparency level (0.0-1.0)")
    geo_art_parser.add_argument("--background-color", default="white", help="Background color")
    geo_art_parser.add_argument("--dpi", type=int, default=300, help="Output resolution (DPI)")
    
    # Style Transfer command
    style_transfer_parser = subparsers.add_parser(
        "style-transfer", 
        help="Apply artistic style transfer to geospatial data"
    )
    style_transfer_parser.add_argument("--input", required=True, help="Input geospatial file")
    style_transfer_parser.add_argument("--output", required=True, help="Output image file")
    style_transfer_parser.add_argument("--style-transfer", required=True, help="Style name or file path")
    style_transfer_parser.add_argument("--iterations", type=int, default=100, help="Number of iterations")
    style_transfer_parser.add_argument("--style-weight", type=float, default=1e-2, help="Style weight")
    style_transfer_parser.add_argument("--content-weight", type=float, default=1e4, help="Content weight")
    style_transfer_parser.add_argument("--color-palette", help="Optional color palette to apply")
    
    # Place Art command
    place_art_parser = subparsers.add_parser(
        "place-art", 
        help="Create art based on geographic locations"
    )
    place_art_group = place_art_parser.add_mutually_exclusive_group(required=True)
    place_art_group.add_argument("--place", help="Name of the place")
    place_art_group.add_argument("--coordinates", help="Coordinates as 'lat,lon'")
    place_art_parser.add_argument("--output", required=True, help="Output image file")
    place_art_parser.add_argument("--style", default="abstract", help="Art style")
    place_art_parser.add_argument("--add-metadata", action="store_true", help="Add location metadata overlay")
    
    # Generative Map command
    gen_map_parser = subparsers.add_parser(
        "generative-map", 
        help="Generate art from elevation data"
    )
    gen_map_group = gen_map_parser.add_mutually_exclusive_group(required=True)
    gen_map_group.add_argument("--region", help="Named region (e.g., 'grand_canyon', 'everest')")
    gen_map_group.add_argument("--bbox", help="Bounding box as 'min_lon,min_lat,max_lon,max_lat'")
    gen_map_parser.add_argument("--output", required=True, help="Output image file")
    gen_map_parser.add_argument("--style", default="contour", help="Generative style")
    gen_map_parser.add_argument("--resolution", type=int, default=512, help="Output resolution")
    gen_map_parser.add_argument("--abstraction-level", type=float, default=0.5, help="Level of abstraction (0.0-1.0)")
    
    # Procedural Art command
    proc_art_parser = subparsers.add_parser(
        "procedural-art", 
        help="Generate procedural art"
    )
    proc_art_group = proc_art_parser.add_mutually_exclusive_group()
    proc_art_group.add_argument("--coordinates", help="Coordinates as 'lat,lon'")
    proc_art_group.add_argument("--feature-type", help="Geographic feature type")
    proc_art_parser.add_argument("--feature-count", type=int, default=5, help="Number of features")
    proc_art_parser.add_argument("--output", required=True, help="Output image file")
    proc_art_parser.add_argument("--algorithm", default="noise_field", help="Procedural algorithm")
    proc_art_parser.add_argument("--color-palette", default="viridis", help="Color palette name")
    proc_art_parser.add_argument("--resolution", type=int, default=800, help="Output resolution")
    
    # Cultural Map command
    cultural_map_parser = subparsers.add_parser(
        "cultural-map", 
        help="Create maps with cultural context"
    )
    cultural_map_group = cultural_map_parser.add_mutually_exclusive_group(required=True)
    cultural_map_group.add_argument("--region", help="Named region (e.g., 'mediterranean', 'east_asia')")
    cultural_map_group.add_argument("--coordinates", help="Coordinates as 'lat,lon'")
    cultural_map_parser.add_argument("--radius-km", type=float, default=100.0, help="Radius in kilometers")
    cultural_map_parser.add_argument("--output", required=True, help="Output image file")
    cultural_map_parser.add_argument("--cultural-theme", default="historical", help="Cultural theme")
    cultural_map_parser.add_argument("--style", default="artistic", help="Visual style")
    cultural_map_parser.add_argument("--narrative", help="Cultural narrative text to add")
    cultural_map_parser.add_argument("--apply-cultural-style", action="store_true", help="Apply cultural styling")
    
    # Simplified command for basic usage
    simple_parser = subparsers.add_parser(
        "simple", 
        help="Simplified command for common operations"
    )
    simple_parser.add_argument("--input", help="Input geospatial file")
    simple_parser.add_argument("--output", required=True, help="Output image file")
    simple_parser.add_argument("--style", default="default", help="Visualization style")
    simple_parser.add_argument("--place", help="Name of the place for place-based art")
    simple_parser.add_argument("--style-transfer", help="Apply style transfer with this style name")
    
    args = parser.parse_args()
    
    if args.command == "geo-art":
        return process_geo_art(args)
    elif args.command == "style-transfer":
        return process_style_transfer(args)
    elif args.command == "place-art":
        return process_place_art(args)
    elif args.command == "generative-map":
        return process_generative_map(args)
    elif args.command == "procedural-art":
        return process_procedural_art(args)
    elif args.command == "cultural-map":
        return process_cultural_map(args)
    elif args.command == "simple":
        # Process simplified commands
        if args.input and args.style_transfer:
            args.command = "style-transfer"
            args.iterations = 50  # Use fewer iterations for simple mode
            return process_style_transfer(args)
        elif args.input:
            args.command = "geo-art"
            return process_geo_art(args)
        elif args.place:
            args.command = "place-art"
            args.add_metadata = True
            return process_place_art(args)
        else:
            print("Error: --input or --place must be specified with the simple command")
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 