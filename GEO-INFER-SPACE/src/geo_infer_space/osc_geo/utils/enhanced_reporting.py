"""
Enhanced reporting module for OSC integration with comprehensive visualizations.

This module extends the existing OSC reporting capabilities with rich visualizations,
interactive dashboards, and comprehensive analysis reports.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

try:
    from .visualization import OSCVisualizationEngine, quick_status_visualization, quick_test_visualization
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    logging.warning("Visualization module not available - running without visual enhancements")

try:
    from .osc_simple_status import check_repo_status, generate_summary
    HAS_STATUS_FUNCTIONS = True
except ImportError:
    HAS_STATUS_FUNCTIONS = False
    logging.warning("Status functions not available - running without status checking")

logger = logging.getLogger(__name__)


class EnhancedOSCReporter:
    """
    Enhanced OSC reporter that combines status checking with comprehensive visualizations.
    
    Provides:
    - Traditional text-based status reports
    - Rich visual dashboards and charts
    - Interactive HTML reports
    - Automated report generation
    """
    
    def __init__(self, 
                 output_dir: Union[str, Path] = "reports",
                 enable_visualizations: bool = True):
        """
        Initialize the enhanced OSC reporter.
        
        Args:
            output_dir: Base directory for all outputs
            enable_visualizations: Whether to generate visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_visualizations = enable_visualizations and HAS_VISUALIZATION
        
        if self.enable_visualizations:
            self.viz_engine = OSCVisualizationEngine(self.output_dir / "visualizations")
            logger.info("Enhanced OSC Reporter initialized with visualizations enabled")
        else:
            logger.info("Enhanced OSC Reporter initialized without visualizations")
    
    def generate_enhanced_status_report(self, 
                                      include_visualizations: bool = True,
                                      save_json: bool = True,
                                      save_html: bool = True) -> Dict[str, Any]:
        """
        Generate a comprehensive status report with optional visualizations.
        
        Args:
            include_visualizations: Whether to include visual analysis
            save_json: Whether to save JSON status data
            save_html: Whether to save HTML report
            
        Returns:
            Complete status report data
        """
        logger.info("Generating enhanced OSC status report...")
        
        # Get basic status data
        if HAS_STATUS_FUNCTIONS:
            status_data = check_repo_status()
            summary = generate_summary(status_data)
        else:
            status_data = {"error": "Status functions not available"}
            summary = "Status checking not available"
        
        # Add timestamp and metadata
        report_data = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "reporter_version": "enhanced_v1.0",
                "visualizations_enabled": self.enable_visualizations and include_visualizations
            },
            "status_data": status_data,
            "summary": summary
        }
        
        # Generate visualizations if enabled
        visualization_paths = {}
        if self.enable_visualizations and include_visualizations:
            try:
                viz_figures = self.viz_engine.generate_status_dashboard(status_data)
                
                # Save visualization paths for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                for name, fig in viz_figures.items():
                    viz_path = self.output_dir / "visualizations" / "status" / f"{name}_{timestamp}.png"
                    visualization_paths[name] = str(viz_path.relative_to(self.output_dir))
                
                report_data["visualizations"] = visualization_paths
                logger.info(f"Generated {len(viz_figures)} status visualizations")
                
            except Exception as e:
                logger.error(f"Error generating visualizations: {e}")
                report_data["visualization_error"] = str(e)
        
        # Save JSON report
        if save_json:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = self.output_dir / f"enhanced_status_report_{timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            logger.info(f"Enhanced status report saved to {json_path}")
        
        # Generate HTML report
        if save_html and self.enable_visualizations:
            try:
                html_content = self._generate_status_html_report(report_data)
                html_path = self.output_dir / f"status_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(html_path, 'w') as f:
                    f.write(html_content)
                logger.info(f"Interactive HTML dashboard saved to {html_path}")
                report_data["html_dashboard"] = str(html_path.relative_to(self.output_dir))
            except Exception as e:
                logger.error(f"Error generating HTML report: {e}")
        
        return report_data
    
    def analyze_test_results(self, 
                           test_report_path: Union[str, Path],
                           include_visualizations: bool = True,
                           save_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze test execution results with enhanced reporting.
        
        Args:
            test_report_path: Path to the test execution report
            include_visualizations: Whether to generate visual analysis
            save_analysis: Whether to save analysis results
            
        Returns:
            Test analysis results
        """
        logger.info(f"Analyzing test results from {test_report_path}")
        
        test_report_path = Path(test_report_path)
        if not test_report_path.exists():
            logger.error(f"Test report not found: {test_report_path}")
            return {"error": "Test report file not found"}
        
        # Load test data
        try:
            with open(test_report_path, 'r') as f:
                test_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing test report JSON: {e}")
            return {"error": "Invalid JSON in test report"}
        
        # Basic analysis
        analysis_data = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "source_report": str(test_report_path),
                "analyzer_version": "enhanced_v1.0"
            },
            "test_summary": self._analyze_test_execution(test_data),
            "dependency_analysis": self._analyze_dependencies(test_data),
            "performance_metrics": self._analyze_performance(test_data)
        }
        
        # Generate visualizations if enabled
        if self.enable_visualizations and include_visualizations:
            try:
                viz_figures = self.viz_engine.generate_test_results_analysis(test_report_path)
                
                # Record visualization paths
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                visualization_paths = {}
                for name, fig in viz_figures.items():
                    viz_path = self.output_dir / "visualizations" / "tests" / f"{name}_{timestamp}.png"
                    visualization_paths[name] = str(viz_path.relative_to(self.output_dir))
                
                analysis_data["visualizations"] = visualization_paths
                logger.info(f"Generated {len(viz_figures)} test analysis visualizations")
                
            except Exception as e:
                logger.error(f"Error generating test visualizations: {e}")
                analysis_data["visualization_error"] = str(e)
        
        # Save analysis
        if save_analysis:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_path = self.output_dir / f"test_analysis_{timestamp}.json"
            with open(analysis_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            logger.info(f"Test analysis saved to {analysis_path}")
        
        return analysis_data
    
    def _analyze_test_execution(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test execution results."""
        summary = {
            "overall_success": test_data.get("overall_success", False),
            "all_tests_passed": test_data.get("all_tests_passed", False),
            "total_repositories": 0,
            "successful_repositories": 0,
            "failed_repositories": 0,
            "step_analysis": {}
        }
        
        # Analyze repositories
        if "test_results" in test_data:
            test_results = test_data["test_results"]
            summary["total_repositories"] = len(test_results)
            
            for repo_name, repo_data in test_results.items():
                if repo_data.get("success", False):
                    summary["successful_repositories"] += 1
                else:
                    summary["failed_repositories"] += 1
        
        # Analyze steps
        if "steps" in test_data:
            for step in test_data["steps"]:
                step_name = step.get("name", "unknown")
                summary["step_analysis"][step_name] = {
                    "success": step.get("success", False),
                    "duration_seconds": self._calculate_step_duration(step)
                }
        
        return summary
    
    def _analyze_dependencies(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependency installation results."""
        analysis = {
            "common_failures": {},
            "successful_installations": {},
            "system_dependencies_missing": []
        }
        
        if "test_results" not in test_data:
            return analysis
        
        for repo_name, repo_data in test_data["test_results"].items():
            if "steps" in repo_data:
                for step in repo_data["steps"]:
                    if step.get("name") == "setup_script":
                        stderr = step.get("stderr", "")
                        stdout = step.get("stdout", "")
                        
                        # Analyze common failure patterns
                        if "gfortran" in stderr.lower() or "fortran" in stderr.lower():
                            analysis["system_dependencies_missing"].append("gfortran (Fortran compiler)")
                        if "gdal" in stderr.lower():
                            analysis["system_dependencies_missing"].append("GDAL libraries")
                        if "pkg-config" in stderr.lower():
                            analysis["system_dependencies_missing"].append("pkg-config")
                        
                        # Count specific package failures
                        if "scipy" in stderr:
                            analysis["common_failures"]["scipy"] = analysis["common_failures"].get("scipy", 0) + 1
                        if "rasterio" in stderr:
                            analysis["common_failures"]["rasterio"] = analysis["common_failures"].get("rasterio", 0) + 1
                        
                        # Track successful installations
                        for line in stdout.split('\n'):
                            if "Successfully installed" in line:
                                packages = line.split("Successfully installed ")[1].split()
                                for package in packages:
                                    pkg_name = package.split('-')[0] if '-' in package else package
                                    analysis["successful_installations"][pkg_name] = analysis["successful_installations"].get(pkg_name, 0) + 1
        
        # Remove duplicates from system dependencies
        analysis["system_dependencies_missing"] = list(set(analysis["system_dependencies_missing"]))
        
        return analysis
    
    def _analyze_performance(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics from test execution."""
        metrics = {
            "total_execution_time": 0,
            "step_durations": {},
            "repository_setup_times": {},
            "bottlenecks": []
        }
        
        # Calculate total execution time
        if "steps" in test_data and test_data["steps"]:
            first_step = test_data["steps"][0]
            last_step = test_data["steps"][-1]
            
            if "start_time" in first_step and "end_time" in last_step:
                try:
                    start_time = datetime.fromisoformat(first_step["start_time"])
                    end_time = datetime.fromisoformat(last_step["end_time"])
                    metrics["total_execution_time"] = (end_time - start_time).total_seconds()
                except ValueError:
                    pass
        
        # Analyze step durations
        if "steps" in test_data:
            for step in test_data["steps"]:
                step_name = step.get("name", "unknown")
                duration = self._calculate_step_duration(step)
                metrics["step_durations"][step_name] = duration
                
                # Identify bottlenecks (steps taking more than 60 seconds)
                if duration > 60:
                    metrics["bottlenecks"].append({
                        "step": step_name,
                        "duration": duration,
                        "success": step.get("success", False)
                    })
        
        return metrics
    
    def _calculate_step_duration(self, step: Dict[str, Any]) -> float:
        """Calculate duration of a step in seconds."""
        if "start_time" in step and "end_time" in step:
            try:
                start = datetime.fromisoformat(step["start_time"])
                end = datetime.fromisoformat(step["end_time"])
                return (end - start).total_seconds()
            except ValueError:
                pass
        return 0.0
    
    def _generate_status_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate an interactive HTML status report."""
        status_data = report_data.get("status_data", {})
        summary = report_data.get("summary", "No summary available")
        visualizations = report_data.get("visualizations", {})
        timestamp = report_data.get("report_metadata", {}).get("timestamp", "Unknown")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OSC Integration Status Dashboard</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f8f9fa;
                    color: #343a40;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin: 2rem 0;
                }}
                .card {{
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }}
                .card h3 {{
                    margin-top: 0;
                    color: #495057;
                }}
                .status-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .status-success {{ background-color: #28a745; }}
                .status-warning {{ background-color: #ffc107; }}
                .status-error {{ background-color: #dc3545; }}
                .visualization {{
                    text-align: center;
                    margin: 1rem 0;
                }}
                .visualization img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .summary-box {{
                    background: #e9ecef;
                    padding: 1rem;
                    border-radius: 6px;
                    margin: 1rem 0;
                    font-family: monospace;
                    font-size: 0.9rem;
                    white-space: pre-line;
                }}
                .metadata {{
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 6px;
                    font-size: 0.9rem;
                    color: #6c757d;
                }}
                .repo-list {{
                    list-style: none;
                    padding: 0;
                }}
                .repo-item {{
                    display: flex;
                    align-items: center;
                    padding: 0.5rem 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .repo-item:last-child {{
                    border-bottom: none;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 OSC Integration Status Dashboard</h1>
                <p>Comprehensive monitoring and analysis of OS Climate repository integration</p>
                <div class="metadata">Generated: {timestamp}</div>
            </div>
            
            <div class="container">
                <div class="card">
                    <h3>📊 Executive Summary</h3>
                    <div class="summary-box">{summary}</div>
                </div>
                
                <div class="grid">
        """
        
        # Add repository status cards
        if "repositories" in status_data:
            html_content += """
                    <div class="card">
                        <h3>📁 Repository Status</h3>
                        <ul class="repo-list">
            """
            
            for repo_name, repo_data in status_data["repositories"].items():
                exists = repo_data.get("exists", False)
                is_git = repo_data.get("is_git_repo", False)
                has_venv = repo_data.get("has_venv", False)
                
                # Determine overall status
                if exists and is_git and has_venv:
                    status_class = "status-success"
                    status_text = "Healthy"
                elif exists and is_git:
                    status_class = "status-warning"
                    status_text = "Partial"
                else:
                    status_class = "status-error"
                    status_text = "Issues"
                
                display_name = repo_name.replace("osc-geo-", "")
                
                html_content += f"""
                            <li class="repo-item">
                                <span class="status-indicator {status_class}"></span>
                                <strong>{display_name}</strong> - {status_text}
                                <br><small>Branch: {repo_data.get('current_branch', 'unknown')}</small>
                            </li>
                """
            
            html_content += """
                        </ul>
                    </div>
            """
        
        # Add visualizations
        if visualizations:
            for viz_name, viz_path in visualizations.items():
                display_name = viz_name.replace('_', ' ').title()
                html_content += f"""
                    <div class="card">
                        <h3>📈 {display_name}</h3>
                        <div class="visualization">
                            <img src="{viz_path}" alt="{display_name}">
                        </div>
                    </div>
                """
        
        html_content += """
                </div>
                
                <div class="card">
                    <h3>🔧 Recommendations</h3>
                    <ul>
                        <li><strong>System Dependencies:</strong> Install missing system libraries (gfortran, GDAL, pkg-config) for full functionality</li>
                        <li><strong>Monitoring:</strong> Set up automated monitoring for repository health and updates</li>
                        <li><strong>Docker:</strong> Consider Docker-based testing for consistent environments</li>
                        <li><strong>CI/CD:</strong> Implement continuous integration for automated testing</li>
                    </ul>
                </div>
                
                <div class="metadata">
                    <strong>Report Details:</strong><br>
                    Generated by Enhanced OSC Reporter v1.0<br>
                    Visualizations: {"Enabled" if visualizations else "Disabled"}<br>
                    Data Source: OSC Simple Status Check
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_comprehensive_report(self, 
                                   test_report_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report combining status and test analysis.
        
        Args:
            test_report_path: Optional path to test execution report
            
        Returns:
            Complete comprehensive report data
        """
        logger.info("Generating comprehensive OSC integration report...")
        
        # Generate status report
        status_report = self.generate_enhanced_status_report()
        
        # Generate test analysis if test report provided
        test_analysis = None
        if test_report_path:
            test_analysis = self.analyze_test_results(test_report_path)
        
        # Combine reports
        comprehensive_report = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "report_type": "comprehensive",
                "components": ["status_analysis", "test_analysis"] if test_analysis else ["status_analysis"]
            },
            "status_report": status_report,
            "test_analysis": test_analysis
        }
        
        # Generate comprehensive HTML report
        if self.enable_visualizations:
            try:
                html_content = self.viz_engine.generate_comprehensive_report(
                    status_report["status_data"],
                    test_report_path
                )
                
                html_path = self.output_dir / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(html_path, 'w') as f:
                    f.write(html_content)
                
                comprehensive_report["comprehensive_html"] = str(html_path.relative_to(self.output_dir))
                logger.info(f"Comprehensive HTML report saved to {html_path}")
                
            except Exception as e:
                logger.error(f"Error generating comprehensive HTML report: {e}")
        
        # Save comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"comprehensive_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        logger.info(f"Comprehensive report saved to {report_path}")
        
        return comprehensive_report


