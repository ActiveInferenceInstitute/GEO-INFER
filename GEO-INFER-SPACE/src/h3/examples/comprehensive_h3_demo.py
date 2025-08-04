#!/usr/bin/env python3
"""
Comprehensive H3 Demonstration Orchestrator

Thin orchestrator that runs all H3 example demonstrations using H3 v4.3.0.
Calls individual example scripts to demonstrate core operations, indexing, 
traversal, hierarchy, and analysis.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import only valid H3 v4 methods from our modular framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_to_polygon,
    cell_area, cell_perimeter, edge_length, num_cells, get_resolution, 
    is_valid_cell, is_pentagon, is_class_iii, is_res_class_iii
)
from constants import (
    H3_VERSION, MAX_H3_RES, MIN_H3_RES, H3_RESOLUTIONS
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"🔹 {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n📋 {title}")
    print("-" * 60)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def run_example_script(script_name: str, description: str) -> bool:
    """Run an individual example script."""
    print_subsection(f"Running {description}")
    print(f"Executing: {script_name}")
    
    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print("Output:")
                print(result.stdout.strip())
            return True
        else:
            print(f"❌ {description} failed")
            print("Error output:")
            print(result.stderr.strip())
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def demo_basic_operations():
    """Demonstrate basic H3 operations via thin orchestration."""
    print_section("Basic H3 Operations")
    
    # Run the basic operations example
    success = run_example_script(
        "01_basic_operations.py",
        "Basic H3 Operations (Coordinate conversion, cell properties, validation)"
    )
    
    if success:
        print_subsection("Basic Operations Summary")
        print("✅ Coordinate to cell conversion")
        print("✅ Cell to coordinate conversion") 
        print("✅ Cell boundary extraction")
        print("✅ Cell area and perimeter calculations")
        print("✅ Cell validation and classification")
        print("✅ Resolution comparison and analysis")
    
    return success


def demo_spatial_analysis():
    """Demonstrate spatial analysis operations via thin orchestration."""
    print_section("Spatial Analysis Operations")
    
    # Run the spatial analysis example
    success = run_example_script(
        "02_spatial_analysis.py",
        "Spatial Analysis (Grid operations, distance calculations, path analysis)"
    )
    
    if success:
        print_subsection("Spatial Analysis Summary")
        print("✅ Grid disk and ring operations")
        print("✅ Distance calculations between cells")
        print("✅ Path analysis between cells")
        print("✅ Spatial statistics and density analysis")
        print("✅ Nearest cell finding")
    
    return success


def demo_hierarchical_operations():
    """Demonstrate hierarchical operations via thin orchestration."""
    print_section("Hierarchical Operations")
    
    # Run the hierarchical operations example
    success = run_example_script(
        "03_hierarchical_operations.py",
        "Hierarchical Operations (Parent-child relationships, hierarchy paths)"
    )
    
    if success:
        print_subsection("Hierarchical Operations Summary")
        print("✅ Parent-child cell relationships")
        print("✅ Hierarchy path analysis")
        print("✅ Ancestors and descendants")
        print("✅ Multi-resolution operations")
        print("✅ Hierarchical data analysis")
    
    return success


def demo_data_conversion():
    """Demonstrate data conversion operations via thin orchestration."""
    print_section("Data Conversion Operations")
    
    # Run the data conversion example
    success = run_example_script(
        "04_data_conversion.py",
        "Data Conversion (GeoJSON, WKT, CSV, KML, Shapefile formats)"
    )
    
    if success:
        print_subsection("Data Conversion Summary")
        print("✅ GeoJSON conversion and export")
        print("✅ WKT (Well-Known Text) conversion")
        print("✅ CSV data export")
        print("✅ KML format export")
        print("✅ Shapefile data preparation")
        print("✅ Multi-channel dataset fusion")
    
    return success


def demo_visualization_outputs():
    """Demonstrate visualization outputs via thin orchestration."""
    print_section("Visualization Outputs")
    
    # Run the visualization outputs example
    success = run_example_script(
        "05_visualization_outputs.py",
        "Visualization Outputs (Static, animated, interactive visualizations)"
    )
    
    if success:
        print_subsection("Visualization Summary")
        print("✅ Static visualization generation")
        print("✅ Animated visualization creation")
        print("✅ Interactive visualization preparation")
        print("✅ Heatmap visualization")
        print("✅ Temporal visualization")
        print("✅ Multi-format export capabilities")
    
    return success


def demo_comprehensive_workflow():
    """Demonstrate comprehensive workflow via thin orchestration."""
    print_section("Comprehensive Workflow")
    
    # Run the comprehensive workflow example
    success = run_example_script(
        "06_comprehensive_workflow.py",
        "Comprehensive Workflow (End-to-end H3 analysis pipeline)"
    )
    
    if success:
        print_subsection("Comprehensive Workflow Summary")
        print("✅ Data ingestion and validation")
        print("✅ Spatial analysis and processing")
        print("✅ Hierarchical data organization")
        print("✅ Grid operations and optimization")
        print("✅ Data conversion and export")
        print("✅ Advanced analysis and visualization")
    
    return success


def generate_comprehensive_report():
    """Generate a comprehensive report of all demonstrations."""
    print_section("Comprehensive Report Generation")
    
    output_dir = ensure_output_dir()
    
    # Collect information about all example scripts
    example_scripts = [
        {
            "name": "01_basic_operations.py",
            "description": "Basic H3 Operations",
            "features": [
                "Coordinate conversion", "Cell properties", "Validation",
                "Resolution comparison", "Cell classification"
            ]
        },
        {
            "name": "02_spatial_analysis.py", 
            "description": "Spatial Analysis",
            "features": [
                "Grid operations", "Distance calculations", "Path analysis",
                "Spatial statistics", "Density analysis"
            ]
        },
        {
            "name": "03_hierarchical_operations.py",
            "description": "Hierarchical Operations", 
            "features": [
                "Parent-child relationships", "Hierarchy paths",
                "Ancestors and descendants", "Multi-resolution operations"
            ]
        },
        {
            "name": "04_data_conversion.py",
            "description": "Data Conversion",
            "features": [
                "GeoJSON conversion", "WKT conversion", "CSV export",
                "KML export", "Multi-channel fusion"
            ]
        },
        {
            "name": "05_visualization_outputs.py",
            "description": "Visualization Outputs",
            "features": [
                "Static visualizations", "Animated visualizations", 
                "Interactive visualizations", "Heatmaps", "Temporal data"
            ]
        },
        {
            "name": "06_comprehensive_workflow.py",
            "description": "Comprehensive Workflow",
            "features": [
                "End-to-end pipeline", "Data processing", "Analysis",
                "Visualization", "Export capabilities"
            ]
        }
    ]
    
    # Create comprehensive report
    report = {
        "framework_info": {
            "name": "GEO-INFER H3 Framework",
            "version": H3_VERSION,
            "h3_version": "4.3.0",
            "resolution_range": f"{MIN_H3_RES} to {MAX_H3_RES}",
            "available_resolutions": H3_RESOLUTIONS
        },
        "example_scripts": example_scripts,
        "output_structure": {
            "data": "Raw data files (JSON, CSV)",
            "reports": "Analysis reports and summaries", 
            "visualizations": "Static and interactive visualizations",
            "animations": "Animated visualizations (GIF)",
            "comprehensive": "End-to-end workflow outputs"
        },
        "framework_architecture": {
            "modular_design": "Functions organized in specialized modules",
            "thin_orchestrators": "Example scripts call modular functions",
            "h3_v4_compatibility": "All methods use valid H3 v4 API",
            "output_organization": "Structured output to subdirectories"
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save comprehensive report
    report_file = output_dir / "comprehensive_demo_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Comprehensive report saved to: {report_file}")
    
    # Create summary text report
    summary_file = output_dir / "comprehensive_demo_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("GEO-INFER H3 Framework Comprehensive Demo Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Framework Version: {H3_VERSION}\n")
        f.write(f"H3 Library Version: 4.3.0\n")
        f.write(f"Resolution Range: {MIN_H3_RES} to {MAX_H3_RES}\n\n")
        
        f.write("Example Scripts Executed:\n")
        f.write("-" * 30 + "\n")
        for script in example_scripts:
            f.write(f"• {script['name']}: {script['description']}\n")
            for feature in script['features']:
                f.write(f"  - {feature}\n")
            f.write("\n")
        
        f.write("Output Structure:\n")
        f.write("-" * 20 + "\n")
        for category, description in report["output_structure"].items():
            f.write(f"• {category}: {description}\n")
        
        f.write(f"\nGenerated: {report['timestamp']}\n")
    
    print(f"✅ Summary report saved to: {summary_file}")
    
    return report


def main():
    """Main orchestration function."""
    print("🧪 Comprehensive H3 Geospatial Operations Demo Orchestrator")
    print("=" * 80)
    print(f"H3 Version: {H3_VERSION}")
    print(f"Resolution range: {MIN_H3_RES} to {MAX_H3_RES}")
    print(f"Available resolutions: {H3_RESOLUTIONS}")
    print("=" * 80)
    
    # Ensure output directory exists
    output_dir = ensure_output_dir()
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Track success of each demonstration
    results = {}
    
    try:
        # Run all demonstrations via thin orchestration
        results["basic_operations"] = demo_basic_operations()
        results["spatial_analysis"] = demo_spatial_analysis()
        results["hierarchical_operations"] = demo_hierarchical_operations()
        results["data_conversion"] = demo_data_conversion()
        results["visualization_outputs"] = demo_visualization_outputs()
        results["comprehensive_workflow"] = demo_comprehensive_workflow()
        
        # Generate comprehensive report
        report = generate_comprehensive_report()
        
        # Summary
        print_section("Demo Orchestration Complete")
        successful_demos = sum(results.values())
        total_demos = len(results)
        
        print(f"✅ Successfully executed: {successful_demos}/{total_demos} demonstrations")
        
        for demo_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {demo_name.replace('_', ' ').title()}")
        
        if successful_demos == total_demos:
            print("\n🎉 All H3 demonstrations completed successfully!")
            print("📊 Comprehensive report and outputs generated in output/ directory")
        else:
            print(f"\n⚠️  {total_demos - successful_demos} demonstrations had issues")
            print("Check individual script outputs for details")
        
        return successful_demos == total_demos
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 