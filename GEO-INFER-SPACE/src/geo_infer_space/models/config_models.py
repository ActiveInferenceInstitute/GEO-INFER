"""
Configuration models for GEO-INFER-SPACE.

This module defines Pydantic models for configuration schemas
including analysis parameters, indexing settings, API configuration,
and database connections.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator, model_validator


class DatabaseConfig(BaseModel):
    """Configuration for spatial database connections."""
    
    host: str = Field("localhost", description="Database host")
    port: int = Field(5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    schema: str = Field("public", description="Database schema")
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(20, description="Maximum pool overflow")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('pool_size')
    def validate_pool_size(cls, v):
        if v < 1:
            raise ValueError('Pool size must be at least 1')
        return v
    
    def get_connection_string(self) -> str:
        """Generate database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class IndexingConfig(BaseModel):
    """Configuration for spatial indexing systems."""
    
    default_index_type: str = Field("rtree", description="Default spatial index type")
    h3_default_resolution: int = Field(8, ge=0, le=15, description="Default H3 resolution")
    rtree_leaf_capacity: int = Field(10, description="R-tree leaf node capacity")
    quadtree_max_depth: int = Field(20, description="QuadTree maximum depth")
    geohash_precision: int = Field(12, description="Geohash precision")
    enable_caching: bool = Field(True, description="Enable index caching")
    cache_size_mb: int = Field(100, description="Index cache size in MB")
    
    @validator('default_index_type')
    def validate_index_type(cls, v):
        valid_types = ['rtree', 'quadtree', 'h3', 'geohash', 's2']
        if v.lower() not in valid_types:
            raise ValueError(f'Index type must be one of {valid_types}')
        return v.lower()
    
    @validator('cache_size_mb')
    def validate_cache_size(cls, v):
        if v < 1:
            raise ValueError('Cache size must be at least 1 MB')
        return v


class AnalysisConfig(BaseModel):
    """Configuration for spatial analysis operations."""
    
    # Vector analysis settings
    buffer_resolution: int = Field(16, description="Buffer resolution (segments per quarter circle)")
    overlay_precision: float = Field(1e-6, description="Geometric precision for overlay operations")
    simplify_tolerance: float = Field(0.0, description="Default simplification tolerance")
    
    # Raster analysis settings
    raster_chunk_size: int = Field(1024, description="Raster processing chunk size")
    nodata_value: float = Field(-9999.0, description="Default NoData value")
    resampling_method: str = Field("bilinear", description="Default resampling method")
    
    # Network analysis settings
    network_tolerance: float = Field(1e-3, description="Network topology tolerance")
    max_routing_distance: float = Field(100000.0, description="Maximum routing distance")
    
    # Geostatistics settings
    interpolation_method: str = Field("idw", description="Default interpolation method")
    idw_power: float = Field(2.0, description="IDW power parameter")
    kriging_variogram: str = Field("spherical", description="Kriging variogram model")
    
    # Performance settings
    parallel_processing: bool = Field(True, description="Enable parallel processing")
    max_workers: Optional[int] = Field(None, description="Maximum worker threads")
    memory_limit_gb: Optional[float] = Field(None, description="Memory limit in GB")
    
    @validator('buffer_resolution')
    def validate_buffer_resolution(cls, v):
        if v < 4:
            raise ValueError('Buffer resolution must be at least 4')
        return v
    
    @validator('raster_chunk_size')
    def validate_chunk_size(cls, v):
        if v < 64 or v > 8192:
            raise ValueError('Raster chunk size must be between 64 and 8192')
        return v
    
    @validator('resampling_method')
    def validate_resampling_method(cls, v):
        valid_methods = ['nearest', 'bilinear', 'cubic', 'average', 'mode']
        if v.lower() not in valid_methods:
            raise ValueError(f'Resampling method must be one of {valid_methods}')
        return v.lower()
    
    @validator('interpolation_method')
    def validate_interpolation_method(cls, v):
        valid_methods = ['idw', 'kriging', 'rbf', 'nearest', 'linear']
        if v.lower() not in valid_methods:
            raise ValueError(f'Interpolation method must be one of {valid_methods}')
        return v.lower()


