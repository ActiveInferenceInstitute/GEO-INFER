"""Configuration management module."""
import os
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, validator

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="console", description="Log format (console, json, or text)")
    file: Optional[str] = Field(default=None, description="Log file path")

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("format")
    @classmethod
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ["console", "json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid log format. Must be one of {valid_formats}")
        return v.lower()

class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    enabled: bool = Field(default=True, description="Enable monitoring")
    metrics_port: int = Field(default=9090, description="Metrics server port")
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")

    @field_validator("metrics_port")
    @classmethod
    def validate_metrics_port(cls, v):
        """Validate metrics port."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

class TestingConfig(BaseModel):
    """Testing configuration."""
    enabled: bool = Field(default=True, description="Enable testing")
    parallel: bool = Field(default=False, description="Enable parallel test execution")
    coverage_threshold: float = Field(default=95.0, description="Minimum test coverage threshold")
    timeout: int = Field(default=300, description="Test timeout in seconds")

    @field_validator("coverage_threshold")
    @classmethod
    def validate_coverage_threshold(cls, v):
        """Validate coverage threshold."""
        if not 0 <= v <= 100:
            raise ValueError("Coverage threshold must be between 0 and 100")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be positive")
        return v

class DockerConfig(BaseModel):
    """Docker configuration."""
    registry: str = Field(default="localhost", description="Docker registry URL")
    username: Optional[str] = Field(default=None, description="Registry username")
    password: Optional[str] = Field(default=None, description="Registry password")
    timeout: int = Field(default=300, description="Docker operation timeout in seconds")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be positive")
        return v

class KubernetesConfig(BaseModel):
    """Kubernetes configuration."""
    context: str = Field(default="default", description="Kubernetes context")
    namespace: str = Field(default="default", description="Kubernetes namespace")
    timeout: int = Field(default=300, description="Kubernetes operation timeout in seconds")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be positive")
        return v

class DeploymentConfig(BaseModel):
    """Deployment configuration."""
    replicas: int = Field(default=1, description="Number of replicas")
    resource_limits: Dict[str, str] = Field(
        default_factory=lambda: {"cpu": "500m", "memory": "512Mi"},
        description="Resource limits"
    )
    resource_requests: Dict[str, str] = Field(
        default_factory=lambda: {"cpu": "250m", "memory": "256Mi"},
        description="Resource requests"
    )
    timeout: int = Field(default=300, description="Deployment timeout in seconds")
    docker: DockerConfig = Field(default_factory=DockerConfig, description="Docker configuration")
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig, description="Kubernetes configuration")

    @validator("replicas")
    def validate_replicas(cls, v: int) -> int:
        """Validate replicas count."""
        if v < 1:
            raise ValueError("Replicas must be at least 1")
        return v

    @validator("timeout")
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value."""
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v

class TLSConfig(BaseModel):
    """TLS configuration."""
    enabled: bool = Field(default=True, description="Enable TLS")
    cert_file: Optional[str] = Field(default=None, description="Certificate file path")
    key_file: Optional[str] = Field(default=None, description="Private key file path")
    ca_file: Optional[str] = Field(default=None, description="CA certificate file path")

    @field_validator("cert_file", "key_file", "ca_file")
    @classmethod
    def validate_file_paths(cls, v, info):
        """Validate file paths."""
        if v and info.data.get("enabled", True):
            if not os.path.exists(v):
                raise ValueError(f"File does not exist: {v}")
        return v

class AuthConfig(BaseModel):
    """Authentication configuration."""
    enabled: bool = Field(default=True, description="Enable authentication")
    jwt_secret: Optional[str] = Field(default=None, description="JWT secret key")
    token_expiry: int = Field(default=3600, description="Token expiry in seconds")

    @field_validator("token_expiry")
    @classmethod
    def validate_token_expiry(cls, v):
        """Validate token expiry."""
        if v < 1:
            raise ValueError("Token expiry must be positive")
        return v

class SecurityConfig(BaseModel):
    """Security configuration."""
    enabled: bool = Field(default=True, description="Enable security features")
    tls: TLSConfig = Field(default_factory=TLSConfig, description="TLS configuration")
    auth: AuthConfig = Field(default_factory=AuthConfig, description="Authentication configuration")

class Config(BaseModel):
    """Main configuration."""
    environment: str = Field(default="development", description="Environment name")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    testing: TestingConfig = Field(default_factory=TestingConfig, description="Testing configuration")
    docker: DockerConfig = Field(default_factory=DockerConfig, description="Docker configuration")
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig, description="Kubernetes configuration")
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig, description="Deployment configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment name."""
        valid_environments = ["development", "testing", "test", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Invalid environment. Must be one of {valid_environments}")
        return v.lower()

# Global configuration instance
_config: Optional[Config] = None

def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from file or environment variables."""
    global _config
    
    if _config is not None:
        return _config

    # Load from environment variables if available
    env_config = {}
    for key, value in os.environ.items():
        if key.startswith("GEO_INFER_"):
            env_key = key[10:].lower().replace("_", ".")
            env_config[env_key] = value

    # Load from file if provided
    file_config = {}
    if config_file and os.path.exists(config_file):
        import yaml
        with open(config_file, "r") as f:
            file_config = yaml.safe_load(f)

    # Merge configurations
    config_dict = {**file_config, **env_config}
    
    # Create configuration instance
    _config = Config(**config_dict)
    return _config

def get_config() -> Config:
    """Get the current configuration instance."""
    if _config is None:
        return load_config()
    return _config

def update_config(config_dict: Dict[str, Any]) -> Config:
    """Update configuration with new values.
    
    Args:
        config_dict: Dictionary of configuration updates
        
    Returns:
        Config: Updated configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    
    # Create a new config with the updated values
    updated_dict = _config.model_dump()
    for key, value in config_dict.items():
        if isinstance(value, dict) and key in updated_dict:
            updated_dict[key].update(value)
        else:
            updated_dict[key] = value

    _config = Config(**updated_dict)
    return _config