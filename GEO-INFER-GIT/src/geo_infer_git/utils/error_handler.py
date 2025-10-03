#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Error handling utilities for GEO-INFER-GIT.

This module provides comprehensive error handling functionality including
retry mechanisms, error classification, and graceful failure recovery.
"""

import os
import time
import logging
import functools
from typing import Dict, Any, Optional, Callable, Type, Union, Tuple, List
from enum import Enum
import requests
import git

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
    GIT_OPERATION = "git_operation"
    FILESYSTEM = "filesystem"
    CONFIGURATION = "configuration"
    API_LIMIT = "api_limit"
    VALIDATION = "validation"
    UNKNOWN = "unknown"

class GeoInferGitError(Exception):
    """
    Base exception class for GEO-INFER-GIT errors.

    Provides structured error information including category, severity,
    and recovery suggestions.
    """

    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 recoverable: bool = False, suggestions: List[str] = None,
                 original_error: Exception = None):
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

class NetworkError(GeoInferGitError):
    """Network-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK,
                        severity=ErrorSeverity.HIGH, **kwargs)

class AuthenticationError(GeoInferGitError):
    """Authentication-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.AUTHENTICATION,
                        severity=ErrorSeverity.HIGH, **kwargs)

class PermissionError(GeoInferGitError):
    """Permission-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.PERMISSION,
                        severity=ErrorSeverity.HIGH, **kwargs)

class GitOperationError(GeoInferGitError):
    """Git operation errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.GIT_OPERATION,
                        severity=ErrorSeverity.MEDIUM, **kwargs)

class FilesystemError(GeoInferGitError):
    """Filesystem-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.FILESYSTEM,
                        severity=ErrorSeverity.HIGH, **kwargs)

class ConfigurationError(GeoInferGitError):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIGURATION,
                        severity=ErrorSeverity.HIGH, **kwargs)

class APILimitError(GeoInferGitError):
    """API rate limit errors."""

    def __init__(self, message: str, reset_time: int = None, **kwargs):
        super().__init__(message, category=ErrorCategory.API_LIMIT,
                        severity=ErrorSeverity.MEDIUM, recoverable=True, **kwargs)
        self.reset_time = reset_time

