#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performance optimization utilities for GEO-INFER-GIT.

This module provides functionality for optimizing large-scale repository
operations including memory management, caching, and performance monitoring.
"""

import os
import time
import psutil
import threading
import functools
from typing import Dict, Any, Optional, Callable, List, cast
from dataclasses import dataclass, field
import gc
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""

    operation_name: str
    start_time: float
    end_time: float = 0.0
    memory_start: int = 0
    memory_end: int = 0
    cpu_percent: float = 0.0
    disk_io: Dict[str, int] = field(default_factory=dict)
    network_io: Dict[str, int] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        return self.end_time - self.start_time if self.end_time > 0 else 0.0

    @property
    def memory_used(self) -> int:
        """Get memory used during operation."""
        return self.memory_end - self.memory_start

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'operation': self.operation_name,
            'duration_seconds': self.duration,
            'memory_used_mb': self.memory_used / (1024 * 1024),
            'cpu_percent': self.cpu_percent,
            'disk_io': self.disk_io,
            'network_io': self.network_io,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0
        }

class PerformanceMonitor:
    """
    Monitor performance metrics for operations.

    Tracks memory usage, CPU usage, disk I/O, and other performance metrics
    for optimization and debugging purposes.
    """

    def __init__(self, enable_monitoring: bool = True):
        """
        Initialize performance monitor.

        Args:
            enable_monitoring: Whether to enable detailed monitoring
        """
        self.enable_monitoring = enable_monitoring
        self.metrics: Dict[str, Any] = {}
        self.lock = threading.Lock()

        if enable_monitoring:
            self._start_monitoring()

    def _start_monitoring(self) -> None:
        """Start background monitoring."""
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            try:
                # Collect system metrics every 5 seconds
                time.sleep(5)

                # Update process metrics
                process = psutil.Process()
                with self.lock:
                    for operation_name, metrics in self.metrics.items():
                        if metrics.end_time == 0:  # Operation still running
                            metrics.memory_end = process.memory_info().rss
                            metrics.cpu_percent = process.cpu_percent()

            except Exception as e:
                logger.warning(f"Performance monitoring error: {e}")
                break

    def start_operation(self, operation_name: str) -> PerformanceMetrics:
        """
        Start monitoring an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            PerformanceMetrics object for the operation
        """
        if not self.enable_monitoring:
            return PerformanceMetrics(operation_name, time.time())

        process = psutil.Process()

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            memory_start=process.memory_info().rss,
            cpu_percent=process.cpu_percent()
        )

        with self.lock:
            self.metrics[operation_name] = metrics

        return metrics

    def end_operation(self, operation_name: str) -> Optional[PerformanceMetrics]:
        """
        End monitoring an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Completed PerformanceMetrics object
        """
        with self.lock:
            if operation_name in self.metrics:
                metrics = self.metrics[operation_name]
                metrics.end_time = time.time()

                # Update final metrics
                process = psutil.Process()
                metrics.memory_end = process.memory_info().rss
                metrics.cpu_percent = process.cpu_percent()

                # Remove from active metrics
                del self.metrics[operation_name]

                return cast(PerformanceMetrics, metrics)

        return None

    def get_metrics(self, operation_name: str) -> Optional[PerformanceMetrics]:
        """Get metrics for an operation."""
        with self.lock:
            return self.metrics.get(operation_name)

    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get all current metrics."""
        with self.lock:
            return self.metrics.copy()

