"""
GEO-INFER-LOG: Comprehensive Logging and Monitoring Module

This module provides advanced logging, monitoring, and observability capabilities
for the GEO-INFER framework. It supports structured logging, performance metrics,
distributed tracing, and integration with monitoring systems.

Key Features:
- Structured JSON logging with spatial context
- Performance metrics collection and analysis
- Real-time log aggregation and search
- Integration with monitoring systems (Prometheus, Grafana)
- Distributed tracing for multi-module workflows
- Log-based alerting and anomaly detection
"""

import json
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from pathlib import Path
import logging
import logging.handlers
import uuid
import os
import queue
import asyncio

# Optional dependencies
try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

__version__ = "1.0.0"
__all__ = [
    "EnhancedLogger",
    "PerformanceMetrics", 
    "LogAnalyzer",
    "SpatialLogContext",
    "GeoInferLogger"
]

@dataclass
class LogEntry:
    """Structured log entry with spatial and temporal context."""
    timestamp: str
    level: str
    module: str
    operation: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    spatial_context: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    error_info: Optional[Dict[str, Any]] = None

@dataclass
class SpatialLogContext:
    """Spatial context for geospatial operations."""
    h3_index: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolution: Optional[int] = None
    region: Optional[str] = None
    bbox: Optional[List[float]] = None
    coordinate_system: str = "EPSG:4326"

