#!/usr/bin/env python3
"""
Performance Benchmark Tests for H3 Module

Comprehensive performance benchmark tests that measure real H3 operation
performance with various data sizes, resolutions, and computational scenarios.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import unittest
import time
import numpy as np
import statistics
from pathlib import Path
from typing import List, Tuple, Dict, Any, Callable

# Import the h3 library directly
import h3


class TestH3PerformanceBenchmarks(unittest.TestCase):
    """
    Comprehensive performance benchmark tests for H3 operations.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_lat = 37.7749
        self.test_lng = -122.4194
        self.test_resolution = 9
        self.test_cell = '89283082e73ffff'
        
        # Performance thresholds (in seconds)
        self.thresholds = {
            'cell_conversion': 0.001,      # 1ms
            'boundary_extraction': 0.001,   # 1ms
            'area_calculation': 0.001,      # 1ms
            'grid_disk': 0.01,             # 10ms
            'grid_ring': 0.01,             # 10ms
            'path_finding': 0.01,          # 10ms
            'hierarchy_ops': 0.001,        # 1ms
            'large_grid': 0.1,             # 100ms
        }
        
        # Create output directory
        self.output_dir = Path(__file__).parent / 'outputs'
        self.output_dir.mkdir(exist_ok=True)
    
    def benchmark_operation(self, operation: Callable, *args, iterations: int = 1000) -> Dict[str, float]:
        """
        Benchmark a single operation.
        
        Args:
            operation: Function to benchmark
            *args: Arguments for the operation
            iterations: Number of iterations to run
            
        Returns:
            Dictionary with timing statistics
        """
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = operation(*args)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std': statistics.stdev(times) if len(times) > 1 else 0.0,
            'total': sum(times)
        }
    
    def test_cell_conversion_performance(self):
        """Test performance of coordinate to cell conversion."""
        # Benchmark latlng_to_cell
        stats = self.benchmark_operation(
            h3.latlng_to_cell, 
            self.test_lat, 
            self.test_lng, 
            self.test_resolution,
            iterations=10000
        )
        
        # Validate performance
        self.assertLess(stats['mean'], self.thresholds['cell_conversion'])
        self.assertGreater(stats['mean'], 0)
        self.assertGreater(stats['median'], 0)
        
        # Test cell_to_latlng performance
        stats2 = self.benchmark_operation(
            h3.cell_to_latlng,
            self.test_cell,
            iterations=10000
        )
        
        self.assertLess(stats2['mean'], self.thresholds['cell_conversion'])
        self.assertGreater(stats2['mean'], 0)
    
    def test_boundary_extraction_performance(self):
        """Test performance of cell boundary extraction."""
        # Benchmark boundary extraction
        stats = self.benchmark_operation(
            h3.cell_to_boundary,
            self.test_cell,
            iterations=5000
        )
        
        # Validate performance
        self.assertLess(stats['mean'], self.thresholds['boundary_extraction'])
        self.assertGreater(stats['mean'], 0)
        
        # Test boundary extraction again
        stats2 = self.benchmark_operation(
            h3.cell_to_boundary,
            self.test_cell,
            iterations=5000
        )
        
        self.assertLess(stats2['mean'], self.thresholds['boundary_extraction'])
        self.assertGreater(stats2['mean'], 0)
    
    def test_area_calculation_performance(self):
        """Test performance of cell area calculations."""
        # Benchmark area calculation
        stats = self.benchmark_operation(
            h3.cell_area,
            self.test_cell,
            iterations=10000
        )
        
        # Validate performance
        self.assertLess(stats['mean'], self.thresholds['area_calculation'])
        self.assertGreater(stats['mean'], 0)
        
        # Test edge length calculation
        stats2 = self.benchmark_operation(
            h3.average_hexagon_edge_length,
            self.test_resolution,
            iterations=10000
        )
        
        self.assertLess(stats2['mean'], self.thresholds['area_calculation'])
        self.assertGreater(stats2['mean'], 0)
        
        # Test edge length calculation
        stats3 = self.benchmark_operation(
            h3.average_hexagon_edge_length,
            self.test_resolution,
            iterations=10000
        )
        
        self.assertLess(stats3['mean'], self.thresholds['area_calculation'])
        self.assertGreater(stats3['mean'], 0)
    
    def test_grid_disk_performance(self):
        """Test performance of grid disk operations."""
        # Test different disk sizes
        for k in [1, 2, 3, 5]:
            stats = self.benchmark_operation(
                h3.grid_disk,
                self.test_cell,
                k,
                iterations=1000
            )
            
            # Validate performance scales reasonably
            self.assertLess(stats['mean'], self.thresholds['grid_disk'] * k)
            self.assertGreater(stats['mean'], 0)
            
            # Test grid ring performance
            stats2 = self.benchmark_operation(
                h3.grid_ring,
                self.test_cell,
                k,
                iterations=1000
            )
            
            self.assertLess(stats2['mean'], self.thresholds['grid_ring'] * k)
            self.assertGreater(stats2['mean'], 0)
    
    def test_path_finding_performance(self):
        """Test performance of path finding operations."""
        # Create test cells at different distances
        test_cells = [
            h3.latlng_to_cell(40.7128, -74.0060, 9),  # New York
            h3.latlng_to_cell(40.7589, -73.9851, 9),  # Brooklyn (closer)
            h3.latlng_to_cell(40.7505, -73.9934, 9),  # Manhattan (closer)
        ]
        
        for i in range(len(test_cells) - 1):
            start_cell = test_cells[i]
            end_cell = test_cells[i + 1]
            
            # Benchmark path finding
            stats = self.benchmark_operation(
                h3.grid_path_cells,
                start_cell,
                end_cell,
                iterations=500
            )
            
            # Validate performance
            self.assertLess(stats['mean'], self.thresholds['path_finding'])
            self.assertGreater(stats['mean'], 0)
            
            # Test distance calculation
            stats2 = self.benchmark_operation(
                h3.grid_distance,
                start_cell,
                end_cell,
                iterations=1000
            )
            
            self.assertLess(stats2['mean'], self.thresholds['path_finding'])
            self.assertGreater(stats2['mean'], 0)
    
    def test_hierarchy_operations_performance(self):
        """Test performance of hierarchy operations."""
        # Test parent-child operations
        child_cell = h3.latlng_to_cell(self.test_lat, self.test_lng, 11)
        parent_cell = h3.cell_to_parent(child_cell, 9)
        
        # Benchmark parent operation
        stats = self.benchmark_operation(
            h3.cell_to_parent,
            child_cell,
            9,
            iterations=5000
        )
        
        self.assertLess(stats['mean'], self.thresholds['hierarchy_ops'])
        self.assertGreater(stats['mean'], 0)
        
        # Benchmark children operation
        stats2 = self.benchmark_operation(
            h3.cell_to_children,
            parent_cell,
            11,
            iterations=1000
        )
        
        self.assertLess(stats2['mean'], self.thresholds['hierarchy_ops'])
        self.assertGreater(stats2['mean'], 0)
        
        # Test resolution operations
        stats3 = self.benchmark_operation(
            h3.get_resolution,
            child_cell,
            iterations=10000
        )
        
        self.assertLess(stats3['mean'], self.thresholds['hierarchy_ops'])
        self.assertGreater(stats3['mean'], 0)
    
    def test_large_grid_performance(self):
        """Test performance with large grid operations."""
        # Create large grid
        base_cell = h3.latlng_to_cell(0, 0, 5)
        
        # Benchmark large grid generation
        start_time = time.perf_counter()
        large_grid = h3.grid_disk(base_cell, 8)
        end_time = time.perf_counter()
        
        grid_time = end_time - start_time
        
        # Validate performance
        self.assertLess(grid_time, self.thresholds['large_grid'])
        self.assertGreater(len(large_grid), 100)  # Adjusted expectation
        
        # Benchmark area calculations on large grid
        sample_cells = large_grid[:100]
        
        start_time = time.perf_counter()
        areas = [h3.cell_area(cell) for cell in sample_cells]
        end_time = time.perf_counter()
        
        area_time = end_time - start_time
        
        # Validate performance
        self.assertLess(area_time, 0.1)  # Should complete within 100ms
        self.assertEqual(len(areas), 100)
        self.assertTrue(all(area > 0 for area in areas))
    
    def test_memory_efficiency(self):
        """Test memory efficiency of H3 operations."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        base_cell = h3.latlng_to_cell(0, 0, 4)
        large_grid = h3.grid_disk(base_cell, 6)
        
        # Generate boundaries for all cells
        boundaries = [h3.cell_to_boundary(cell) for cell in large_grid]
        
        # Calculate areas for all cells
        areas = [h3.cell_area(cell) for cell in large_grid]
        
        # Get memory usage after operations
        gc.collect()  # Force garbage collection
        final_memory = process.memory_info().rss
        
        # Calculate memory increase
        memory_increase = final_memory - initial_memory
        
        # Validate memory efficiency (should not exceed 100MB for this operation)
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # 100MB
        
        # Validate results
        self.assertGreater(len(large_grid), 100)
        self.assertEqual(len(boundaries), len(large_grid))
        self.assertEqual(len(areas), len(large_grid))
    
    def test_concurrent_operations_performance(self):
        """Test performance of concurrent H3 operations."""
        import threading
        import queue
        
        # Create test data
        test_cells = [
            h3.latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
            h3.latlng_to_cell(40.7128, -74.0060, 9),   # New York
            h3.latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
            h3.latlng_to_cell(51.5074, -0.1278, 9),    # London
        ]
        
        results_queue = queue.Queue()
        
        def worker(cell):
            """Worker function for concurrent operations."""
            try:
                # Perform multiple operations
                boundary = h3.cell_to_boundary(cell)
                area = h3.cell_area(cell)
                # Note: cell_perimeter doesn't exist in h3 library
                # Use grid_disk with k=1 to get neighbors
                neighbors = h3.grid_disk(cell, 1)
                
                results_queue.put({
                    'cell': cell,
                    'boundary_points': len(boundary),
                    'area': area,
                    'neighbors': len(neighbors)
                })
            except Exception as e:
                results_queue.put({'error': str(e), 'cell': cell})
        
        # Start concurrent threads
        threads = []
        start_time = time.perf_counter()
        
        for cell in test_cells:
            thread = threading.Thread(target=worker, args=(cell,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Validate concurrent performance
        self.assertEqual(len(results), len(test_cells))
        self.assertLess(total_time, 0.1)  # Should complete within 100ms
        
        # Validate results
        for result in results:
            self.assertNotIn('error', result)
            self.assertIn('cell', result)
            self.assertIn('boundary_points', result)
            self.assertIn('area', result)
            self.assertIn('neighbors', result)
            
            self.assertGreater(result['boundary_points'], 0)
            self.assertGreater(result['area'], 0)
            self.assertGreater(result['neighbors'], 0)
    
    def test_resolution_scaling_performance(self):
        """Test performance scaling across different resolutions."""
        resolutions = [7, 9, 11, 13]
        performance_data = {}
        
        for res in resolutions:
            cell = h3.latlng_to_cell(self.test_lat, self.test_lng, res)
            
            # Benchmark operations at this resolution
            stats = self.benchmark_operation(
                h3.cell_area,
                cell,
                iterations=1000
            )
            
            performance_data[res] = {
                'area_mean': stats['mean'],
                'cell': cell
            }
        
        # Validate that performance is reasonable across resolutions
        for res in resolutions:
            self.assertLess(performance_data[res]['area_mean'], 0.001)
            self.assertGreater(performance_data[res]['area_mean'], 0)
        
        # Test that higher resolutions don't have significantly worse performance
        # (they should be similar since we're doing the same operation)
        mean_performance = statistics.mean([
            performance_data[res]['area_mean'] for res in resolutions
        ])
        
        for res in resolutions:
            performance = performance_data[res]['area_mean']
            # Performance should be within 10x of the mean
            self.assertLess(performance, mean_performance * 10)
    
    def test_error_handling_performance(self):
        """Test performance of error handling scenarios."""
        # Test invalid input handling performance
        invalid_cells = ['invalid_cell', 'not_a_cell', '123456']
        
        for invalid_cell in invalid_cells:
            start_time = time.perf_counter()
            
            try:
                h3.cell_to_boundary(invalid_cell)
            except ValueError:
                pass
            
            end_time = time.perf_counter()
            error_time = end_time - start_time
            
            # Error handling should be fast
            self.assertLess(error_time, 0.001)  # 1ms
    
    def test_statistical_analysis_performance(self):
        """Test performance of statistical analysis operations."""
        # Create test dataset
        base_cell = h3.latlng_to_cell(0, 0, 6)
        test_cells = h3.grid_disk(base_cell, 3)
        
        # Benchmark spatial statistics
        start_time = time.perf_counter()
        stats = {
            'total_area': sum(h3.cell_area(cell) for cell in test_cells),
            'total_edge_length': sum(h3.average_hexagon_edge_length(6, unit='km') for _ in test_cells),
            'cell_count': len(test_cells)
        }
        end_time = time.perf_counter()
        
        stats_time = end_time - start_time
        
        # Validate performance
        self.assertLess(stats_time, 0.1)  # 100ms
        self.assertIsInstance(stats, dict)
        self.assertIn('total_area', stats)
        self.assertIn('total_edge_length', stats)
        self.assertIn('cell_count', stats)
        
        # Benchmark cell distribution analysis
        start_time = time.perf_counter()
        distribution = {
            'resolution_distribution': {h3.get_resolution(cell): 1 for cell in test_cells},
            'area_statistics': {
                'total_area': sum(h3.cell_area(cell) for cell in test_cells),
                'average_area': sum(h3.cell_area(cell) for cell in test_cells) / len(test_cells)
            }
        }
        end_time = time.perf_counter()
        
        dist_time = end_time - start_time
        
        # Validate performance
        self.assertLess(dist_time, 0.1)  # 100ms
        self.assertIsInstance(distribution, dict)
        self.assertIn('resolution_distribution', distribution)
        self.assertIn('area_statistics', distribution)


if __name__ == '__main__':
    unittest.main() 