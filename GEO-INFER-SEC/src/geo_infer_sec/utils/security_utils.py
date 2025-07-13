"""
Security utilities for GEO-INFER framework.

This module provides utility functions for security and privacy protection
in geospatial data processing and analysis.
"""

import hashlib
import hmac
import secrets
import base64
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Configuration for security utilities."""
    
    # Encryption parameters
    key_length: int = 32
    salt_length: int = 16
    iterations: int = 100000
    
    # Privacy parameters
    k_anonymity: int = 5
    l_diversity: int = 3
    t_closeness: float = 0.1
    
    # Access control
    max_failed_attempts: int = 5
    lockout_duration: int = 300  # seconds
    
    # Audit parameters
    enable_audit_logging: bool = True
    audit_retention_days: int = 90

class SecurityUtils:
    """
    Utility class for security and privacy operations.
    
    Provides methods for data encryption, privacy protection,
    access control, and audit logging.
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize security utilities.
        
        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.failed_attempts = {}
        self.audit_log = []
    
    def generate_secure_key(self, length: Optional[int] = None) -> bytes:
        """
        Generate a cryptographically secure random key.
        
        Args:
            length: Key length in bytes (uses config default if None)
            
        Returns:
            Random key as bytes
        """
        key_len = length or self.config.key_length
        return secrets.token_bytes(key_len)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt for hashing (generated if None)
            
        Returns:
            Tuple of (hash, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(self.config.salt_length)
        
        # Use PBKDF2 for password hashing
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.config.iterations
        )
        
        return hash_obj, salt
    
    def verify_password(self, password: str, stored_hash: bytes, salt: bytes) -> bool:
        """
        Verify a password against stored hash.
        
        Args:
            password: Password to verify
            stored_hash: Stored password hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)
    
    def encrypt_data(self, data: Union[str, bytes], key: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES (simplified implementation).
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Tuple of (encrypted_data, iv)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate initialization vector
        iv = secrets.token_bytes(16)
        
        # Simple XOR encryption (for demonstration - use proper AES in production)
        encrypted = bytes(a ^ b for a, b in zip(data, key[:len(data)]))
        
        return encrypted, iv
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Decrypt data using AES (simplified implementation).
        
        Args:
            encrypted_data: Encrypted data
            key: Decryption key
            iv: Initialization vector
            
        Returns:
            Decrypted data
        """
        # Simple XOR decryption (for demonstration - use proper AES in production)
        decrypted = bytes(a ^ b for a, b in zip(encrypted_data, key[:len(encrypted_data)]))
        
        return decrypted
    
    def anonymize_spatial_data(self, 
                              data: pd.DataFrame,
                              lat_col: str = 'lat',
                              lon_col: str = 'lon',
                              precision: int = 2) -> pd.DataFrame:
        """
        Anonymize spatial data by reducing precision.
        
        Args:
            data: Input DataFrame
            lat_col: Latitude column name
            lon_col: Longitude column name
            precision: Decimal precision to keep
            
        Returns:
            Anonymized DataFrame
        """
        anonymized = data.copy()
        
        if lat_col in anonymized.columns:
            anonymized[lat_col] = anonymized[lat_col].round(precision)
        
        if lon_col in anonymized.columns:
            anonymized[lon_col] = anonymized[lon_col].round(precision)
        
        return anonymized
    
    def apply_k_anonymity(self, 
                         data: pd.DataFrame,
                         sensitive_cols: List[str],
                         quasi_identifiers: List[str]) -> pd.DataFrame:
        """
        Apply k-anonymity to protect sensitive data.
        
        Args:
            data: Input DataFrame
            sensitive_cols: Columns containing sensitive information
            quasi_identifiers: Columns that could identify individuals
            
        Returns:
            K-anonymized DataFrame
        """
        k = self.config.k_anonymity
        anonymized = data.copy()
        
        # Group by quasi-identifiers
        groups = anonymized.groupby(quasi_identifiers)
        
        # For each group, ensure at least k records
        for name, group in groups:
            if len(group) < k:
                # Suppress or generalize values
                for col in quasi_identifiers:
                    anonymized.loc[group.index, col] = '*'
        
        return anonymized
    
    def add_noise_to_numerical(self, 
                              data: pd.DataFrame,
                              columns: List[str],
                              noise_level: float = 0.1) -> pd.DataFrame:
        """
        Add noise to numerical columns for privacy protection.
        
        Args:
            data: Input DataFrame
            columns: Columns to add noise to
            noise_level: Standard deviation of noise as fraction of data std
            
        Returns:
            DataFrame with added noise
        """
        noisy_data = data.copy()
        
        for col in columns:
            if col in noisy_data.columns and pd.api.types.is_numeric_dtype(noisy_data[col]):
                std = noisy_data[col].std()
                noise = np.random.normal(0, std * noise_level, len(noisy_data))
                noisy_data[col] = noisy_data[col] + noise
        
        return noisy_data
    
    def check_access_control(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if user has permission to perform action on resource.
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Check for account lockout
        if self._is_account_locked(user_id):
            self._log_audit_event(user_id, resource, action, "DENIED", "Account locked")
            return False
        
        # Simple access control (in practice, use proper RBAC/ABAC)
        allowed_resources = self._get_user_permissions(user_id)
        
        if resource in allowed_resources:
            self._log_audit_event(user_id, resource, action, "ALLOWED")
            return True
        else:
            self._log_audit_event(user_id, resource, action, "DENIED", "Insufficient permissions")
            return False
    
    def _is_account_locked(self, user_id: str) -> bool:
        """Check if user account is locked due to failed attempts."""
        if user_id not in self.failed_attempts:
            return False
        
        attempts, last_attempt = self.failed_attempts[user_id]
        
        if attempts >= self.config.max_failed_attempts:
            lockout_until = last_attempt + timedelta(seconds=self.config.lockout_duration)
            if datetime.now() < lockout_until:
                return True
            else:
                # Reset failed attempts after lockout period
                del self.failed_attempts[user_id]
        
        return False
    
    def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get list of resources user has permission to access."""
        # Simplified permission system
        # In practice, this would query a database or external system
        permissions = {
            'admin': ['*'],  # Admin has access to everything
            'analyst': ['geo_infer_space', 'geo_infer_place', 'geo_infer_iot'],
            'viewer': ['geo_infer_space']
        }
        
        # Extract role from user_id (simplified)
        if 'admin' in user_id.lower():
            role = 'admin'
        elif 'analyst' in user_id.lower():
            role = 'analyst'
        else:
            role = 'viewer'
        
        return permissions.get(role, [])
    
    def record_failed_attempt(self, user_id: str):
        """Record a failed authentication attempt."""
        now = datetime.now()
        
        if user_id in self.failed_attempts:
            attempts, _ = self.failed_attempts[user_id]
            self.failed_attempts[user_id] = (attempts + 1, now)
        else:
            self.failed_attempts[user_id] = (1, now)
    
    def _log_audit_event(self, 
                        user_id: str, 
                        resource: str, 
                        action: str, 
                        result: str, 
                        reason: Optional[str] = None):
        """Log an audit event."""
        if not self.config.enable_audit_logging:
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': result,
            'reason': reason,
            'event_id': str(uuid.uuid4())
        }
        
        self.audit_log.append(event)
        logger.info(f"Audit: {user_id} {action} {resource} - {result}")
    
    def get_audit_log(self, 
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries with optional filtering.
        
        Args:
            start_time: Start time for filtering
            end_time: End time for filtering
            user_id: User ID for filtering
            
        Returns:
            List of audit log entries
        """
        filtered_log = self.audit_log.copy()
        
        if start_time:
            filtered_log = [e for e in filtered_log if datetime.fromisoformat(e['timestamp']) >= start_time]
        
        if end_time:
            filtered_log = [e for e in filtered_log if datetime.fromisoformat(e['timestamp']) <= end_time]
        
        if user_id:
            filtered_log = [e for e in filtered_log if e['user_id'] == user_id]
        
        return filtered_log
    
    def cleanup_audit_log(self):
        """Remove old audit log entries based on retention policy."""
        if not self.config.enable_audit_logging:
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.config.audit_retention_days)
        
        self.audit_log = [
            e for e in self.audit_log 
            if datetime.fromisoformat(e['timestamp']) > cutoff_date
        ]
    
    def generate_secure_token(self, user_id: str, expiration_hours: int = 24) -> str:
        """
        Generate a secure token for user authentication.
        
        Args:
            user_id: User identifier
            expiration_hours: Token expiration time in hours
            
        Returns:
            Secure token string
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(hours=expiration_hours),
            'nonce': secrets.token_hex(16)
        }
        
        # Encode payload
        payload_str = json.dumps(payload, default=str)
        payload_bytes = payload_str.encode('utf-8')
        
        # Create signature
        key = self.generate_secure_key()
        signature = hmac.new(key, payload_bytes, hashlib.sha256).digest()
        
        # Combine payload and signature
        token_data = payload_bytes + b'.' + signature
        token = base64.urlsafe_b64encode(token_data).decode('utf-8')
        
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate a secure token and return user ID if valid.
        
        Args:
            token: Token to validate
            
        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            # Decode token
            token_data = base64.urlsafe_b64decode(token.encode('utf-8'))
            payload_str, signature = token_data.split(b'.', 1)
            
            # Verify signature (simplified - in practice, use proper key management)
            key = self.generate_secure_key()
            expected_signature = hmac.new(key, payload_str, hashlib.sha256).digest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Parse payload
            payload = json.loads(payload_str.decode('utf-8'))
            
            # Check expiration
            exp_str = payload['exp']
            if isinstance(exp_str, str):
                exp = datetime.fromisoformat(exp_str)
            else:
                exp = exp_str
            
            if datetime.now() > exp:
                return None
            
            return payload['user_id']
            
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return None
    
    def sanitize_input(self, input_data: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_data: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
        sanitized = input_data
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def validate_file_upload(self, 
                           file_path: str,
                           allowed_extensions: List[str],
                           max_size_mb: int = 10) -> Tuple[bool, str]:
        """
        Validate file upload for security.
        
        Args:
            file_path: Path to uploaded file
            allowed_extensions: List of allowed file extensions
            max_size_mb: Maximum file size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        import os
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f"File extension {file_ext} not allowed"
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File size {file_size_mb:.2f}MB exceeds maximum {max_size_mb}MB"
        
        return True, "File upload valid"

# Convenience functions
def create_security_utils(config: Optional[SecurityConfig] = None) -> SecurityUtils:
    """Create a new SecurityUtils instance."""
    return SecurityUtils(config)

def hash_password_simple(password: str) -> str:
    """Simple password hashing function."""
    salt = secrets.token_bytes(16)
    hash_obj, salt = SecurityUtils().hash_password(password, salt)
    return base64.b64encode(hash_obj + salt).decode('utf-8')

def verify_password_simple(password: str, stored_hash: str) -> bool:
    """Simple password verification function."""
    try:
        hash_data = base64.b64decode(stored_hash.encode('utf-8'))
        hash_obj = hash_data[:-16]
        salt = hash_data[-16:]
        return SecurityUtils().verify_password(password, hash_obj, salt)
    except Exception:
        return False 