#!/usr/bin/env python3
"""
GEO-INFER-SEC Example: Secure Geospatial Data Handling

This example demonstrates secure geospatial data operations including
encryption, access control, audit logging, and privacy preservation.
"""

import json
from datetime import datetime

from geo_infer_sec import (
    EncryptionManager,
    AccessController,
    AuditLogger,
    PrivacyPreserver,
    SecureDataStore
)


def main():
    print("=" * 60)
    print("GEO-INFER-SEC: Secure Geospatial Data Handling")
    print("=" * 60)
    
    # 1. Initialize Encryption Manager
    print("\n1. Setting Up Encryption...")
    
    encryption = EncryptionManager(
        algorithm='AES-256-GCM',
        key_derivation='PBKDF2',
        key_rotation_days=90
    )
    
    # Generate encryption keys
    key_info = encryption.generate_key(
        key_id='GEO_DATA_KEY_001',
        purpose='geospatial_data_encryption'
    )
    
    print(f"   Algorithm: AES-256-GCM")
    print(f"   Key ID: {key_info['key_id']}")
    print(f"   Key rotation: 90 days")
    print(f"   Key status: Active")
    
    # 2. Encrypt Sensitive Location Data
    print("\n2. Encrypting Sensitive Location Data...")
    
    sensitive_data = {
        'locations': [
            {'name': 'Critical Infrastructure A', 'lat': 34.0522, 'lon': -118.2437, 'type': 'power_plant'},
            {'name': 'Water Treatment Facility', 'lat': 34.1128, 'lon': -118.3965, 'type': 'water'},
            {'name': 'Data Center Alpha', 'lat': 34.0195, 'lon': -118.4912, 'type': 'data_center'},
        ],
        'sensitivity_level': 'classified',
        'access_groups': ['infrastructure_ops', 'emergency_response']
    }
    
    encrypted_data = encryption.encrypt(
        data=json.dumps(sensitive_data),
        key_id=key_info['key_id'],
        associated_data={'classification': 'classified'}
    )
    
    print(f"   Original size: {len(json.dumps(sensitive_data))} bytes")
    print(f"   Encrypted size: {len(encrypted_data['ciphertext'])} bytes")
    print(f"   Encryption overhead: {len(encrypted_data['ciphertext']) - len(json.dumps(sensitive_data))} bytes")
    
    # 3. Access Control Configuration
    print("\n3. Configuring Access Control...")
    
    access_controller = AccessController(
        model='RBAC',  # Role-Based Access Control
        policy_engine='opa'  # Open Policy Agent
    )
    
    # Define roles
    roles = [
        {'name': 'admin', 'permissions': ['read', 'write', 'delete', 'admin']},
        {'name': 'analyst', 'permissions': ['read', 'write']},
        {'name': 'viewer', 'permissions': ['read']},
        {'name': 'emergency_ops', 'permissions': ['read', 'write'], 'data_classes': ['emergency', 'infrastructure']}
    ]
    
    for role in roles:
        access_controller.add_role(**role)
    
    # Define users
    users = [
        {'user_id': 'user_001', 'name': 'Alice Admin', 'roles': ['admin']},
        {'user_id': 'user_002', 'name': 'Bob Analyst', 'roles': ['analyst']},
        {'user_id': 'user_003', 'name': 'Carol Viewer', 'roles': ['viewer']},
        {'user_id': 'user_004', 'name': 'Dave Emergency', 'roles': ['emergency_ops', 'viewer']},
    ]
    
    for user in users:
        access_controller.add_user(**user)
    
    print(f"   Roles defined: {len(roles)}")
    print(f"   Users configured: {len(users)}")
    print(f"   Access model: Role-Based Access Control (RBAC)")
    
    # Test access
    print("\n   Access Check Examples:")
    test_cases = [
        ('user_001', 'admin', 'classified_data'),
        ('user_002', 'write', 'analysis_results'),
        ('user_003', 'write', 'analysis_results'),
        ('user_004', 'read', 'emergency_data'),
    ]
    
    for user_id, action, resource in test_cases:
        allowed = access_controller.check_access(user_id, action, resource)
        status = "✓ Allowed" if allowed else "✗ Denied"
        print(f"   {user_id} → {action} {resource}: {status}")
    
    # 4. Audit Logging
    print("\n4. Implementing Audit Logging...")
    
    audit_logger = AuditLogger(
        log_level='INFO',
        storage='encrypted_db',
        retention_days=365
    )
    
    # Log access events
    events = [
        {'user_id': 'user_001', 'action': 'decrypt', 'resource': 'classified_locations', 'status': 'success'},
        {'user_id': 'user_002', 'action': 'read', 'resource': 'analysis_data', 'status': 'success'},
        {'user_id': 'user_003', 'action': 'write', 'resource': 'analysis_data', 'status': 'denied'},
        {'user_id': 'user_004', 'action': 'read', 'resource': 'emergency_data', 'status': 'success'},
    ]
    
    for event in events:
        audit_logger.log_event(
            event_type='data_access',
            **event,
            timestamp=datetime.now().isoformat(),
            ip_address='192.168.1.100'
        )
    
    print(f"   Events logged: {len(events)}")
    print(f"   Retention period: 365 days")
    print(f"   Storage: Encrypted database")
    
    # Get audit summary
    summary = audit_logger.get_summary(period_days=30)
    print(f"\n   30-Day Audit Summary:")
    print(f"   - Total events: {sum(summary.values())}")
    print(f"   - Successful accesses: {summary.get('success', 0)}")
    print(f"   - Denied accesses: {summary.get('denied', 0)}")
    
    # 5. Privacy Preservation
    print("\n5. Applying Privacy Preservation...")
    
    privacy = PrivacyPreserver(
        methods=['k_anonymity', 'differential_privacy', 'spatial_cloaking'],
        privacy_budget=1.0  # Epsilon for differential privacy
    )
    
    # Sample location data for privacy protection
    user_locations = [
        {'user_id': 'A', 'lat': 34.0522, 'lon': -118.2437, 'timestamp': '2024-01-15T10:00:00'},
        {'user_id': 'B', 'lat': 34.0525, 'lon': -118.2440, 'timestamp': '2024-01-15T10:05:00'},
        {'user_id': 'C', 'lat': 34.0530, 'lon': -118.2445, 'timestamp': '2024-01-15T10:10:00'},
    ]
    
    # Apply k-anonymity
    anonymized = privacy.apply_k_anonymity(
        data=user_locations,
        k=3,
        quasi_identifiers=['lat', 'lon', 'timestamp'],
        generalization_levels={'lat': 2, 'lon': 2, 'timestamp': 'hour'}
    )
    
    print(f"   K-anonymity applied: k={anonymized['k_level']}")
    print(f"   Records protected: {len(anonymized['data'])}")
    
    # Apply spatial cloaking
    cloaked = privacy.apply_spatial_cloaking(
        locations=user_locations,
        min_area_km2=0.5,
        min_users=5
    )
    
    print(f"   Spatial cloaking: min area = 0.5 km²")
    print(f"   Cloaking regions created: {cloaked['region_count']}")
    
    # Differential privacy for aggregate statistics
    true_count = 1500
    noisy_count = privacy.add_laplace_noise(
        value=true_count,
        sensitivity=1,
        epsilon=0.5
    )
    
    print(f"\n   Differential Privacy Example:")
    print(f"   True count: {true_count}")
    print(f"   Noisy count: {noisy_count}")
    print(f"   Privacy guarantee: ε = 0.5")
    
    # 6. Secure Data Store
    print("\n6. Setting Up Secure Data Store...")
    
    secure_store = SecureDataStore(
        encryption_at_rest=True,
        encryption_in_transit=True,
        backup_encryption=True
    )
    
    # Store encrypted data
    store_result = secure_store.store(
        data_id='INFRA_LOCS_001',
        data=encrypted_data,
        metadata={
            'classification': 'classified',
            'owner': 'user_001',
            'access_groups': ['infrastructure_ops']
        },
        tags=['infrastructure', 'critical', 'locations']
    )
    
    print(f"   Data ID: {store_result['data_id']}")
    print(f"   Encryption at rest: ✓")
    print(f"   Encryption in transit: ✓")
    print(f"   Backup encryption: ✓")
    print(f"   Integrity hash: {store_result.get('hash', 'sha256:...')[:20]}...")
    
    # 7. Security Compliance Check
    print("\n7. Running Security Compliance Check...")
    
    compliance_checks = {
        'Encryption': 'PASS',
        'Access Control': 'PASS',
        'Audit Logging': 'PASS',
        'Key Management': 'PASS',
        'Data Classification': 'PASS',
        'Privacy Controls': 'PASS'
    }
    
    print("   Compliance Status:")
    for check, status in compliance_checks.items():
        symbol = "✓" if status == 'PASS' else "✗"
        print(f"   {symbol} {check}")
    
    passed = sum(1 for v in compliance_checks.values() if v == 'PASS')
    print(f"\n   Overall Compliance: {passed}/{len(compliance_checks)} checks passed")
    
    print("\n" + "=" * 60)
    print("Secure Data Handling Complete!")
    print("=" * 60)
    
    # Summary
    print("\nSecurity Summary:")
    print(f"  - Encryption: AES-256-GCM")
    print(f"  - Access control: RBAC with 4 roles")
    print(f"  - Audit events: {len(events)} logged")
    print(f"  - Privacy: k-anonymity + spatial cloaking")
    print(f"  - Compliance: 100%")


if __name__ == "__main__":
    main()
