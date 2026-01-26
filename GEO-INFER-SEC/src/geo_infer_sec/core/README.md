# core
 ## Overview
 This directory contains core components. It includes 11 Python modules. ## Components
 ### access_contro
l
.py Role-based access control for geospatial data. **Classes**: `SpatialPermission`, `Role`, `GeospatialAccessManager` ### anonymizatio
n
.py Geospatial data anonymization techniques. **Classes**: `GeospatialAnonymizer` ### audi
t
.py Audit logging system for GEO-INFER-SEC. **Classes**: `AuditEventType`, `AuditEventSeverity`, `AuditEvent`, `AuditLogger` ### authenticatio
n
.py Authentication system for GEO-INFER-SEC. **Classes**: `UserCredentials`, `TokenInfo`, `AuthenticationManager` ### authorizatio
n
.py Authorization framework for GEO-INFER-SEC. **Classes**: `PermissionType`, `AuthorizationManager` ### cognitive_securit
y
.py Cognitive Security Module for GEO-INFER-SEC **Classes**: `BehaviorType`, `ThreatHuntingType`, `LearningMode`, `BehaviorProfile`, `CognitiveThreat`, `ThreatHuntingResult`, `CognitiveSecurityManager` ### complianc
e
.py Compliance frameworks for geospatial data. **Classes**: `ComplianceRegime`, `ComplianceRule`, `ComplianceViolation`, `ComplianceFramework` **Functions**: `create_gdpr_validators`, `personal_data_minimization`, `location_precision` ### digital_securit
y
.py Digital Security Module for GEO-INFER-SEC **Classes**: `ThreatType`, `SecurityEventType`, `EncryptionAlgorithm`, `DigitalThreat`, `SecurityPolicy`, `NetworkConnection`, `VulnerabilityReport`, `DigitalSecurityManager` ### encryptio
n
.py Encryption utilities for geospatial data. **Classes**: `GeospatialEncryption`, `AsymmetricEncryption` ### integrated_securit
y
.py Integrated Security Orchestrator for GEO-INFER-SEC **Classes**: `SecurityDomain`, `ThreatCorrelationType`, `IncidentSeverity`, `IntegratedThreat`, `SecurityIncident`, `IntegratedSecurityManager` ### physical_securit
y
.py Physical Security Module for GEO-INFER-SEC **Classes**: `AccessControlType`, `SurveillanceType`, `SecurityZoneType`, `AccessControlDevice`, `SurveillanceDevice`, `SecurityZone`, `PhysicalThreat`, `PhysicalSecurityManager` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 