class MemoryManager:
    """
    Memory management utilities for large-scale operations.

    Provides functionality for:
    - Memory usage monitoring
    - Garbage collection optimization
    - Memory-efficient data structures
    - Memory leak detection
    """

    def __init__(self, max_memory_mb: int = 1024, gc_threshold_mb: int = 512):
        """
        Initialize memory manager.

        Args:
            max_memory_mb: Maximum memory usage in MB before warnings
            gc_threshold_mb: Memory threshold in MB for triggering GC
        """
        self.max_memory_mb = max_memory_mb
        self.gc_threshold_mb = gc_threshold_mb
        self.process = psutil.Process()

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage information.

        Returns:
            Dictionary with memory usage details
        """
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'memory_percent': memory_percent,
            'available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'total_mb': psutil.virtual_memory().total / (1024 * 1024)
        }

    def should_trigger_gc(self) -> bool:
        """
        Check if garbage collection should be triggered.

        Returns:
            True if GC should be triggered
        """
        memory_usage = self.get_memory_usage()
        return bool(memory_usage['rss_mb'] > self.gc_threshold_mb)

    def trigger_gc(self, force: bool = False) -> Dict[str, Any]:
        """
        Trigger garbage collection if needed.

        Args:
            force: Force garbage collection regardless of threshold

        Returns:
            Dictionary with GC results
        """
        if not force and not self.should_trigger_gc():
            return {'triggered': False, 'reason': 'below_threshold'}

        # Record memory before GC
        before_memory = self.get_memory_usage()

        # Trigger garbage collection
        gc.collect()

        # Record memory after GC
        after_memory = self.get_memory_usage()

        # Force garbage collection on all objects
        gc.collect()
        gc.collect()

        memory_freed = before_memory['rss_mb'] - after_memory['rss_mb']

        result = {
            'triggered': True,
            'memory_before_mb': before_memory['rss_mb'],
            'memory_after_mb': after_memory['rss_mb'],
            'memory_freed_mb': memory_freed,
            'forced': force
        }

        if memory_freed > 0:
            logger.info(f"Garbage collection freed {memory_freed:.2f} MB of memory")

        return result

    def check_memory_pressure(self) -> Dict[str, Any]:
        """
        Check for memory pressure and return recommendations.

        Returns:
            Dictionary with memory pressure analysis
        """
        memory_usage = self.get_memory_usage()

        pressure_level = "low"
        recommendations = []

        if memory_usage['memory_percent'] > 80:
            pressure_level = "high"
            recommendations.append("Consider reducing batch sizes")
            recommendations.append("Enable memory-efficient processing modes")
        elif memory_usage['memory_percent'] > 60:
            pressure_level = "medium"
            recommendations.append("Monitor memory usage closely")
            recommendations.append("Consider enabling automatic GC")

        if memory_usage['rss_mb'] > self.max_memory_mb:
            pressure_level = "critical"
            recommendations.append("High memory usage detected")
            recommendations.append("Consider processing in smaller batches")

        return {
            'pressure_level': pressure_level,
            'memory_usage': memory_usage,
            'recommendations': recommendations,
            'should_reduce_batch_size': pressure_level in ['high', 'critical']
        }

class CacheManager:
    """
    Caching utilities for performance optimization.

    Provides intelligent caching for:
    - API responses
    - Repository metadata
    - Configuration data
    - Computation results
    """

    def __init__(self, max_cache_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache manager.

        Args:
            max_cache_size: Maximum number of cached items
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()

    def get(self, key: str) -> Any:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self.miss_count += 1
                return None

            # Check if item has expired
            if time.time() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                self.miss_count += 1
                return None

            # Update access time and hit count
            self.access_times[key] = time.time()
            self.hit_count += 1

            # Move to end (most recently used)
            value = self.cache[key]
            del self.cache[key]
            self.cache[key] = value

            return value

    def put(self, key: str, value: Any) -> None:
        """
        Put item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # Remove oldest items if cache is full
            if len(self.cache) >= self.max_cache_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = value
            self.access_times[key] = time.time()

    def clear(self) -> None:
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0.0

        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }

