#!/usr/bin/env python3
"""
Test script to demonstrate enhanced OSC reporting and visualization capabilities.
Using docxology forks of OS-Climate repos.
"""

import sys
import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

def test_enhanced_reporting():
    """Test the enhanced reporting functionality."""
    print("=== Testing Enhanced OSC Reporting with Visualizations ===\n")
    
    try:
        from geo_infer_space.osc_geo.utils.enhanced_reporting import generate_enhanced_status_report
        
        print("📊 Generating enhanced status report...")
        report = generate_enhanced_status_report(output_dir='reports')
        
        print("✅ Report generated successfully!\n")
        
        # Display results
        status_data = report.get('status_data', {})
        repositories = status_data.get('repositories', {})
        
        print(f"📈 Repository Analysis:")
        print(f"  - Total repositories: {len(repositories)}")
        
        for repo_name, repo_data in repositories.items():
            display_name = repo_name.replace('osc-geo-', '')
            exists = "✅" if repo_data.get('exists', False) else "❌"
            git_repo = "✅" if repo_data.get('is_git_repo', False) else "❌"
            has_venv = "✅" if repo_data.get('has_venv', False) else "❌"
            
            print(f"  - {display_name}:")
            print(f"    * Exists: {exists}")
            print(f"    * Git Repo: {git_repo}")
            print(f"    * Virtual Env: {has_venv}")
            print(f"    * Branch: {repo_data.get('current_branch', 'unknown')}")
        
        print(f"\n🌐 Generated Reports:")
        if 'html_dashboard' in report:
            print(f"  - HTML Dashboard: {report['html_dashboard']}")
        
        if 'visualizations' in report:
            print(f"  - Visualizations ({len(report['visualizations'])} charts):")
            for name, path in report['visualizations'].items():
                print(f"    * {name.replace('_', ' ').title()}: {path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📝 Note: Visualization dependencies may not be installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_status():
    """Test basic status checking functionality."""
    print("\n=== Testing Basic Status Functionality ===\n")
    
    try:
        from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status, generate_summary
        
        print("🔍 Checking repository status...")
        status = check_repo_status()
        summary = generate_summary(status)
        
        print("✅ Status check completed!\n")
        print("📋 Summary:")
        print(summary)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 OSC Integration Testing Suite")
    print("=" * 50)
    
    # Test basic functionality first
    basic_success = test_basic_status()
    
    # Test enhanced reporting
    enhanced_success = test_enhanced_reporting()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  - Basic Status Check: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    print(f"  - Enhanced Reporting: {'✅ PASSED' if enhanced_success else '❌ FAILED'}")
    
    if enhanced_success:
        print("\n🎉 Enhanced reporting with visualizations is working!")
        print("📁 Check the 'reports/' directory for generated files:")
        print("   - HTML dashboards for interactive viewing")
        print("   - PNG charts for documentation")
        print("   - JSON reports for programmatic access")
    else:
        print("\n⚠️  Enhanced reporting not available")
        print("💡 Install visualization dependencies: pip install matplotlib seaborn folium plotly")
    
    return basic_success and enhanced_success

if __name__ == "__main__":
    sys.exit(0 if main() else 1) 