# Agent
: core

## Scope
 This directory contains core components for the module. It provides 48 classes and 3 functions.

## Classes
 and Functions

### SpatialPermission
 Represents a spatial permission for accessing geographic areas.

**Methods**:
- `contains_point(lat: float, lon: float) -> bool`: Check if a point is contained in the permitted area.
- `filter_geodataframe(gdf: gpd.GeoDataFrame, geometry_col: str) -> gpd.GeoDataFrame`: Filter a GeoDataFrame to only include geometries within the permitted area.

### Role
 Represents a security role with associated permissions.

**Methods**:
- `add_permission(permission: SpatialPermission) -> None`: Add a permission to the role.
- `has_permission(permission_name: str) -> bool`: Check if the role has a specific permission.
- `get_accessible_area() -> Optional[Union[Polygon, MultiPolygon]]`: Get the combined area of all spatial permissions.

### GeospatialAccessManager
 Manages access control for geospatial data.

**Methods**:
- `add_role(role: Role) -> None`: Add a role to the manager.
- `assign_role_to_user(user_id: str, role_name: str) -> bool`: Assign a role to a user.
- `get_user_roles(user_id: str) -> List[Role]`: Get all roles assigned to a user.
- `generate_token(user_id: str, expiration_hours: int) -> str`: Generate a JWT token for a user.
- `validate_token(token: str) -> Optional[Dict]`: Validate a JWT token.
- `can_access_location(user_id: str, lat: float, lon: float) -> bool`: Check if a user can access data at a specific location.
- `filter_geodataframe(user_id: str, gdf: gpd.GeoDataFrame, geometry_col: str) -> gpd.GeoDataFrame`: Filter a GeoDataFrame based on user's spatial permissions.

### GeospatialAnonymizer
 Provides methods for anonymizing geospatial data while preserving utility.

**Methods**:
- `location_perturbation(gdf: gpd.GeoDataFrame, epsilon: float, geometry_col: str) -> gpd.GeoDataFrame`: Apply random perturbation to point locations.
- `spatial_k_anonymity(gdf: gpd.GeoDataFrame, k: int, h3_resolution: int, geometry_col: str) -> gpd.GeoDataFrame`: Apply spatial k-anonymity by aggregating points into H3 cells.
- `geographic_masking(gdf: gpd.GeoDataFrame, attribute_cols: List[str], admin_boundaries: gpd.GeoDataFrame, admin_id_col: str, geometry_col: str) -> gpd.GeoDataFrame`: Apply geographic masking by aggregating data to administrative boundaries.

### AuditEventType
 Types of audit events.

### AuditEventSeverity
 Severity levels for audit events.

### AuditEvent
 Represents an audit log event.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert audit event to dictionary.
- `to_json() -> str`: Convert audit event to JSON string.

### AuditLogger
 Audit logger for security and compliance events.

**Methods**:
- `log_event(event_type: AuditEventType, user_id: Optional[str], username: Optional[str], resource: Optional[str], action: Optional[str], result: str, severity: AuditEventSeverity, ip_address: Optional[str], user_agent: Optional[str], details: Optional[Dict[str, Any]], metadata: Optional[Dict[str, Any]]) -> AuditEvent`: Log an audit event.
- `log_authentication(username: str, user_id: Optional[str], result: str, ip_address: Optional[str], user_agent: Optional[str], details: Optional[Dict[str, Any]]) -> AuditEvent`: Log an authentication event.
- `log_authorization(user_id: str, username: Optional[str], resource: str, action: str, result: str, ip_address: Optional[str], details: Optional[Dict[str, Any]]) -> AuditEvent`: Log an authorization event.
- `log_data_access(user_id: str, username: Optional[str], resource: str, action: str, result: str, ip_address: Optional[str], details: Optional[Dict[str, Any]]) -> AuditEvent`: Log a data access event.
- `get_events(event_type: Optional[AuditEventType], user_id: Optional[str], start_time: Optional[datetime], end_time: Optional[datetime], severity: Optional[AuditEventSeverity], limit: int) -> List[AuditEvent]`: Retrieve audit events with filtering.
- `generate_compliance_report(start_time: datetime, end_time: datetime, report_type: str) -> Dict[str, Any]`: Generate a compliance report from audit logs.

### UserCredentials
 User credentials for authentication.

### TokenInfo
 JWT token information.

### AuthenticationManager
 Authentication manager for user authentication and token management.