class BatchProcessor:
    """
    Batch processing utilities for large-scale operations.

    Provides functionality for:
    - Dynamic batch sizing based on system resources
    - Memory-efficient batch processing
    - Progress tracking for large operations
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None,
                 performance_monitor: Optional[PerformanceMonitor] = None) -> None:
        """
        Initialize batch processor.

        Args:
            memory_manager: Memory manager instance
            performance_monitor: Performance monitor instance
        """
        self.memory_manager = memory_manager or MemoryManager()
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        self.batch_history: List[Any] = []

    def calculate_optimal_batch_size(self, item_size_bytes: int, target_memory_mb: int = 512) -> int:
        """
        Calculate optimal batch size based on memory constraints.

        Args:
            item_size_bytes: Average size of items in bytes
            target_memory_mb: Target memory usage in MB

        Returns:
            Optimal batch size
        """
        # Reserve memory for overhead (30% buffer)
        available_memory = target_memory_mb * 0.7 * 1024 * 1024

        # Calculate batch size
        batch_size = int(available_memory / item_size_bytes)

        # Ensure reasonable bounds
        batch_size = max(1, min(batch_size, 1000))

        # Check memory pressure and adjust
        pressure = self.memory_manager.check_memory_pressure()
        if pressure['should_reduce_batch_size']:
            batch_size = max(1, batch_size // 2)

        return batch_size

    def process_in_batches(self, items: List[Any], processor: Callable[[List[Any]], Any],
                          batch_size: Optional[int] = None, show_progress: bool = True) -> List[Any]:
        """
        Process items in batches with memory management.

        Args:
            items: List of items to process
            processor: Function to process each batch
            batch_size: Batch size (calculated if None)
            show_progress: Whether to show progress

        Returns:
            List of processed results
        """
        if not items:
            return []

        # Calculate batch size if not provided
        if batch_size is None:
            avg_item_size = 1024  # Assume 1KB per item
            batch_size = self.calculate_optimal_batch_size(avg_item_size)

        results = []
        total_items = len(items)

        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]

            # Trigger GC if needed before processing large batches
            if len(batch) > 100:
                self.memory_manager.trigger_gc()

            # Process batch
            try:
                batch_results = processor(batch)
                results.extend(batch_results if isinstance(batch_results, list) else [batch_results])

                # Update batch history
                self.batch_history.append({
                    'batch_size': len(batch),
                    'processing_time': time.time(),
                    'memory_mb': self.memory_manager.get_memory_usage()['rss_mb']
                })

            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                # Continue with next batch
                continue

        return results

    def get_batch_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics."""
        if not self.batch_history:
            return {'total_batches': 0}

        total_batches = len(self.batch_history)
        avg_batch_size = sum(batch['batch_size'] for batch in self.batch_history) / total_batches
        avg_memory = sum(batch['memory_mb'] for batch in self.batch_history) / total_batches

        return {
            'total_batches': total_batches,
            'avg_batch_size': avg_batch_size,
            'avg_memory_mb': avg_memory,
            'memory_efficiency': avg_memory / max(avg_batch_size, 1)
        }

class ResourceManager:
    """
    Resource management utilities for system optimization.

    Provides functionality for:
    - System resource monitoring
    - Adaptive resource allocation
    - Performance-based scaling
    """

    def __init__(self) -> None:
        """Initialize resource manager."""
        self.baseline_cpu = psutil.cpu_count()
        self.baseline_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # GB

    def get_system_load(self) -> Dict[str, Any]:
        """
        Get current system load information.

        Returns:
            Dictionary with system load metrics
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024 * 1024 * 1024),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024 * 1024 * 1024),
            'network_bytes_sent': network.bytes_sent,
            'network_bytes_recv': network.bytes_recv,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }

    def calculate_optimal_workers(self, operation_complexity: str = 'medium') -> int:
        """
        Calculate optimal number of workers based on system resources.

        Args:
            operation_complexity: Complexity level (low, medium, high)

        Returns:
            Optimal number of workers
        """
        system_load = self.get_system_load()

        # Base calculation on CPU cores
        base_workers = max(1, self.baseline_cpu - 1)  # Reserve one core for system

        # Adjust based on memory availability
        memory_factor = min(1.0, system_load['memory_available_gb'] / 4.0)  # Assume 4GB baseline

        # Adjust based on system load
        load_factor = 1.0 - (system_load['cpu_percent'] / 100.0)

        # Complexity multipliers
        complexity_multipliers = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.2
        }

        multiplier = complexity_multipliers.get(operation_complexity, 1.0)

        optimal_workers = int(base_workers * memory_factor * load_factor * multiplier)

        # Ensure reasonable bounds
        optimal_workers = max(1, min(optimal_workers, 16))

        return optimal_workers

    def should_throttle_operations(self) -> bool:
        """
        Check if operations should be throttled due to high system load.

        Returns:
            True if operations should be throttled
        """
        system_load = self.get_system_load()

        # Throttle if CPU > 80% or memory > 85% or disk > 90%
        return bool(
            system_load['cpu_percent'] > 80
            or system_load['memory_percent'] > 85
            or system_load['disk_percent'] > 90
        )

def performance_optimized(func: Optional[Callable] = None, operation_name: Optional[str] = None,
                         memory_threshold_mb: int = 512) -> Callable:
    """
    Decorator for performance-optimized function execution.

    Args:
        func: Function to optimize (if None, returns decorator)
        operation_name: Name of operation for metrics
        memory_threshold_mb: Memory threshold for GC triggering

    Returns:
        Decorated function or decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Initialize performance monitoring
            monitor = PerformanceMonitor()
            memory_manager = MemoryManager()

            # Determine operation name
            op_name = operation_name or f"{f.__module__}.{f.__name__}"

            # Start monitoring
            monitor.start_operation(op_name)

            try:
                # Trigger GC if memory pressure is high
                memory_manager.trigger_gc()

                # Execute function
                result = f(*args, **kwargs)

                # End monitoring
                final_metrics = monitor.end_operation(op_name)

                if final_metrics:
                    logger.debug(f"Performance metrics for {op_name}: {final_metrics.to_dict()}")

                return result

            except Exception:
                # End monitoring on error
                monitor.end_operation(op_name)
                raise

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)

