"""
Standardized error handling utilities for GEO-INFER modules.

This module provides comprehensive error handling functionality including
error classification, retry mechanisms, and graceful failure recovery.
It can be used across all GEO-INFER modules for consistent error handling.
"""

import functools
import logging
import random
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    FILESYSTEM = "filesystem"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    API_LIMIT = "api_limit"
    PROCESSING = "processing"
    DATA = "data"
    UNKNOWN = "unknown"


class GeoInferError(Exception):
    """
    Base exception class for GEO-INFER errors.

    Provides structured error information including category, severity,
    and recovery suggestions.
    """

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = False,
        suggestions: Optional[List[str]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            category: Error category
            severity: Error severity level
            recoverable: Whether the error is recoverable
            suggestions: List of recovery suggestions
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.recoverable = recoverable
        self.suggestions = suggestions or []
        self.original_error = original_error

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.category.value.upper()}] {super().__str__()}"]

        if self.severity != ErrorSeverity.MEDIUM:
            parts.append(f"Severity: {self.severity.value}")

        if not self.recoverable:
            parts.append("Non-recoverable")

        if self.suggestions:
            parts.append(f"Suggestions: {', '.join(self.suggestions)}")

        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": {
                "message": str(self),
                "category": self.category.value,
                "severity": self.severity.value,
                "recoverable": self.recoverable,
                "suggestions": self.suggestions,
            }
        }


class NetworkError(GeoInferError):
    """Network-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.NETWORK, severity=ErrorSeverity.HIGH, **kwargs
        )


class AuthenticationError(GeoInferError):
    """Authentication-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )


class PermissionError(GeoInferError):
    """Permission-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.PERMISSION, severity=ErrorSeverity.HIGH, **kwargs
        )


class FilesystemError(GeoInferError):
    """Filesystem-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.FILESYSTEM, severity=ErrorSeverity.HIGH, **kwargs
        )


class ConfigurationError(GeoInferError):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.CONFIGURATION, severity=ErrorSeverity.HIGH, **kwargs
        )


class ValidationError(GeoInferError):
    """Validation-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.VALIDATION, severity=ErrorSeverity.MEDIUM, **kwargs
        )


class ProcessingError(GeoInferError):
    """Processing-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.PROCESSING, severity=ErrorSeverity.MEDIUM, **kwargs
        )