# Convenience functions for quick enhanced reporting
def generate_enhanced_status_report(output_dir: str = "reports") -> Dict[str, Any]:
    """
    Quick function to generate an enhanced status report.
    
    Args:
        output_dir: Output directory for reports
        
    Returns:
        Enhanced status report data
    """
    reporter = EnhancedOSCReporter(output_dir)
    return reporter.generate_enhanced_status_report()


def generate_enhanced_test_analysis(test_report_path: Union[str, Path],
                                  output_dir: str = "reports") -> Dict[str, Any]:
    """
    Quick function to generate enhanced test analysis.
    
    Args:
        test_report_path: Path to test execution report
        output_dir: Output directory for analysis
        
    Returns:
        Enhanced test analysis data
    """
    reporter = EnhancedOSCReporter(output_dir)
    return reporter.analyze_test_results(test_report_path)


def generate_comprehensive_osc_report(test_report_path: Optional[Union[str, Path]] = None,
                                    output_dir: str = "reports") -> Dict[str, Any]:
    """
    Quick function to generate a comprehensive OSC integration report.
    
    Args:
        test_report_path: Optional path to test execution report
        output_dir: Output directory for reports
        
    Returns:
        Comprehensive report data
    """
    reporter = EnhancedOSCReporter(output_dir)
    return reporter.generate_comprehensive_report(test_report_path) 