class PerformanceMetrics:
    """Performance metrics collection and analysis."""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.start_times: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def start_timer(self, operation: str) -> str:
        """Start a timer for an operation."""
        timer_id = f"{operation}_{uuid.uuid4().hex[:8]}"
        with self.lock:
            self.start_times[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """End a timer and record the duration."""
        with self.lock:
            if timer_id in self.start_times:
                duration = time.time() - self.start_times[timer_id]
                operation = timer_id.split('_')[0]
                self.record_duration(operation, duration)
                del self.start_times[timer_id]
                return duration
        return 0.0
    
    def record_duration(self, operation: str, duration: float):
        """Record operation duration."""
        with self.lock:
            self.metrics[f"{operation}_duration"].append(duration)
            self.histograms[f"{operation}_duration"].append(duration)
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        with self.lock:
            self.counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge metric."""
        with self.lock:
            self.gauges[name] = value
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        with self.lock:
            durations = list(self.metrics[f"{operation}_duration"])
            if not durations:
                return {}
            
            durations.sort()
            n = len(durations)
            
            return {
                "count": n,
                "mean": sum(durations) / n,
                "min": durations[0],
                "max": durations[-1],
                "p50": durations[n // 2],
                "p95": durations[int(n * 0.95)] if n > 0 else 0,
                "p99": durations[int(n * 0.99)] if n > 0 else 0
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        with self.lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "performance_stats": {
                    op.replace("_duration", ""): self.get_stats(op.replace("_duration", ""))
                    for op in self.metrics.keys()
                    if op.endswith("_duration")
                }
            }

class EnhancedLogger:
    """Enhanced logger with spatial context and performance tracking."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.metrics = PerformanceMetrics()
        self.trace_id = None
        self.span_id = None
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.config.get("level", "INFO")))
        
        # Setup handlers
        self._setup_handlers()
        
        # Log queue for async processing
        self.log_queue = queue.Queue()
        self.log_processor_running = False
        
        # Start background log processor
        if self.config.get("async_logging", True):
            self._start_log_processor()
    
    def _setup_handlers(self):
        """Setup logging handlers based on configuration."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        outputs = self.config.get("outputs", {"console": {"enabled": True}})
        
        # Console handler
        if outputs.get("console", {}).get("enabled", True):
            console_handler = logging.StreamHandler()
            console_format = outputs.get("console", {}).get("format", "text")
            
            if console_format == "json":
                formatter = JSONFormatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if outputs.get("file", {}).get("enabled", False):
            file_config = outputs["file"]
            log_file = Path(file_config.get("path", "logs/geo_infer.log"))
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            if file_config.get("rotation", "") == "daily":
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    log_file, when="D", interval=1, 
                    backupCount=int(file_config.get("retention", "30").replace("d", ""))
                )
            else:
                file_handler = logging.FileHandler(log_file)
            
            file_format = file_config.get("format", "json")
            if file_format == "json":
                formatter = JSONFormatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _start_log_processor(self):
        """Start background log processor for async logging."""
        if not self.log_processor_running:
            self.log_processor_running = True
            thread = threading.Thread(target=self._process_logs, daemon=True)
            thread.start()
    
    def _process_logs(self):
        """Process logs from the queue."""
        while self.log_processor_running:
            try:
                log_entry = self.log_queue.get(timeout=1.0)
                self._write_log_entry(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing log: {e}")
    
    def _write_log_entry(self, entry: LogEntry):
        """Write log entry to configured outputs."""
        level_method = getattr(self.logger, entry.level.lower(), self.logger.info)
        
        # Create extra fields for structured logging
        extra = {
            "module": entry.module,
            "operation": entry.operation,
            "context": entry.context,
            "trace_id": entry.trace_id,
            "span_id": entry.span_id
        }
        
        if entry.spatial_context:
            extra["spatial_context"] = asdict(entry.spatial_context)
        
        if entry.performance_metrics:
            extra["performance_metrics"] = entry.performance_metrics
        
        if entry.error_info:
            extra["error_info"] = entry.error_info
        
        level_method(entry.message, extra=extra)
    
    def log(self, level: str, operation: str, message: str, 
            context: Optional[Dict] = None,
            spatial_context: Optional[SpatialLogContext] = None,
            module: Optional[str] = None,
            performance_metrics: Optional[Dict] = None,
            error_info: Optional[Dict] = None):
        """Log a structured message."""
        
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level.upper(),
            module=module or self.name,
            operation=operation,
            message=message,
            context=context or {},
            spatial_context=spatial_context,
            performance_metrics=performance_metrics,
            trace_id=self.trace_id,
            span_id=self.span_id,
            error_info=error_info
        )
        
        # Update metrics
        self.metrics.increment_counter(f"{entry.module}_{entry.operation}")
        
        # Queue for async processing or process immediately
        if self.config.get("async_logging", True):
            try:
                self.log_queue.put_nowait(entry)
            except queue.Full:
                # Fallback to immediate processing if queue is full
                self._write_log_entry(entry)
        else:
            self._write_log_entry(entry)
    
    def info(self, operation: str, message: str, **kwargs):
        """Log info message."""
        self.log("INFO", operation, message, **kwargs)
    
    def debug(self, operation: str, message: str, **kwargs):
        """Log debug message."""
        self.log("DEBUG", operation, message, **kwargs)
    
    def warning(self, operation: str, message: str, **kwargs):
        """Log warning message."""
        self.log("WARNING", operation, message, **kwargs)
    
    def error(self, operation: str, message: str, **kwargs):
        """Log error message."""
        self.log("ERROR", operation, message, **kwargs)
    
    def critical(self, operation: str, message: str, **kwargs):
        """Log critical message."""
        self.log("CRITICAL", operation, message, **kwargs)
    
    def start_operation(self, operation: str, **context) -> str:
        """Start tracking an operation."""
        timer_id = self.metrics.start_timer(operation)
        
        self.info(
            f"{operation}_start",
            f"Started operation: {operation}",
            context=context,
            performance_metrics={"timer_id": timer_id}
        )
        
        return timer_id
    
    def end_operation(self, operation: str, timer_id: str, 
                     success: bool = True, **context):
        """End tracking an operation."""
        duration = self.metrics.end_timer(timer_id)
        
        level = "info" if success else "error"
        status = "completed" if success else "failed"
        
        getattr(self, level)(
            f"{operation}_end",
            f"Operation {status}: {operation}",
            context=context,
            performance_metrics={
                "duration_seconds": duration,
                "success": success
            }
        )
    
    def log_spatial_operation(self, operation: str, 
                            h3_index: Optional[str] = None,
                            lat: Optional[float] = None,
                            lon: Optional[float] = None,
                            resolution: Optional[int] = None,
                            **context):
        """Log a spatial operation with geographic context."""
        spatial_context = SpatialLogContext(
            h3_index=h3_index,
            latitude=lat,
            longitude=lon,
            resolution=resolution
        )
        
        self.info(
            operation,
            f"Spatial operation: {operation}",
            context=context,
            spatial_context=spatial_context
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.get_all_metrics()

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": getattr(record, "module", "unknown"),
            "operation": getattr(record, "operation", "unknown")
        }
        
        # Add extra fields
        if hasattr(record, "context"):
            log_entry["context"] = record.context
        
        if hasattr(record, "spatial_context"):
            log_entry["spatial_context"] = record.spatial_context
        
        if hasattr(record, "performance_metrics"):
            log_entry["performance_metrics"] = record.performance_metrics
        
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        
        if hasattr(record, "error_info"):
            log_entry["error_info"] = record.error_info
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str)

class LogAnalyzer:
    """Analyze logs for patterns, anomalies, and insights."""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
        self.log_entries: List[Dict] = []
        
        if self.log_file_path.exists():
            self._load_logs()
    
    def _load_logs(self):
        """Load logs from file."""
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            self.log_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error loading logs: {e}")
    
    def analyze_performance(self, operation: str = None) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        performance_data = []
        
        for entry in self.log_entries:
            if operation and entry.get("operation") != operation:
                continue
                
            if "performance_metrics" in entry:
                metrics = entry["performance_metrics"]
                if "duration_seconds" in metrics:
                    performance_data.append({
                        "timestamp": entry["timestamp"],
                        "operation": entry["operation"],
                        "duration": metrics["duration_seconds"],
                        "success": metrics.get("success", True)
                    })
        
        if not performance_data:
            return {"message": "No performance data found"}
        
        durations = [p["duration"] for p in performance_data]
        successes = [p for p in performance_data if p["success"]]
        
        return {
            "total_operations": len(performance_data),
            "successful_operations": len(successes),
            "success_rate": len(successes) / len(performance_data),
            "duration_stats": {
                "mean": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
                "p95": sorted(durations)[int(len(durations) * 0.95)] if durations else 0
            }
        }
    
    def find_errors(self, hours: int = 24) -> List[Dict]:
        """Find error entries in the last N hours."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        errors = []
        for entry in self.log_entries:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if (entry_time > cutoff_time and 
                    entry["level"] in ["ERROR", "CRITICAL"]):
                    errors.append(entry)
            except (KeyError, ValueError):
                continue
        
        return sorted(errors, key=lambda x: x["timestamp"], reverse=True)
    
    def spatial_analysis(self) -> Dict[str, Any]:
        """Analyze spatial operations from logs."""
        spatial_operations = []
        
        for entry in self.log_entries:
            if "spatial_context" in entry:
                spatial_operations.append(entry)
        
        if not spatial_operations:
            return {"message": "No spatial operations found"}
        
        h3_resolutions = defaultdict(int)
        regions = defaultdict(int)
        
        for op in spatial_operations:
            spatial = op["spatial_context"]
            if "resolution" in spatial:
                h3_resolutions[spatial["resolution"]] += 1
            if "region" in spatial:
                regions[spatial["region"]] += 1
        
        return {
            "total_spatial_operations": len(spatial_operations),
            "h3_resolution_usage": dict(h3_resolutions),
            "region_distribution": dict(regions)
        }

# Convenience logger factory
def get_logger(name: str, config: Optional[Dict] = None) -> EnhancedLogger:
    """Get an enhanced logger instance."""
    return EnhancedLogger(name, config)

# Legacy compatibility
GeoInferLogger = EnhancedLogger 