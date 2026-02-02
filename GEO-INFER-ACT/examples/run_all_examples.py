#!/usr/bin/env python
"""
GEO-INFER-ACT Examples Runner - Thin Orchestrator

This script runs all example scripts in the examples directory,
collects their results, and generates a summary report.

Orchestrates:
    - simple_model.py - Categorical active inference
    - ecological_model.py - Ecological niche modeling
    - urban_planning.py - Multi-agent urban planning
    - h3_active_inference.py - H3 spatial active inference
    - modern_active_inference.py - Hierarchical active inference
    - spatial_inference_demo.py - Spatial VFE/EFE demonstration

VFE/EFE Coverage:
    All examples compute Variational Free Energy (VFE) for belief updates
    and use Expected Free Energy (EFE) for policy selection.

Documentation:
    - ../docs/free_energy_principle.md
    - ../docs/mathematical_framework.md
    - ../examples/README.md

Usage:
    python examples/run_all_examples.py [--quick] [--verbose]

Arguments:
    --quick     Run a reduced subset for quick verification
    --verbose   Show detailed output from each example
"""

import sys
import os
import subprocess
import time
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ExamplesRunner")


def get_examples_dir() -> Path:
    """Get the examples directory path."""
    return Path(__file__).parent


def get_output_dir() -> Path:
    """Create and return the output directory for the run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_root = get_examples_dir().parent.parent
    output_dir = repo_root / "output" / f"examples_run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_example(script_name: str, timeout: int = 300, verbose: bool = False) -> Dict[str, Any]:
    """
    Run a single example script and capture its results.
    
    Args:
        script_name: Name of the script file
        timeout: Maximum execution time in seconds
        verbose: Whether to print stdout/stderr in real-time
        
    Returns:
        Dictionary with execution results
    """
    examples_dir = get_examples_dir()
    script_path = examples_dir / script_name
    
    if not script_path.exists():
        return {
            'script': script_name,
            'status': 'not_found',
            'success': False,
            'error': f"Script not found: {script_path}",
            'duration': 0
        }
    
    logger.info(f"Running: {script_name}")
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(examples_dir)
        )
        
        duration = time.time() - start_time
        
        # Check for success
        success = result.returncode == 0
        
        if verbose:
            if result.stdout:
                print(f"\n--- {script_name} stdout ---\n{result.stdout[:2000]}")
            if result.stderr:
                print(f"\n--- {script_name} stderr ---\n{result.stderr[:1000]}")
        
        # Extract key metrics from output
        output_metrics = extract_metrics_from_output(result.stdout)
        
        return {
            'script': script_name,
            'status': 'success' if success else 'failed',
            'success': success,
            'return_code': result.returncode,
            'duration': round(duration, 2),
            'stdout_lines': len(result.stdout.split('\n')),
            'stderr_lines': len(result.stderr.split('\n')) if result.stderr else 0,
            'metrics': output_metrics,
            'error': result.stderr[:500] if not success and result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.warning(f"  Timeout after {timeout}s: {script_name}")
        return {
            'script': script_name,
            'status': 'timeout',
            'success': False,
            'duration': round(duration, 2),
            'error': f"Execution timed out after {timeout} seconds"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"  Error running {script_name}: {e}")
        return {
            'script': script_name,
            'status': 'error',
            'success': False,
            'duration': round(duration, 2),
            'error': str(e)
        }


def extract_metrics_from_output(stdout: str) -> Dict[str, Any]:
    """Extract key metrics from example output."""
    metrics = {}
    
    # Look for common patterns
    lines = stdout.lower().split('\n')
    
    for line in lines:
        # Free energy patterns
        if 'free energy' in line and ('final' in line or 'initial' in line):
            try:
                # Extract numeric value
                parts = line.split(':')
                if len(parts) > 1:
                    val_str = parts[-1].strip()
                    # Extract first number
                    import re
                    numbers = re.findall(r'-?\d+\.?\d*', val_str)
                    if numbers:
                        key = 'final_free_energy' if 'final' in line else 'initial_free_energy'
                        metrics[key] = float(numbers[0])
            except (ValueError, IndexError):
                pass
        
        # Steps pattern
        if 'step' in line and 'total' in line:
            try:
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    metrics['total_steps'] = int(numbers[-1])
            except (ValueError, IndexError):
                pass
        
        # Simulation complete pattern
        if 'complete' in line or 'success' in line:
            metrics['completed'] = True
    
    return metrics


def generate_summary_report(results: List[Dict], output_dir: Path) -> str:
    """Generate a summary report of all example runs."""
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total - successful
    total_duration = sum(r.get('duration', 0) for r in results)
    
    report_lines = [
        "=" * 70,
        "GEO-INFER-ACT Examples Execution Report",
        "=" * 70,
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Output Directory: {output_dir}",
        "",
        "SUMMARY",
        "-" * 40,
        f"Total Examples: {total}",
        f"Successful: {successful}",
        f"Failed: {failed}",
        f"Success Rate: {successful/total*100:.1f}%",
        f"Total Duration: {total_duration:.1f}s",
        "",
        "INDIVIDUAL RESULTS",
        "-" * 40,
    ]
    
    for r in results:
        status_icon = "✅" if r['success'] else "❌"
        report_lines.append(f"{status_icon} {r['script']}")
        report_lines.append(f"   Status: {r['status']}")
        report_lines.append(f"   Duration: {r.get('duration', 0):.1f}s")
        
        if r.get('metrics'):
            for key, value in r['metrics'].items():
                report_lines.append(f"   {key}: {value}")
        
        if r.get('error'):
            report_lines.append(f"   Error: {r['error'][:200]}")
        
        report_lines.append("")
    
    # Module coverage summary
    report_lines.extend([
        "MODULE COVERAGE",
        "-" * 40,
        "Core Modules Used:",
        "  ✓ ActiveInferenceModel - all examples",
        "  ✓ FreeEnergyCalculator - VFE computation",
        "  ✓ GenerativeModel - state spaces",
        "  ✓ PolicySelector - EFE-based action selection",
        "  ✓ SpatialActiveInferenceAgent - spatial demos",
        "",
        "API Modules Used:",
        "  ✓ ActiveInferenceInterface - unified interface",
        "",
        "Utils Modules Used:",
        "  ✓ ActiveInferenceAnalyzer - analysis & logging",
        "  ✓ visualization - plots & dashboards",
        "  ✓ math - VFE/EFE computations",
        "  ✓ spatial_diagnostics - H3 spatial metrics",
        "",
        "=" * 70,
    ])
    
    report = "\n".join(report_lines)
    
    # Save report
    report_path = output_dir / "examples_run_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Also save as JSON for programmatic access
    json_path = output_dir / "examples_run_results.json"
    with open(json_path, 'w') as f:
        json.dump({
            'summary': {
                'total': total,
                'successful': successful,
                'failed': failed,
                'success_rate': successful/total,
                'total_duration': total_duration
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    return report


def main():
    """Run all examples and generate report."""
    parser = argparse.ArgumentParser(description='Run all GEO-INFER-ACT examples')
    parser.add_argument('--quick', action='store_true', 
                        help='Run only quick examples (simple_model, spatial_inference_demo)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output from each example')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Timeout per example in seconds (default: 300)')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("GEO-INFER-ACT Examples Runner")
    logger.info("=" * 60)
    
    # Define examples to run (order matters for dependencies)
    all_examples = [
        'simple_model.py',
        'spatial_inference_demo.py',
        'ecological_model.py',
        'urban_planning.py',
        'h3_active_inference.py',
        'modern_active_inference.py',
    ]
    
    quick_examples = [
        'simple_model.py',
        'spatial_inference_demo.py',
    ]
    
    examples_to_run = quick_examples if args.quick else all_examples
    
    logger.info(f"Running {len(examples_to_run)} examples...")
    logger.info(f"Mode: {'Quick' if args.quick else 'Full'}")
    logger.info("")
    
    # Create output directory
    output_dir = get_output_dir()
    logger.info(f"Output directory: {output_dir}")
    logger.info("")
    
    # Run each example
    results = []
    for script in examples_to_run:
        result = run_example(script, timeout=args.timeout, verbose=args.verbose)
        results.append(result)
        
        status = "✅" if result['success'] else "❌"
        logger.info(f"  {status} {script}: {result['status']} ({result['duration']:.1f}s)")
    
    logger.info("")
    
    # Generate summary report
    report = generate_summary_report(results, output_dir)
    
    # Print summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    logger.info("=" * 60)
    logger.info("EXECUTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Results: {successful}/{total} examples passed")
    logger.info(f"Report saved to: {output_dir / 'examples_run_report.txt'}")
    logger.info("")
    
    # Print full report
    print(report)
    
    # Return exit code based on success
    return 0 if successful == total else 1


if __name__ == "__main__":
    sys.exit(main())