**Methods**:
- `hash_password(password: str, salt: Optional[bytes]) -> Tuple[str, bytes]`: Hash a password using PBKDF2.
- `verify_password(password: str, password_hash: str, salt: str) -> bool`: Verify a password against a hash.
- `register_user(username: str, password: str, email: Optional[str], user_id: Optional[str]) -> UserCredentials`: Register a user.
- `authenticate(username: str, password: str, mfa_code: Optional[str]) -> Optional[TokenInfo]`: Authenticate a user and generate access token.
- `generate_tokens(user_id: str, username: str, scope: Optional[List[str]]) -> TokenInfo`: Generate access and refresh tokens.
- `validate_token(token: str) -> Optional[Dict[str, Any]]`: Validate a JWT access token.
- `refresh_access_token(refresh_token: str) -> Optional[TokenInfo]`: Generate a access token from a refresh token.
- `revoke_token(token: str) -> bool`: Revoke a refresh token.
- `get_user(username: str) -> Optional[UserCredentials]`: Get user credentials by username.
- `enable_mfa(username: str, secret: str) -> bool`: Enable multi-factor authentication for a user.
- `disable_mfa(username: str) -> bool`: Disable multi-factor authentication for a user.

### PermissionType
 Types of permissions.

### AuthorizationManager
 Authorization manager implementing RBAC and ABAC.

**Methods**:
- `check_permission(user_id: str, resource: str, permission: PermissionType, attributes: Optional[Dict[str, Any]]) -> bool`: Check if a user has permission to perform an action on a resource.
- `grant_permission(user_id: str, resource: str, permission: PermissionType, spatial_bounds: Optional[Any]) -> bool`: Grant a permission to a user.
- `revoke_permission(user_id: str, resource: str, permission: PermissionType) -> bool`: Revoke a permission from a user.
- `list_user_permissions(user_id: str) -> List[Dict[str, Any]]`: List all permissions for a user.

### BehaviorType
 Types of behavioral patterns.

### ThreatHuntingType
 Types of threat hunting activities.

### LearningMode
 Machine learning modes.

### BehaviorProfile
 Represents a behavioral profile for an entity.

### CognitiveThreat
 Represents a threat detected through cognitive analysis.

### ThreatHuntingResult
 Results from threat hunting activities.

### CognitiveSecurityManager
 AI-driven cognitive security management system.

**Methods**:
- `analyze_user_behavior(user_id: str, events: List[SecurityEvent]) -> BehaviorProfile`: Analyze user behavior patterns.
- `detect_anomalies(events: List[SecurityEvent]) -> List[Dict[str, Any]]`: Detect anomalies in security events using ML.
- `predict_threats(historical_data: List[SecurityEvent]) -> List[CognitiveThreat]`: Predict potential threats using ML models.
- `conduct_threat_hunt(hypothesis: str, hunt_type: ThreatHuntingType, search_criteria: Dict[str, Any]) -> ThreatHuntingResult`: Conduct AI-assisted threat hunting.
- `start_cognitive_monitoring()`: Start cognitive security monitoring.
- `stop_cognitive_monitoring()`: Stop cognitive security monitoring.
- `add_security_event(event: SecurityEvent)`: Add a security event to the cognitive analysis buffer.
- `get_behavior_profile(entity_id: str) -> Optional[BehaviorProfile]`: Get behavior profile for an entity.
- `get_cognitive_threats() -> List[CognitiveThreat]`: Get all active cognitive threats.
- `get_threat_hunting_results() -> List[ThreatHuntingResult]`: Get all threat hunting results.
- `add_alert_callback(callback: callable)`: Add a callback function for cognitive security alerts.
- `generate_cognitive_report() -> Dict[str, Any]`: Generate a cognitive security report.

### ComplianceRegime
 Enumeration of supported compliance regimes.

### ComplianceRule
 Represents a compliance rule for geospatial data.

**Methods**:
- `check(data: Any) -> bool`: Check if data complies with the rule.

### ComplianceViolation
 Represents a compliance violation.

**Methods**:
- `to_dict() -> Dict`: Convert the violation to a dictionary.

### ComplianceFramework
 Framework for managing geospatial data compliance.

**Methods**:
- `add_rule(rule: ComplianceRule) -> None`: Add a compliance rule.
- `get_rules_by_regime(regime: ComplianceRegime) -> List[ComplianceRule]`: Get all rules for a specific compliance regime.
- `check_compliance(data: Any, data_reference: str, regimes: Optional[List[ComplianceRegime]]) -> List[ComplianceViolation]`: Check compliance of data against rules.
- `check_geodataframe_compliance(gdf: gpd.GeoDataFrame, data_reference: str, regimes: Optional[List[ComplianceRegime]]) -> List[ComplianceViolation]`: Check compliance of a GeoDataFrame.
- `generate_compliance_report(output_format: str, output_file: Optional[str]) -> Union[str, Dict]`: Generate a compliance report.
- `clear_violations() -> None`: Clear all recorded violations.