class DataError(GeoInferError):
    """Data-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message, category=ErrorCategory.DATA, severity=ErrorSeverity.MEDIUM, **kwargs
        )


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def classify_error(error: Exception) -> Tuple[ErrorCategory, ErrorSeverity, bool]:
    """
    Classify an exception into category, severity, and recoverability.

    Args:
        error: Exception to classify

    Returns:
        Tuple of (category, severity, recoverable)
    """
    error_type = type(error)

    # Network errors
    try:
        import requests

        if isinstance(error, requests.RequestException):
            if isinstance(error, requests.ConnectionError):
                return ErrorCategory.NETWORK, ErrorSeverity.HIGH, True
            elif isinstance(error, requests.Timeout):
                return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM, True
            elif isinstance(error, requests.HTTPError):
                status_code = error.response.status_code if error.response else 0
                if status_code == 401:
                    return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, False
                elif status_code == 403:
                    return ErrorCategory.PERMISSION, ErrorSeverity.HIGH, False
                elif status_code == 429:
                    return ErrorCategory.API_LIMIT, ErrorSeverity.MEDIUM, True
                else:
                    return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM, True
    except ImportError:
        pass

    # File system errors
    if isinstance(error, (FileNotFoundError, PermissionError, OSError)):
        return ErrorCategory.FILESYSTEM, ErrorSeverity.HIGH, False

    # Configuration errors
    if isinstance(error, (ValueError, TypeError, KeyError)):
        return ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, False

    # Default classification
    return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM, False


def handle_error(
    error: Exception,
    operation: Optional[str] = None,
    logger_instance: Optional[logging.Logger] = None,
    reraise: bool = True,
) -> Optional[GeoInferError]:
    """
    Handle and classify an error.

    Args:
        error: Exception to handle
        operation: Operation that failed
        logger_instance: Logger instance for logging
        reraise: Whether to re-raise the error

    Returns:
        Classified error if not reraising, None if reraised
    """
    category, severity, recoverable = classify_error(error)

    # Create suggestions based on error type
    suggestions = []

    if category == ErrorCategory.NETWORK:
        suggestions.extend(
            [
                "Check your internet connection",
                "Verify the target service is accessible",
                "Check if firewalls or proxies are blocking the connection",
            ]
        )
    elif category == ErrorCategory.AUTHENTICATION:
        suggestions.extend(
            [
                "Verify your credentials are valid",
                "Check that credentials haven't expired",
                "Ensure you have appropriate permissions",
            ]
        )
    elif category == ErrorCategory.PERMISSION:
        suggestions.extend(
            [
                "Check if you have access to the resource",
                "Verify the resource exists",
                "Ensure your credentials have the necessary permissions",
            ]
        )
    elif category == ErrorCategory.FILESYSTEM:
        suggestions.extend(
            [
                "Check if the file or directory exists",
                "Verify file permissions",
                "Check disk space and system resources",
            ]
        )
    elif category == ErrorCategory.VALIDATION:
        suggestions.extend(
            [
                "Verify input data format and types",
                "Check required fields are provided",
                "Validate data constraints",
            ]
        )

    # Create structured error
    structured_error = GeoInferError(
        message=str(error),
        category=category,
        severity=severity,
        recoverable=recoverable,
        suggestions=suggestions,
        original_error=error,
    )

    # Log the error
    log_func = (logger_instance or logger).error
    log_msg = f"Error in {operation or 'operation'}: {structured_error}"
    log_func(log_msg, exc_info=True)

    if reraise:
        raise structured_error

    return structured_error


def retry_on_error(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_errors: Optional[Tuple[Type[Exception], ...]] = None,
    logger_instance: Optional[logging.Logger] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retrying operations on error.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_errors: Tuple of exception types that should be retried
        logger_instance: Logger instance for logging

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger_instance or logger

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise
                        log.error(
                            f"Final failure after {max_attempts} attempts in {func.__name__}: {error}"
                        )
                        raise

                    # Check if error is retryable
                    if retryable_errors and not isinstance(error, retryable_errors):
                        log.error(f"Non-retryable error in {func.__name__}: {error}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt), max_delay
                    )

                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    log.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed in {func.__name__}, "
                        f"retrying in {delay:.2f}s: {error}"
                    )
                    time.sleep(delay)

            return None  # Should not reach here

        return wrapper

    return decorator


def with_error_handling(
    operation: Optional[str] = None,
    logger_instance: Optional[logging.Logger] = None,
    max_retries: int = 3,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for comprehensive error handling.

    Args:
        operation: Name of operation for logging
        logger_instance: Logger instance for logging errors
        max_retries: Maximum number of retry attempts

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger_instance or logger
            op_name = operation or func.__name__

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    structured_error = handle_error(
                        error, op_name, log, reraise=False
                    )

                    if structured_error and structured_error.recoverable and attempt < max_retries - 1:
                        log.warning(
                            f"Recoverable error in {op_name} (attempt {attempt + 1}/{max_retries}), "
                            f"retrying: {structured_error}"
                        )
                        continue

                    # No more retries or non-recoverable error
                    if structured_error is None:
                        log.error(f"Final failure in {op_name}")
                        raise
                    log.error(f"Final failure in {op_name}: {structured_error}")
                    raise structured_error

            return None  # Should not reach here

        return wrapper

    return decorator


__all__ = [
    "ErrorSeverity",
    "ErrorCategory",
    "GeoInferError",
    "NetworkError",
    "AuthenticationError",
    "PermissionError",
    "FilesystemError",
    "ConfigurationError",
    "ValidationError",
    "ProcessingError",
    "DataError",
    "RetryConfig",
    "classify_error",
    "handle_error",
    "retry_on_error",
    "with_error_handling",
]

