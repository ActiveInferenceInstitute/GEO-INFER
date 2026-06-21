"""
GEO-INFER-SEC provides security and privacy frameworks for sensitive geospatial information.

This module ensures that geospatial data is collected, processed, shared, 
and stored in a manner that protects individual privacy, organizational 
security, and complies with relevant regulations.
"""

from datetime import datetime, timezone
import logging

__version__ = "0.1.0"
__author__ = "GEO-INFER Team" 
__email__ = "geo-infer@activeinference.institute"

logger = logging.getLogger(__name__)

# Import core security components
try:
    from .core.authentication import AuthenticationManager, UserCredentials, TokenInfo
    from .core.authorization import GeospatialAccessManager, Role, SpatialPermission
    from .core.encryption import GeospatialEncryption
    from .core.audit import AuditLogger, AuditEvent, AuditEventType, AuditEventSeverity
    from .core.access_control import GeospatialAccessManager as AccessManager
    from .models.security_models import SecurityEvent, ThreatLevel
    from .utils.security_utils import SecurityUtils
    
    __all__ = [
        'AuthenticationManager',
        'UserCredentials',
        'TokenInfo',
        'GeospatialAccessManager',
        'AccessManager',
        'Role',
        'SpatialPermission',
        'GeospatialEncryption',
        'AuditLogger',
        'AuditEvent',
        'AuditEventType',
        'AuditEventSeverity',
        'SecurityEvent',
        'ThreatLevel',
        'SecurityUtils'
    ]
except ImportError as e:
    # If imports fail, provide a minimal interface
    __all__ = []
    import logging
    logging.warning(f"Some SEC module components not available: {e}")

# High-level convenience class
class SecurityFramework:
    """
    High-level security framework for GEO-INFER applications.
    
    Provides comprehensive security and privacy protection for geospatial data
    processing and analysis workflows.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.audit_log = []
        # Initialize security components when available
        try:
            self.cognitive = CognitiveSecurity()
            self.privacy = PrivacyFramework()
        except NameError:
            pass
    
    def secure_data_processing(self, data, privacy_level='standard'):
        """Apply security measures to data processing pipeline."""
        # Implementation would apply security controls
        return data
    
    def audit_access(self, user_id, data_access):
        """Audit data access for security compliance."""
        event = {
            "user_id": user_id,
            "data_access": data_access,
            "status": "recorded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.audit_log.append(event)
        logger.info("Recorded security audit access event", extra={"audit_event": event})
        return event