def adaptive_batch_size(initial_size: int = 10, max_size: int = 100,
                       memory_threshold_mb: int = 512) -> Callable:
    """
    Create an adaptive batch size function.

    Args:
        initial_size: Initial batch size
        max_size: Maximum batch size
        memory_threshold_mb: Memory threshold for size reduction

    Returns:
        Function that returns adaptive batch size
    """
    memory_manager = MemoryManager(max_memory_mb=memory_threshold_mb * 2)

    def get_batch_size() -> int:
        """Get adaptive batch size based on memory usage."""
        memory_usage = memory_manager.get_memory_usage()

        # Reduce batch size if memory usage is high
        if memory_usage['memory_percent'] > 70:
            return max(1, initial_size // 2)
        elif memory_usage['memory_percent'] > 50:
            return initial_size

        # Increase batch size if memory usage is low
        return min(max_size, initial_size * 2)

    return get_batch_size

class PerformanceOptimizer:
    """
    Comprehensive performance optimization manager.

    Combines all performance optimization utilities into a single,
    easy-to-use interface for large-scale repository operations.
    """

    def __init__(self, enable_monitoring: bool = True, max_memory_mb: int = 1024):
        """
        Initialize performance optimizer.

        Args:
            enable_monitoring: Whether to enable performance monitoring
            max_memory_mb: Maximum memory usage in MB
        """
        self.performance_monitor = PerformanceMonitor(enable_monitoring)
        self.memory_manager = MemoryManager(max_memory_mb)
        self.cache_manager = CacheManager()
        self.batch_processor = BatchProcessor(self.memory_manager, self.performance_monitor)
        self.resource_manager = ResourceManager()

    def optimize_operation(self, operation_name: str, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Optimize and execute an operation with full performance monitoring.

        Args:
            operation_name: Name of the operation
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result
        """
        # Start performance monitoring
        self.performance_monitor.start_operation(operation_name)

        try:
            # Check for memory pressure and optimize
            pressure = self.memory_manager.check_memory_pressure()
            if pressure['should_reduce_batch_size']:
                logger.warning(f"Memory pressure detected: {pressure['pressure_level']}")
                logger.info(f"Recommendations: {', '.join(pressure['recommendations'])}")

            # Trigger GC if needed
            self.memory_manager.trigger_gc()

            # Execute operation
            result = func(*args, **kwargs)

            # End monitoring
            final_metrics = self.performance_monitor.end_operation(operation_name)

            if final_metrics:
                logger.info(f"Operation {operation_name} completed in {final_metrics.duration:.2f}s")

            return result

        except Exception:
            self.performance_monitor.end_operation(operation_name)
            raise

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'memory_usage': self.memory_manager.get_memory_usage(),
            'system_load': self.resource_manager.get_system_load(),
            'cache_stats': self.cache_manager.get_stats(),
            'batch_stats': self.batch_processor.get_batch_stats(),
            'active_operations': len(self.performance_monitor.get_all_metrics()),
            'memory_pressure': self.memory_manager.check_memory_pressure()
        }
