"""
Visualization utilities for OSC (OS Climate) integration reporting and analysis.

This module provides comprehensive visualization capabilities for OSC repository status,
test results, H3 grid analysis, and geospatial data processing workflows.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import seaborn as sns

# Optional dependencies with graceful fallbacks
try:
    import geopandas as gpd
    import folium
    from folium.plugins import MarkerCluster, HeatMap
    import h3
    HAS_GEO_DEPS = True
except ImportError:
    HAS_GEO_DEPS = False

# Configure logging
logger = logging.getLogger(__name__)

# Set visualization style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class OSCVisualizationEngine:
    """
    Comprehensive visualization engine for OSC integration analysis and reporting.
    
    Provides static and interactive visualizations for:
    - Repository status and health metrics
    - Test execution results and trends
    - H3 grid analysis and spatial patterns
    - Performance metrics and benchmarks
    """
    
    def __init__(self, output_dir: Union[str, Path] = "reports/visualizations"):
        """
        Initialize the OSC Visualization Engine.
        
        Args:
            output_dir: Directory for saving visualization outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        (self.output_dir / "status").mkdir(exist_ok=True)
        (self.output_dir / "tests").mkdir(exist_ok=True)
        (self.output_dir / "spatial").mkdir(exist_ok=True)
        (self.output_dir / "interactive").mkdir(exist_ok=True)
        
        logger.info(f"OSC Visualization Engine initialized with output directory: {self.output_dir}")
    
    def generate_status_dashboard(self, 
                                 status_data: Dict[str, Any],
                                 save_plots: bool = True) -> Dict[str, Figure]:
        """
        Generate a comprehensive status dashboard with multiple visualizations.
        
        Args:
            status_data: Repository status data from check_repo_status()
            save_plots: Whether to save plots to disk
            
        Returns:
            Dictionary of matplotlib Figure objects
        """
        figures = {}
        
        # 1. Repository Health Overview
        fig_health = self._create_repository_health_chart(status_data)
        figures['repository_health'] = fig_health
        
        # 2. Git Activity Timeline
        if 'repositories' in status_data:
            fig_timeline = self._create_git_activity_timeline(status_data['repositories'])
            figures['git_timeline'] = fig_timeline
        
        # 3. Environment Status Matrix
        fig_env = self._create_environment_status_matrix(status_data)
        figures['environment_status'] = fig_env
        
        # Save plots if requested
        if save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for name, fig in figures.items():
                save_path = self.output_dir / "status" / f"{name}_{timestamp}.png"
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Saved {name} to {save_path}")
        
        return figures
    
    def _create_repository_health_chart(self, status_data: Dict[str, Any]) -> Figure:
        """Create a repository health overview chart."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        if 'repositories' not in status_data:
            fig.suptitle("Repository Health Overview - No Data Available")
            return fig
        
        repos = status_data['repositories']
        repo_names = list(repos.keys())
        
        # 1. Repository Existence Status (Pie Chart)
        exists_count = sum(1 for repo in repos.values() if repo.get('exists', False))
        missing_count = len(repos) - exists_count
        
        ax1.pie([exists_count, missing_count], 
                labels=['Exists', 'Missing'], 
                colors=['#2ecc71', '#e74c3c'],
                autopct='%1.1f%%',
                startangle=90)
        ax1.set_title('Repository Existence Status')
        
        # 2. Git Repository Status (Bar Chart)
        git_status = [repos[repo].get('is_git_repo', False) for repo in repo_names]
        git_counts = [sum(git_status), len(git_status) - sum(git_status)]
        
        ax2.bar(['Valid Git Repos', 'Invalid/Missing'], git_counts, 
                color=['#3498db', '#f39c12'])
        ax2.set_title('Git Repository Status')
        ax2.set_ylabel('Count')
        
        # 3. Virtual Environment Status (Horizontal Bar Chart)
        venv_status = [repos[repo].get('has_venv', False) for repo in repo_names]
        repo_colors = ['#27ae60' if status else '#e67e22' for status in venv_status]
        
        y_pos = np.arange(len(repo_names))
        ax3.barh(y_pos, [1 if status else 0 for status in venv_status], 
                 color=repo_colors)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels([name.replace('osc-geo-', '') for name in repo_names])
        ax3.set_xlabel('Virtual Environment Status')
        ax3.set_title('Virtual Environment Status by Repository')
        ax3.set_xlim(0, 1.2)
        
        # Add text annotations
        for i, status in enumerate(venv_status):
            ax3.text(0.5, i, '✓' if status else '✗', 
                    ha='center', va='center', fontsize=16, 
                    color='white' if status else 'black')
        
        # 4. Overall Health Score (Gauge-like chart)
        health_metrics = []
        for repo_data in repos.values():
            score = 0
            if repo_data.get('exists', False): score += 25
            if repo_data.get('is_git_repo', False): score += 25
            if repo_data.get('has_venv', False): score += 25
            if repo_data.get('current_branch') == 'main': score += 25
            health_metrics.append(score)
        
        avg_health = np.mean(health_metrics) if health_metrics else 0
        
        # Create semi-circle gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        ax4.plot(x, y, 'k-', linewidth=2)
        ax4.fill_between(x, 0, y, alpha=0.3, color='lightgray')
        
        # Add health score indicator
        health_angle = np.pi * (1 - avg_health / 100)
        indicator_x = np.cos(health_angle)
        indicator_y = np.sin(health_angle)
        ax4.arrow(0, 0, indicator_x*0.8, indicator_y*0.8, 
                 head_width=0.1, head_length=0.1, fc='red', ec='red')
        
        ax4.set_xlim(-1.2, 1.2)
        ax4.set_ylim(-0.2, 1.2)
        ax4.set_aspect('equal')
        ax4.axis('off')
        ax4.set_title(f'Overall Health Score: {avg_health:.1f}%')
        
        # Add color zones
        zone_colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
        zone_labels = ['Critical', 'Warning', 'Good', 'Excellent']
        for i, (color, label) in enumerate(zip(zone_colors, zone_labels)):
            start_angle = np.pi * (1 - (i+1)*25/100)
            end_angle = np.pi * (1 - i*25/100)
            angles = np.linspace(start_angle, end_angle, 20)
            x_zone = 0.9 * np.cos(angles)
            y_zone = 0.9 * np.sin(angles)
            ax4.plot(x_zone, y_zone, color=color, linewidth=6, alpha=0.7)
        
        plt.tight_layout()
        fig.suptitle('OSC Repository Health Dashboard', fontsize=16, y=0.98)
        
        return fig
    
    def _create_git_activity_timeline(self, repositories: Dict[str, Any]) -> Figure:
        """Create a Git activity timeline chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        repo_names = []
        commit_info = []
        
        for repo_name, repo_data in repositories.items():
            if repo_data.get('latest_commit'):
                repo_names.append(repo_name.replace('osc-geo-', ''))
                commit_info.append({
                    'repo': repo_name.replace('osc-geo-', ''),
                    'commit': repo_data['latest_commit'][:8],
                    'branch': repo_data.get('current_branch', 'unknown')
                })
        
        if not commit_info:
            ax.text(0.5, 0.5, 'No Git commit information available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Git Activity Timeline - No Data')
            return fig
        
        # Create timeline visualization
        y_positions = range(len(commit_info))
        colors = plt.cm.Set3(np.linspace(0, 1, len(commit_info)))
        
        for i, info in enumerate(commit_info):
            ax.barh(y_positions[i], 1, color=colors[i], alpha=0.7, height=0.6)
            ax.text(0.5, y_positions[i], 
                   f"{info['commit']} ({info['branch']})", 
                   ha='center', va='center', fontweight='bold')
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels([info['repo'] for info in commit_info])
        ax.set_xlabel('Latest Commit Information')
        ax.set_title('Repository Git Status Overview')
        ax.set_xlim(0, 1)
        
        # Remove x-axis ticks as they're not meaningful here
        ax.set_xticks([])
        
        plt.tight_layout()
        return fig
    
    def _create_environment_status_matrix(self, status_data: Dict[str, Any]) -> Figure:
        """Create an environment status matrix visualization."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if 'repositories' not in status_data:
            ax.text(0.5, 0.5, 'No repository data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        repos = status_data['repositories']
        repo_names = [name.replace('osc-geo-', '') for name in repos.keys()]
        
        # Define status categories
        categories = ['Exists', 'Git Repo', 'Has VEnv', 'Main Branch']
        
        # Create status matrix
        status_matrix = []
        for repo_name, repo_data in repos.items():
            repo_status = [
                repo_data.get('exists', False),
                repo_data.get('is_git_repo', False),
                repo_data.get('has_venv', False),
                repo_data.get('current_branch') == 'main'
            ]
            status_matrix.append([1 if status else 0 for status in repo_status])
        
        status_matrix = np.array(status_matrix)
        
        # Create heatmap
        im = ax.imshow(status_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(categories)))
        ax.set_yticks(np.arange(len(repo_names)))
        ax.set_xticklabels(categories)
        ax.set_yticklabels(repo_names)
        
        # Add text annotations
        for i in range(len(repo_names)):
            for j in range(len(categories)):
                text = '✓' if status_matrix[i, j] else '✗'
                ax.text(j, i, text, ha='center', va='center', 
                       color='white' if status_matrix[i, j] else 'black',
                       fontsize=16, fontweight='bold')
        
        ax.set_title('Repository Environment Status Matrix')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Status (0=Failed, 1=Success)', rotation=-90, va="bottom")
        
        plt.tight_layout()
        return fig
    
    def generate_test_results_analysis(self, 
                                     test_report_path: Union[str, Path],
                                     save_plots: bool = True) -> Dict[str, Figure]:
        """
        Generate comprehensive test results analysis visualizations.
        
        Args:
            test_report_path: Path to the test report JSON file
            save_plots: Whether to save plots to disk
            
        Returns:
            Dictionary of matplotlib Figure objects
        """
        figures = {}
        
        try:
            with open(test_report_path, 'r') as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading test report: {e}")
            return figures
        
        # 1. Test Execution Summary
        fig_summary = self._create_test_execution_summary(test_data)
        figures['test_summary'] = fig_summary
        
        # 2. Dependency Installation Analysis
        if 'test_results' in test_data:
            fig_deps = self._create_dependency_analysis(test_data['test_results'])
            figures['dependency_analysis'] = fig_deps
        
        # 3. Timeline Analysis
        fig_timeline = self._create_test_timeline_analysis(test_data)
        figures['test_timeline'] = fig_timeline
        
        # Save plots if requested
        if save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for name, fig in figures.items():
                save_path = self.output_dir / "tests" / f"{name}_{timestamp}.png"
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Saved {name} to {save_path}")
        
        return figures
    
    def _create_test_execution_summary(self, test_data: Dict[str, Any]) -> Figure:
        """Create test execution summary visualization."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Overall success/failure
        overall_success = test_data.get('overall_success', False)
        all_tests_passed = test_data.get('all_tests_passed', False)
        
        # 1. Overall Status Pie Chart
        status_data = [1 if overall_success else 0, 1 if not overall_success else 0]
        colors = ['#2ecc71', '#e74c3c']
        ax1.pie(status_data, labels=['Success', 'Failed'], colors=colors, autopct='%1.1f%%')
        ax1.set_title('Overall Setup Status')
        
        # 2. Steps Analysis
        if 'steps' in test_data:
            steps = test_data['steps']
            step_names = [step.get('name', 'Unknown') for step in steps]
            step_success = [step.get('success', False) for step in steps]
            
            colors = ['#27ae60' if success else '#e74c3c' for success in step_success]
            ax2.bar(range(len(step_names)), [1 if s else 0 for s in step_success], 
                   color=colors)
            ax2.set_xticks(range(len(step_names)))
            ax2.set_xticklabels(step_names, rotation=45, ha='right')
            ax2.set_ylabel('Success (1) / Failure (0)')
            ax2.set_title('Step-by-Step Execution Results')
            ax2.set_ylim(0, 1.2)
        
        # 3. Repository Test Results
        if 'test_results' in test_data:
            test_results = test_data['test_results']
            repo_names = list(test_results.keys())
            repo_success = [test_results[repo].get('success', False) for repo in repo_names]
            
            colors = ['#3498db' if success else '#f39c12' for success in repo_success]
            y_pos = np.arange(len(repo_names))
            ax3.barh(y_pos, [1 if s else 0 for s in repo_success], color=colors)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels([name.replace('osc-geo-', '') for name in repo_names])
            ax3.set_xlabel('Test Success (1) / Failure (0)')
            ax3.set_title('Repository Test Results')
            ax3.set_xlim(0, 1.2)
        
        # 4. Time Analysis
        if 'steps' in test_data:
            step_durations = []
            for step in test_data['steps']:
                if 'start_time' in step and 'end_time' in step:
                    try:
                        start = datetime.fromisoformat(step['start_time'])
                        end = datetime.fromisoformat(step['end_time'])
                        duration = (end - start).total_seconds()
                        step_durations.append(duration)
                    except ValueError:
                        step_durations.append(0)
                else:
                    step_durations.append(0)
            
            if step_durations:
                ax4.bar(range(len(step_names)), step_durations, 
                       color=['#9b59b6', '#1abc9c', '#f1c40f'][:len(step_names)])
                ax4.set_xticks(range(len(step_names)))
                ax4.set_xticklabels(step_names, rotation=45, ha='right')
                ax4.set_ylabel('Duration (seconds)')
                ax4.set_title('Step Execution Times')
        
        plt.tight_layout()
        fig.suptitle('OSC Test Execution Analysis Dashboard', fontsize=16, y=0.98)
        
        return fig
    
    def _create_dependency_analysis(self, test_results: Dict[str, Any]) -> Figure:
        """Create dependency installation analysis."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        dependency_issues = {}
        successful_deps = {}
        
        for repo_name, repo_data in test_results.items():
            if 'steps' in repo_data:
                for step in repo_data['steps']:
                    if step.get('name') == 'setup_script':
                        stderr = step.get('stderr', '')
                        if 'scipy' in stderr.lower():
                            dependency_issues['scipy (Fortran required)'] = dependency_issues.get('scipy (Fortran required)', 0) + 1
                        if 'gdal' in stderr.lower() or 'rasterio' in stderr.lower():
                            dependency_issues['GDAL/Rasterio'] = dependency_issues.get('GDAL/Rasterio', 0) + 1
                        if 'pkg-config' in stderr.lower():
                            dependency_issues['pkg-config'] = dependency_issues.get('pkg-config', 0) + 1
                        
                        stdout = step.get('stdout', '')
                        if 'Successfully installed' in stdout or 'finished with status' in stdout:
                            lines = stdout.split('\n')
                            for line in lines:
                                if 'Collecting' in line and '==' in line:
                                    package = line.split('Collecting ')[1].split('==')[0].strip()
                                    successful_deps[package] = successful_deps.get(package, 0) + 1
        
        # 1. Dependency Issues
        if dependency_issues:
            issues = list(dependency_issues.keys())
            counts = list(dependency_issues.values())
            ax1.bar(issues, counts, color=['#e74c3c', '#f39c12', '#e67e22'])
            ax1.set_title('Dependency Installation Issues')
            ax1.set_ylabel('Number of Repositories Affected')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        else:
            ax1.text(0.5, 0.5, 'No dependency issues detected', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Dependency Installation Issues - None Found')
        
        # 2. Successfully Installed Dependencies
        if successful_deps:
            # Show top 10 most common successful dependencies
            sorted_deps = sorted(successful_deps.items(), key=lambda x: x[1], reverse=True)[:10]
            packages = [item[0] for item in sorted_deps]
            install_counts = [item[1] for item in sorted_deps]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(packages)))
            ax2.barh(packages, install_counts, color=colors)
            ax2.set_title('Successfully Installed Dependencies (Top 10)')
            ax2.set_xlabel('Installation Count')
        else:
            ax2.text(0.5, 0.5, 'No successful installations detected', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Successfully Installed Dependencies - None Found')
        
        plt.tight_layout()
        return fig
    
    def _create_test_timeline_analysis(self, test_data: Dict[str, Any]) -> Figure:
        """Create timeline analysis of test execution."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if 'steps' not in test_data:
            ax.text(0.5, 0.5, 'No timeline data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        steps = test_data['steps']
        timeline_data = []
        
        for i, step in enumerate(steps):
            if 'start_time' in step and 'end_time' in step:
                try:
                    start = datetime.fromisoformat(step['start_time'])
                    end = datetime.fromisoformat(step['end_time'])
                    duration = (end - start).total_seconds()
                    timeline_data.append({
                        'step': step.get('name', f'Step {i+1}'),
                        'start': start,
                        'duration': duration,
                        'success': step.get('success', False)
                    })
                except ValueError:
                    continue
        
        if not timeline_data:
            ax.text(0.5, 0.5, 'No valid timeline data found', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        # Create Gantt chart
        base_time = min(item['start'] for item in timeline_data)
        
        for i, item in enumerate(timeline_data):
            start_offset = (item['start'] - base_time).total_seconds()
            color = '#2ecc71' if item['success'] else '#e74c3c'
            
            ax.barh(i, item['duration'], left=start_offset, 
                   color=color, alpha=0.7, height=0.6)
            
            # Add step label
            ax.text(start_offset + item['duration']/2, i, 
                   f"{item['step']}\n({item['duration']:.1f}s)", 
                   ha='center', va='center', fontsize=9, fontweight='bold')
        
        ax.set_yticks(range(len(timeline_data)))
        ax.set_yticklabels([item['step'] for item in timeline_data])
        ax.set_xlabel('Time (seconds from start)')
        ax.set_title('Test Execution Timeline')
        
        # Add legend
        success_patch = mpatches.Patch(color='#2ecc71', label='Success')
        failure_patch = mpatches.Patch(color='#e74c3c', label='Failure')
        ax.legend(handles=[success_patch, failure_patch], loc='upper right')
        
        plt.tight_layout()
        return fig

    @staticmethod
    def create_interactive_h3_map(h3_cells: List[str], 
                                 values: Optional[List[float]] = None,
                                 center: Optional[Tuple[float, float]] = None,
                                 zoom: int = 8,
                                 title: str = "H3 Cells Visualization") -> Optional[object]:
        """
        Create an interactive H3 cells visualization using Folium.
        
        Args:
            h3_cells: List of H3 cell identifiers
            values: Optional list of values associated with each cell
            center: Optional center coordinates (lat, lon)
            zoom: Initial zoom level
            title: Map title
            
        Returns:
            Folium map object or None if dependencies not available
        """
        if not HAS_GEO_DEPS:
            logger.warning("Geospatial dependencies not available for interactive maps")
            return None
        
        if not h3_cells:
            logger.warning("No H3 cells provided for visualization")
            return None
        
        # Determine map center
        if center is None:
            # Calculate center from first H3 cell
            lat, lon = h3.h3_to_geo(h3_cells[0])
            center = (lat, lon)
        
        # Create map
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')
        
        # Color scale for values
        if values:
            min_val, max_val = min(values), max(values)
            value_range = max_val - min_val if max_val != min_val else 1
        
        # Add H3 cells to map
        for i, cell in enumerate(h3_cells):
            # Get cell boundary
            boundary = h3.h3_to_geo_boundary(cell, geo_json=False)
            
            # Determine color
            if values and i < len(values):
                # Normalize value to 0-1 range for color mapping
                normalized_val = (values[i] - min_val) / value_range if value_range > 0 else 0.5
                color_intensity = int(255 * normalized_val)
                color = f'#{255-color_intensity:02x}{color_intensity:02x}00'
                popup_text = f'H3 Cell: {cell}<br/>Value: {values[i]:.3f}'
            else:
                color = '#3388ff'
                popup_text = f'H3 Cell: {cell}'
            
            # Add polygon to map
            folium.Polygon(
                locations=boundary,
                popup=popup_text,
                tooltip=f'Cell: {cell[:8]}...',
                color=color,
                weight=2,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # Add title
        title_html = f'''
                     <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        return m
    
    def generate_comprehensive_report(self, 
                                    status_data: Dict[str, Any],
                                    test_report_path: Optional[Union[str, Path]] = None,
                                    save_html: bool = True) -> str:
        """
        Generate a comprehensive HTML report with all visualizations.
        
        Args:
            status_data: Repository status data
            test_report_path: Optional path to test report
            save_html: Whether to save HTML report
            
        Returns:
            HTML content as string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate all visualizations
        status_figures = self.generate_status_dashboard(status_data, save_plots=True)
        
        test_figures = {}
        if test_report_path and Path(test_report_path).exists():
            test_figures = self.generate_test_results_analysis(test_report_path, save_plots=True)
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OSC Integration Comprehensive Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
                img {{ max-width: 100%; height: auto; }}
                .timestamp {{ color: #7f8c8d; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>OSC Integration Comprehensive Report</h1>
                <p class="timestamp">Generated: {timestamp}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>This comprehensive report provides detailed analysis of the OS Climate (OSC) integration 
                status, including repository health, test execution results, and system performance metrics.</p>
            </div>
        """
        
        # Add status visualizations
        if status_figures:
            html_content += """
            <div class="section">
                <h2>Repository Status Analysis</h2>
                <div class="grid">
            """
            
            for name, fig in status_figures.items():
                img_path = f"visualizations/status/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                html_content += f"""
                    <div>
                        <h3>{name.replace('_', ' ').title()}</h3>
                        <img src="{img_path}" alt="{name}">
                    </div>
                """
            
            html_content += "</div></div>"
        
        # Add test results visualizations
        if test_figures:
            html_content += """
            <div class="section">
                <h2>Test Execution Analysis</h2>
                <div class="grid">
            """
            
            for name, fig in test_figures.items():
                img_path = f"visualizations/tests/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                html_content += f"""
                    <div>
                        <h3>{name.replace('_', ' ').title()}</h3>
                        <img src="{img_path}" alt="{name}">
                    </div>
                """
            
            html_content += "</div></div>"
        
        html_content += """
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    <li>Monitor repository health metrics regularly</li>
                    <li>Install missing system dependencies (gfortran, GDAL) for full functionality</li>
                    <li>Consider Docker-based testing for consistent environments</li>
                    <li>Set up automated monitoring for repository changes</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        if save_html:
            report_path = self.output_dir / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(report_path, 'w') as f:
                f.write(html_content)
            logger.info(f"Comprehensive HTML report saved to {report_path}")
        
        return html_content


# Convenience function for quick visualization
def quick_status_visualization(status_data: Dict[str, Any], 
                              output_dir: str = "reports/visualizations") -> Dict[str, Figure]:
    """
    Quick function to generate status visualizations.
    
    Args:
        status_data: Repository status data
        output_dir: Output directory for visualizations
        
    Returns:
        Dictionary of matplotlib Figure objects
    """
    viz_engine = OSCVisualizationEngine(output_dir)
    return viz_engine.generate_status_dashboard(status_data)


def quick_test_visualization(test_report_path: Union[str, Path],
                            output_dir: str = "reports/visualizations") -> Dict[str, Figure]:
    """
    Quick function to generate test result visualizations.
    
    Args:
        test_report_path: Path to test report JSON
        output_dir: Output directory for visualizations
        
    Returns:
        Dictionary of matplotlib Figure objects
    """
    viz_engine = OSCVisualizationEngine(output_dir)
    return viz_engine.generate_test_results_analysis(test_report_path) 