### ThreatType
 Types of digital security threats.

### SecurityEventType
 Types of security events.

### EncryptionAlgorithm
 Supported encryption algorithms.

### DigitalThreat
 Represents a detected digital security threat.

### SecurityPolicy
 Represents a digital security policy.

### NetworkConnection
 Represents a network connection for monitoring.

### VulnerabilityReport
 Represents a vulnerability assessment report.

### DigitalSecurityManager
 digital security management system.

**Methods**:
- `detect_threat(event_data: Dict[str, Any]) -> Optional[DigitalThreat]`: Analyze an event for potential threats.
- `monitor_network_connection(connection: NetworkConnection) -> bool`: Monitor a network connection for security issues.
- `block_ip(ip_address: str, duration_hours: int) -> bool`: Block an IP address for a specified duration.
- `unblock_ip(ip_address: str) -> bool`: Unblock an IP address.
- `is_ip_blocked(ip_address: str) -> bool`: Check if an IP address is blocked.
- `encrypt_data(data: Union[str, bytes], key_id: str, algorithm: EncryptionAlgorithm) -> Optional[bytes]`: Encrypt data using specified algorithm and key.
- `decrypt_data(encrypted_data: bytes, key_id: str, algorithm: EncryptionAlgorithm) -> Optional[bytes]`: Decrypt data using specified algorithm and key.
- `rotate_encryption_key(key_id: str) -> bool`: Rotate an encryption key.
- `check_key_rotation_schedule()`: Check if any keys need rotation.
- `create_jwt_token(user_id: str, permissions: List[str], expires_in_hours: int) -> Optional[str]`: Create a JWT token for user authentication.
- `verify_jwt_token(token: str) -> Optional[Dict[str, Any]]`: Verify and decode a JWT token.
- `hash_password(password: str, salt: Optional[bytes]) -> Tuple[bytes, bytes]`: Hash a password with salt.
- `verify_password(password: str, password_hash: bytes, salt: bytes) -> bool`: Verify a password against its hash.
- `check_rate_limit(identifier: str, limit_per_minute: int) -> bool`: Check if an identifier (IP, user, etc.) exceeds rate limit.
- `run_vulnerability_scan(target_system: str) -> VulnerabilityReport`: Run a vulnerability scan on a target system.
- `start_monitoring()`: Start digital security monitoring.
- `stop_monitoring()`: Stop digital security monitoring.
- `log_security_event(event_type: SecurityEventType, metadata: Dict[str, Any]) -> SecurityEvent`: Log a security event.
- `get_security_report(start_date: datetime, end_date: datetime) -> Dict[str, Any]`: Generate a security report.
- `add_alert_callback(callback: callable)`: Add a callback function for security alerts.
- `get_active_threats() -> List[DigitalThreat]`: Get all active threats.
- `mitigate_threat(threat_id: str, mitigation_notes: str) -> bool`: Mark a threat as mitigated.

### GeospatialEncryption
 Provides encryption methods for geospatial data.

**Methods**:
- `from_password(cls, password: str, salt: Optional[bytes]) -> 'GeospatialEncryption'`: Create an encryptor using a password-derived key.
- `get_key() -> bytes`: Get the encryption key.
- `encrypt_text(text: str) -> bytes`: Encrypt a text string.
- `decrypt_text(encrypted_data: bytes) -> str`: Decrypt encrypted text data.
- `encrypt_json(data: Dict) -> bytes`: Encrypt a dictionary as JSON.
- `decrypt_json(encrypted_data: bytes) -> Dict`: Decrypt JSON data.
- `encrypt_coordinates(lat: float, lon: float) -> str`: Encrypt latitude and longitude.
- `decrypt_coordinates(encrypted_coords: str) -> Tuple[float, float]`: Decrypt coordinates.
- `encrypt_geodataframe(gdf: gpd.GeoDataFrame, sensitive_columns: Optional[List[str]], encrypt_coordinates: bool) -> gpd.GeoDataFrame`: Encrypt sensitive columns in a GeoDataFrame.
- `decrypt_geodataframe(gdf: gpd.GeoDataFrame, encrypted_columns: List[str], geometry_col: str) -> gpd.GeoDataFrame`: Decrypt columns in a GeoDataFrame.

### AsymmetricEncryption
 Provides asymmetric encryption for secure data sharing.