class ValidationError(GeoInferGitError):
    """Validation-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION,
                        severity=ErrorSeverity.MEDIUM, **kwargs)

class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
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

    # Git errors
    elif isinstance(error, git.GitCommandError):
        return ErrorCategory.GIT_OPERATION, ErrorSeverity.MEDIUM, True

    # File system errors
    elif isinstance(error, (FileNotFoundError, PermissionError, OSError)):
        return ErrorCategory.FILESYSTEM, ErrorSeverity.HIGH, False

    # Configuration errors
    elif isinstance(error, (ValueError, TypeError, KeyError)):
        return ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM, False

    # Default classification
    return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM, False

def retry_on_error(max_attempts: int = 3, base_delay: float = 1.0,
                  max_delay: float = 60.0, exponential_base: float = 2.0,
                  jitter: bool = True, retryable_errors: Tuple[Type[Exception], ...] = None,
                  logger_instance: logging.Logger = None):
    """
    Decorator for retrying functions on errors.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_errors: Tuple of exception types to retry on
        logger_instance: Logger instance for logging retry attempts

    Returns:
        Decorated function
    """
    retry_config = RetryConfig(max_attempts, base_delay, max_delay, exponential_base, jitter)
    default_retryable_errors = (requests.RequestException, git.GitCommandError, ConnectionError, TimeoutError)

    if retryable_errors is None:
        retryable_errors = default_retryable_errors

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as error:
                    last_error = error

                    # Check if error is retryable
                    if not isinstance(error, retryable_errors):
                        logger_instance.error(f"Non-retryable error in {func.__name__}: {error}")
                        raise

                    # Don't retry on last attempt
                    if attempt == max_attempts - 1:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)

                    # Add jitter if enabled
                    if jitter:
                        import random
                        delay *= (0.5 + random.random())

                    if logger_instance:
                        logger_instance.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed in {func.__name__}: {error}. "
                            f"Retrying in {delay:.1f}s..."
                        )

                    time.sleep(delay)

            # All retries failed
            if logger_instance:
                logger_instance.error(f"All {max_attempts} attempts failed in {func.__name__}")

            raise last_error

        return wrapper

    return decorator

def handle_error(error: Exception, operation: str = None, logger_instance: logging.Logger = None,
                reraise: bool = True) -> Optional[GeoInferGitError]:
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
        suggestions.extend([
            "Check your internet connection",
            "Verify the target repository URL is accessible",
            "Check if firewalls or proxies are blocking the connection"
        ])
    elif category == ErrorCategory.AUTHENTICATION:
        suggestions.extend([
            "Verify your GitHub token is valid and has appropriate permissions",
            "Check that the token hasn't expired",
            "Ensure the token has 'repo' scope for private repositories"
        ])
    elif category == ErrorCategory.PERMISSION:
        suggestions.extend([
            "Check if you have access to the repository",
            "Verify the repository exists and is not private",
            "Ensure your token has the necessary permissions"
        ])
    elif category == ErrorCategory.API_LIMIT:
        suggestions.extend([
            "Wait for rate limit reset",
            "Use a GitHub token to increase rate limits",
            "Reduce the frequency of API calls"
        ])
    elif category == ErrorCategory.GIT_OPERATION:
        suggestions.extend([
            "Check if the repository exists",
            "Verify Git is properly installed",
            "Check disk space and permissions",
            "Ensure the repository is not corrupted"
        ])
    elif category == ErrorCategory.FILESYSTEM:
        suggestions.extend([
            "Check disk space availability",
            "Verify file permissions",
            "Ensure the directory path exists"
        ])
    elif category == ErrorCategory.VALIDATION:
        suggestions.extend([
            "Check configuration file format",
            "Verify all required fields are present",
            "Ensure data types are correct"
        ])

    # Create structured error
    structured_error = GeoInferGitError(
        str(error),
        category=category,
        severity=severity,
        recoverable=recoverable,
        suggestions=suggestions,
        original_error=error
    )

    # Log the error
    if logger_instance:
        logger_instance.log_error_with_context(error, operation)

    if reraise:
        raise structured_error from error

    return structured_error

class ErrorRecoveryManager:
    """
    Manager for handling error recovery strategies.
    """

    def __init__(self, logger_instance: logging.Logger = None):
        """
        Initialize error recovery manager.

        Args:
            logger_instance: Logger instance for logging recovery actions
        """
        self.logger = logger_instance
        self.recovery_strategies = self._load_recovery_strategies()

    def _load_recovery_strategies(self) -> Dict[ErrorCategory, List[Callable]]:
        """Load default recovery strategies for each error category."""
        strategies = {}

        strategies[ErrorCategory.NETWORK] = [
            self._retry_with_backoff,
            self._check_network_connectivity
        ]

        strategies[ErrorCategory.AUTHENTICATION] = [
            self._check_token_validity,
            self._refresh_token
        ]

        strategies[ErrorCategory.API_LIMIT] = [
            self._wait_for_rate_limit_reset,
            self._use_alternate_api_endpoint
        ]

        strategies[ErrorCategory.GIT_OPERATION] = [
            self._retry_git_operation,
            self._clean_git_cache
        ]

        strategies[ErrorCategory.FILESYSTEM] = [
            self._check_disk_space,
            self._verify_permissions
        ]

        return strategies

    def attempt_recovery(self, error: GeoInferGitError, context: Dict[str, Any] = None) -> bool:
        """
        Attempt to recover from an error.

        Args:
            error: Error to recover from
            context: Additional context for recovery

        Returns:
            True if recovery was successful, False otherwise
        """
        context = context or {}

        if not error.recoverable:
            if self.logger:
                self.logger.warning(f"Error {error.category.value} is not recoverable")
            return False

        strategies = self.recovery_strategies.get(error.category, [])

        for strategy in strategies:
            try:
                if strategy(error, context):
                    if self.logger:
                        self.logger.info(f"Successfully recovered using {strategy.__name__}")
                    return True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Recovery strategy {strategy.__name__} failed: {e}")

        return False

    def _retry_with_backoff(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Retry operation with exponential backoff."""
        # This would be implemented based on the specific operation context
        return False

    def _check_network_connectivity(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Check if network connectivity is available."""
        try:
            requests.get("https://api.github.com", timeout=5)
            return True
        except requests.RequestException:
            return False

    def _check_token_validity(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Check if authentication token is valid."""
        token = context.get('token')
        if not token:
            return False

        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={'Authorization': f'token {token}'},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _refresh_token(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Attempt to refresh authentication token."""
        # This would implement token refresh logic
        return False

    def _wait_for_rate_limit_reset(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Wait for API rate limit reset."""
        if hasattr(error, 'reset_time') and error.reset_time:
            wait_time = max(0, error.reset_time - int(time.time()))
            if self.logger:
                self.logger.info(f"Waiting {wait_time} seconds for rate limit reset")
            time.sleep(wait_time)
            return True
        return False

    def _use_alternate_api_endpoint(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Try using an alternate API endpoint."""
        # This would implement endpoint switching logic
        return False

    def _retry_git_operation(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Retry a Git operation."""
        # This would implement Git-specific retry logic
        return False

    def _clean_git_cache(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Clean Git cache and retry."""
        # This would implement cache cleaning logic
        return False

    def _check_disk_space(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(context.get('path', '.'))
            return free > 1024 * 1024 * 100  # At least 100MB free
        except Exception:
            return False

    def _verify_permissions(self, error: GeoInferGitError, context: Dict[str, Any]) -> bool:
        """Verify file/directory permissions."""
        path = context.get('path')
        if not path:
            return False

        try:
            # Try to create a test file
            test_file = os.path.join(path, '.test_permissions')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except Exception:
            return False

def with_error_handling(operation: str = None, logger_instance: logging.Logger = None,
                       max_retries: int = 3):
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
        def wrapper(*args, **kwargs):
            recovery_manager = ErrorRecoveryManager(logger_instance)

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except Exception as error:
                    # Handle and classify the error
                    structured_error = handle_error(
                        error,
                        operation or func.__name__,
                        logger_instance,
                        reraise=False
                    )

                    # Attempt recovery if possible
                    if structured_error.recoverable and attempt < max_retries - 1:
                        context = {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'args': args,
                            'kwargs': kwargs
                        }

                        if recovery_manager.attempt_recovery(structured_error, context):
                            continue

                    # No more retries or non-recoverable error
                    if logger_instance:
                        logger_instance.error(f"Final failure in {func.__name__}: {structured_error}")

                    raise structured_error

            return None  # Should not reach here

        return wrapper

    return decorator