class APIConfig(BaseModel):
    """Configuration for REST API server."""
    
    host: str = Field("0.0.0.0", description="API server host")
    port: int = Field(8000, description="API server port")
    workers: int = Field(1, description="Number of worker processes")
    reload: bool = Field(False, description="Enable auto-reload in development")
    
    # CORS settings
    cors_origins: List[str] = Field(["*"], description="Allowed CORS origins")
    cors_methods: List[str] = Field(["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(["*"], description="Allowed CORS headers")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(False, description="Enable rate limiting")
    rate_limit_requests: int = Field(100, description="Requests per minute limit")
    
    # Authentication
    auth_enabled: bool = Field(False, description="Enable authentication")
    jwt_secret: Optional[str] = Field(None, description="JWT secret key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(24, description="JWT expiration time in hours")
    
    # Request limits
    max_request_size_mb: int = Field(100, description="Maximum request size in MB")
    request_timeout_seconds: int = Field(300, description="Request timeout in seconds")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('workers')
    def validate_workers(cls, v):
        if v < 1:
            raise ValueError('Number of workers must be at least 1')
        return v
    
    @validator('max_request_size_mb')
    def validate_request_size(cls, v):
        if v < 1:
            raise ValueError('Maximum request size must be at least 1 MB')
        return v


class LoggingConfig(BaseModel):
    """Configuration for logging system."""
    
    level: str = Field("INFO", description="Logging level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_enabled: bool = Field(True, description="Enable file logging")
    file_path: Optional[Path] = Field(None, description="Log file path")
    file_max_size_mb: int = Field(10, description="Maximum log file size in MB")
    file_backup_count: int = Field(5, description="Number of backup log files")
    console_enabled: bool = Field(True, description="Enable console logging")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    @validator('file_max_size_mb')
    def validate_file_size(cls, v):
        if v < 1:
            raise ValueError('Log file size must be at least 1 MB')
        return v


class CacheConfig(BaseModel):
    """Configuration for caching system."""
    
    enabled: bool = Field(True, description="Enable caching")
    backend: str = Field("memory", description="Cache backend type")
    ttl_seconds: int = Field(3600, description="Default TTL in seconds")
    max_size_mb: int = Field(100, description="Maximum cache size in MB")
    
    # Redis settings (if backend is redis)
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, description="Redis port")
    redis_db: int = Field(0, description="Redis database number")
    redis_password: Optional[str] = Field(None, description="Redis password")
    
    @validator('backend')
    def validate_backend(cls, v):
        valid_backends = ['memory', 'redis', 'memcached']
        if v.lower() not in valid_backends:
            raise ValueError(f'Cache backend must be one of {valid_backends}')
        return v.lower()
    
    @validator('ttl_seconds')
    def validate_ttl(cls, v):
        if v < 1:
            raise ValueError('TTL must be at least 1 second')
        return v


class OSCConfig(BaseModel):
    """Configuration for OS-Climate integration."""
    
    enabled: bool = Field(True, description="Enable OS-Climate integration")
    repos_directory: Path = Field(Path("./repo"), description="Directory for cloned repositories")
    auto_update: bool = Field(False, description="Auto-update repositories")
    update_interval_hours: int = Field(24, description="Update interval in hours")
    
    # Repository settings
    repositories: Dict[str, str] = Field(
        default_factory=lambda: {
            "osc-geo-h3loader-cli": "https://github.com/docxology/osc-geo-h3loader-cli.git",
            "osc-geo-h3grid-srv": "https://github.com/docxology/osc-geo-h3grid-srv.git"
        },
        description="Repository URLs"
    )
    
    # H3 service settings
    h3_service_enabled: bool = Field(True, description="Enable H3 grid service")
    h3_service_host: str = Field("localhost", description="H3 service host")
    h3_service_port: int = Field(8080, description="H3 service port")
    
    @validator('update_interval_hours')
    def validate_update_interval(cls, v):
        if v < 1:
            raise ValueError('Update interval must be at least 1 hour')
        return v


class SpaceConfig(BaseModel):
    """Main configuration model for GEO-INFER-SPACE."""
    
    # Core settings
    debug: bool = Field(False, description="Enable debug mode")
    environment: str = Field("production", description="Environment name")
    data_directory: Path = Field(Path("./data"), description="Data directory path")
    temp_directory: Path = Field(Path("./temp"), description="Temporary files directory")
    
    # Component configurations
    database: Optional[DatabaseConfig] = Field(None, description="Database configuration")
    indexing: IndexingConfig = Field(default_factory=IndexingConfig, description="Indexing configuration")
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig, description="Analysis configuration")
    api: APIConfig = Field(default_factory=APIConfig, description="API configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    osc: OSCConfig = Field(default_factory=OSCConfig, description="OS-Climate configuration")
    
    # Custom settings
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration parameters")
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_environments = ['development', 'testing', 'staging', 'production']
        if v.lower() not in valid_environments:
            raise ValueError(f'Environment must be one of {valid_environments}')
        return v.lower()
    
    @model_validator(mode='after')
    def validate_directories(self):
        """Ensure directories exist or can be created."""
        values = self.model_dump()
        for dir_field in ['data_directory', 'temp_directory']:
            if dir_field in values and values[dir_field]:
                directory = Path(values[dir_field])
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise ValueError(f'Cannot create directory {directory}: {e}')
        return self
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'SpaceConfig':
        """Load configuration from YAML or JSON file."""
        import yaml
        import json
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f'Configuration file not found: {config_path}')
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f'Unsupported configuration file format: {config_path.suffix}')
        
        return cls(**config_data)
    
    def to_file(self, config_path: Union[str, Path], format: str = 'yaml') -> None:
        """Save configuration to file."""
        import yaml
        import json
        
        config_path = Path(config_path)
        config_data = self.dict()
        
        # Convert Path objects to strings for serialization
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            else:
                return obj
        
        config_data = convert_paths(config_data)
        
        with open(config_path, 'w') as f:
            if format.lower() == 'yaml':
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError(f'Unsupported format: {format}')


class PerformanceConfig(BaseModel):
    """Configuration for performance optimization."""
    
    # Memory management
    memory_limit_gb: Optional[float] = Field(None, description="Memory limit in GB")
    gc_threshold: int = Field(1000, description="Garbage collection threshold")
    
    # Parallel processing
    max_workers: Optional[int] = Field(None, description="Maximum worker threads")
    chunk_size: int = Field(1000, description="Processing chunk size")
    use_multiprocessing: bool = Field(True, description="Enable multiprocessing")
    
    # I/O optimization
    io_buffer_size: int = Field(65536, description="I/O buffer size in bytes")
    async_io: bool = Field(True, description="Enable asynchronous I/O")
    
    # Spatial operations
    spatial_precision: float = Field(1e-6, description="Spatial precision for operations")
    simplify_threshold: float = Field(0.0, description="Geometry simplification threshold")
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        if v < 1:
            raise ValueError('Chunk size must be at least 1')
        return v
    
    @validator('io_buffer_size')
    def validate_buffer_size(cls, v):
        if v < 1024:
            raise ValueError('I/O buffer size must be at least 1024 bytes')
        return v