**Methods**:
- `generate_keys(cls, key_size: int) -> 'AsymmetricEncryption'`: Generate a key pair.
- `export_private_key() -> bytes`: Export the private key in PEM format.
- `export_public_key() -> bytes`: Export the public key in PEM format.
- `from_pem(cls, private_key_pem: Optional[bytes], public_key_pem: Optional[bytes]) -> 'AsymmetricEncryption'`: Create an instance from PEM encoded keys.
- `encrypt(data: bytes) -> bytes`: Encrypt data using the public key.
- `decrypt(encrypted_data: bytes) -> bytes`: Decrypt data using the private key.
- `encrypt_text(text: str) -> bytes`: Encrypt a text string.
- `decrypt_text(encrypted_data: bytes) -> str`: Decrypt text data.
- `encrypt_json(data: Dict) -> bytes`: Encrypt a dictionary as JSON.
- `decrypt_json(encrypted_data: bytes) -> Dict`: Decrypt JSON data.

### SecurityDomain
 Security domains.

### ThreatCorrelationType
 Types of threat correlation.

### IncidentSeverity
 Incident severity levels.

### IntegratedThreat
 Represents a threat that spans multiple security domains.

### SecurityIncident
 Represents a security incident.

### IntegratedSecurityManager
 Holistic security management system integrating all security domains.

**Methods**:
- `start_integrated_monitoring()`: Start integrated security monitoring and orchestration.
- `stop_integrated_monitoring()`: Stop integrated security monitoring.
- `get_security_dashboard() -> Dict[str, Any]`: Get security dashboard data.
- `get_integrated_threats() -> List[IntegratedThreat]`: Get all integrated threats.
- `get_security_incidents(status: Optional[str]) -> List[SecurityIncident]`: Get security incidents, optionally filtered by status.
- `resolve_incident(incident_id: str, resolution_notes: str) -> bool`: Resolve a security incident.
- `add_response_handler(action: str, handler: callable)`: Add a response handler for specific actions.
- `add_alert_callback(callback: callable)`: Add alert callback for integrated security notifications.

### AccessControlType
 Types of access control systems.

### SurveillanceType
 Types of surveillance systems.

### SecurityZoneType
 Types of security zones.

### AccessControlDevice
 Represents a physical access control device.

### SurveillanceDevice
 Represents a surveillance device.

### SecurityZone
 Represents a security zone with specific access requirements.

### PhysicalThreat
 Represents a detected physical threat.

### PhysicalSecurityManager
 physical security management system.

**Methods**:
- `add_security_zone(zone: SecurityZone) -> bool`: Add a security zone.
- `get_security_zone(zone_id: str) -> Optional[SecurityZone]`: Get a security zone by ID.
- `get_zones_for_location(location: Point) -> List[SecurityZone]`: Get all security zones that contain a given location.
- `update_zone_boundary(zone_id: str, new_boundary: Union[Polygon, MultiPolygon]) -> bool`: Update the boundary of a security zone.
- `add_access_device(device: AccessControlDevice) -> bool`: Add a access control device.
- `verify_access_permission(user_id: str, device_id: str, clearance_level: int) -> Tuple[bool, str]`: Verify if a user has permission to access a device.
- `add_surveillance_device(device: SurveillanceDevice) -> bool`: Add a surveillance device.
- `get_surveillance_coverage(location: Point) -> List[SurveillanceDevice]`: Get all surveillance devices that cover a specific location.
- `calculate_surveillance_coverage_map() -> gpd.GeoDataFrame`: Calculate overall surveillance coverage map.
- `detect_intrusion(location: Point, detection_method: str, confidence: float) -> Optional[PhysicalThreat]`: Detect and register a potential intrusion.
- `detect_unauthorized_access(device_id: str, user_id: str, attempted_at: datetime) -> Optional[PhysicalThreat]`: Detect unauthorized access attempts.
- `add_alert_callback(callback: callable)`: Add a callback function for security alerts.
- `start_monitoring()`: Start continuous security monitoring.
- `stop_monitoring()`: Stop security monitoring.
- `generate_security_report(start_date: datetime, end_date: datetime) -> Dict[str, Any]`: Generate a security report.
- `get_active_threats() -> List[PhysicalThreat]`: Get all active threats.
- `resolve_threat(threat_id: str, resolution_notes: str) -> bool`: Mark a threat as resolved.

### create_gdpr_validators
 `create_gdpr_validators() -> Dict[str, ComplianceRule]` Create GDPR compliance validators.

### personal_data_minimization
 `personal_data_minimization(gdf: gpd.GeoDataFrame) -> bool`

### location_precision
 `location_precision(gdf: gpd.GeoDataFrame) -> bool`

## Capabilities

- **48 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-SEC/src/geo_infer_sec/core`
- **Type**: Directory Node
