#!/usr/bin/env python3
"""
Basic example demonstrating GEO-INFER-TEST usage with LOG integration.

This example shows how to:
1. Configure and run tests across multiple modules
2. Integrate with GEO-INFER-LOG for comprehensive logging
3. Generate detailed test reports
4. Monitor module health and performance
"""

import sys
import time
from pathlib import Path

# Add the GEO-INFER-TEST module to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from geo_infer_test import GeoInferTestRunner, TestConfiguration
    from geo_infer_test.core import LogIntegration, LoggingTestReporter
    from geo_infer_test.utils import TestHelpers
except ImportError as e:
    print(f"Error importing GEO-INFER-TEST modules: {e}")
    print("Please ensure GEO-INFER-TEST is properly installed")
    sys.exit(1)


def main():
    """Main function demonstrating comprehensive testing with LOG integration."""
    
    print("🧪 GEO-INFER-TEST Example: Comprehensive Module Testing")
    print("=" * 60)
    
    # 1. Configure logging integration
    print("\n1. Setting up LOG integration...")
    log_config = {
        'level': 'INFO',
        'log_dir': 'example_logs',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
    
    log_integration = LogIntegration(log_config)
    print(f"   ✅ Logging initialized (LOG module available: {log_integration.log_available})")
    
    # 2. Configure test execution
    print("\n2. Configuring test execution...")
    config = TestConfiguration(
        modules_to_test=['SPACE', 'TIME', 'MATH'],  # Start with core modules
        test_types=['unit', 'integration'],
        parallel_execution=True,
        max_workers=2,
        timeout_seconds=30,
        fail_fast=False,
        coverage_enabled=True,
        log_integration_enabled=True
    )
    
    print(f"   ✅ Testing configured for modules: {config.modules_to_test}")
    print(f"   ✅ Test types: {config.test_types}")
    
    # 3. Initialize test runner
    print("\n3. Initializing test runner...")
    runner = GeoInferTestRunner(config)
    runner.log_integration = log_integration
    
    # 4. Discover available tests
    print("\n4. Discovering tests...")
    discovered_tests = runner.discover_tests()
    
    total_tests = sum(len(tests) for tests in discovered_tests.values())
    print(f"   ✅ Discovered {total_tests} tests across {len(discovered_tests)} modules")
    
    for module, tests in discovered_tests.items():
        print(f"      {module}: {len(tests)} tests")
    
    # 5. Demonstrate LOG integration with test context
    print("\n5. Demonstrating LOG integration...")
    with log_integration.test_context("demo_001", "TEST", "log_integration_demo"):
        print("   📝 Test execution being logged...")
        time.sleep(0.5)  # Simulate test work
        
        # Log some performance metrics
        test_logger = log_integration.TestLogger(log_integration)
        test_logger.log_performance_metrics("demo_001", {
            'execution_time': 0.5,
            'memory_usage_mb': 125.3,
            'operations_per_second': 1000
        })
        
        print("   ✅ Test logged successfully")
    
    # 6. Run a subset of tests (simulated)
    print("\n6. Running simulated tests...")
    start_time = time.time()
    
    # Simulate test execution with LOG integration
    test_results = []
    
    for module in ['SPACE', 'TIME']:
        for test_type in ['unit']:
            test_id = f"{module}_{test_type}_example"
            
            with log_integration.test_context(test_id, module, f"{test_type}_test"):
                # Simulate test execution
                execution_time = 0.1 + (hash(test_id) % 1000) / 10000
                time.sleep(execution_time)
                
                # Simulate occasional failures
                success = hash(test_id) % 10 != 0  # 90% success rate
                
                if not success:
                    raise Exception("Simulated test failure")
                
                print(f"   ✅ {test_id} passed ({execution_time:.3f}s)")
    
    execution_time = time.time() - start_time
    print(f"   ✅ Test execution completed in {execution_time:.2f}s")
    
    # 7. Generate comprehensive report
    print("\n7. Generating test report...")
    reporter = LoggingTestReporter(log_integration)
    report_data = reporter.generate_test_report(Path("example_reports"))
    
    print(f"   ✅ Report generated with {len(log_integration.test_entries)} test entries")
    print(f"   📊 Success rate: {report_data['summary']['success_rate']:.1f}%")
    
    # 8. Analyze test patterns
    print("\n8. Analyzing test patterns...")
    from geo_infer_test.core.log_integration import LogAnalyzer
    
    analyzer = LogAnalyzer(log_integration)
    analysis = analyzer.analyze_test_patterns()
    
    if analysis:
        print(f"   📈 Analyzed {analysis['total_tests_analyzed']} test executions")
        
        if analysis['module_reliability']:
            print("   Module reliability scores:")
            for module, metrics in analysis['module_reliability'].items():
                print(f"      {module}: {metrics['success_rate']:.1f}% success, "
                      f"{metrics['avg_duration']:.3f}s avg duration")
    
    # 9. Check for performance bottlenecks
    print("\n9. Checking for performance issues...")
    bottlenecks = analyzer.identify_performance_bottlenecks()
    
    if bottlenecks:
        print(f"   ⚠️  Found {len(bottlenecks)} potential performance bottlenecks:")
        for bottleneck in bottlenecks[:3]:  # Show top 3
            print(f"      {bottleneck['test_name']}: {bottleneck['duration']:.3f}s "
                  f"({bottleneck['slowness_factor']:.1f}x slower than average)")
    else:
        print("   ✅ No significant performance bottlenecks detected")
    
    # 10. Summary
    print("\n" + "=" * 60)
    print("🎉 GEO-INFER-TEST Example Complete!")
    print("\nKey capabilities demonstrated:")
    print("✅ LOG integration for comprehensive test tracking")
    print("✅ Automated test discovery and execution")
    print("✅ Performance monitoring and analysis")
    print("✅ Comprehensive reporting with multiple formats")
    print("✅ Pattern analysis and bottleneck detection")
    print("\nNext steps:")
    print("- Configure real module tests in your environment")
    print("- Set up automated CI/CD integration")
    print("- Customize reporting and alerting")
    print("- Explore advanced testing features")


def demo_cross_module_testing():
    """Demonstrate cross-module integration testing capabilities."""
    
    print("\n🔗 Cross-Module Integration Testing Demo")
    print("-" * 40)
    
    # This would demonstrate testing interactions between modules
    modules_to_test = [
        ('SPACE', 'TIME'),  # Spatial-temporal integration
        ('AI', 'SPACE'),    # AI with spatial data
        ('API', 'DATA'),    # API data access
    ]
    
    for module_a, module_b in modules_to_test:
        print(f"   🔄 Testing {module_a} <-> {module_b} integration")
        # In a real implementation, this would test actual module interactions
        time.sleep(0.1)
        print(f"   ✅ {module_a} <-> {module_b} integration verified")


def demo_health_monitoring():
    """Demonstrate module health monitoring capabilities."""
    
    print("\n🏥 Module Health Monitoring Demo")
    print("-" * 40)
    
    # Simulate health checks for various modules
    modules = ['SPACE', 'TIME', 'AI', 'DATA', 'API']
    
    for module in modules:
        # Simulate health check
        response_time = 0.05 + (hash(module) % 100) / 1000
        is_healthy = response_time < 0.1
        
        status = "✅ Healthy" if is_healthy else "⚠️  Slow"
        print(f"   {module}: {status} ({response_time:.3f}s)")


if __name__ == "__main__":
    try:
        main()
        demo_cross_module_testing()
        demo_health_monitoring()
        
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nExample completed.") 