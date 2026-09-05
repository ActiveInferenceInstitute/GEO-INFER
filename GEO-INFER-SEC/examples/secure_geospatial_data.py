#!/usr/bin/env python3
"""
GEO-INFER-SEC Example: Secure Geospatial Data Handling

Thin orchestration over the real public API of ``geo_infer_sec``:
encryption (GeospatialEncryption), spatial access control
(GeospatialAccessManager), audit logging (AuditLogger), and point-data
anonymization (GeospatialAnonymizer).
"""

import base64
import tempfile
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

from geo_infer_sec import AuditLogger, GeospatialAccessManager, GeospatialEncryption
from geo_infer_sec.core.access_control import Role, SpatialPermission
from geo_infer_sec.core.anonymization import GeospatialAnonymizer


def main() -> None:
    print("=" * 60)
    print("GEO-INFER-SEC: Secure Geospatial Data Handling")
    print("=" * 60)

    # 1. Encryption: derive a key from a password and round-trip a payload.
    print("\n1. Encrypting Sensitive Location Data...")
    encryption = GeospatialEncryption.from_password(
        "correct-horse-battery-staple", salt=base64.b64decode("c2VjdXJlLXNhbHQ9")
    )

    sensitive_payload = {
        "locations": [
            {"name": "Critical Infrastructure A", "lat": 34.0522, "lon": -118.2437},
            {"name": "Water Treatment Facility", "lat": 34.1128, "lon": -118.3965},
        ],
        "classification": "confidential",
    }
    encrypted = encryption.encrypt_json(sensitive_payload)
    decrypted = encryption.decrypt_json(encrypted)
    assert decrypted == sensitive_payload
    print(f"   Ciphertext size: {len(encrypted)} bytes")
    print(f"   Round-trip verified: {decrypted == sensitive_payload}")

    # 2. Spatial access control: roles, JWT tokens, point checks.
    print("\n2. Configuring Spatial Access Control...")
    access = GeospatialAccessManager(secret_key="demo-signing-secret")
    la_basin = Point(-118.24, 34.05).buffer(0.2)
    access.add_role(
        Role(
            name="infrastructure_viewer",
            permissions=[SpatialPermission(name="view_facilities", geometry=la_basin)],
        )
    )
    access.add_role(
        Role(
            name="field_responder",
            permissions=[SpatialPermission(name="view_facilities", geometry=None)],
        )
    )
    access.assign_role_to_user("alice", "infrastructure_viewer")
    access.assign_role_to_user("dave", "field_responder")

    token = access.generate_token("alice")
    payload = access.validate_token(token)
    print(f"   Token subject: {payload['user_id']}")
    print(f"   alice inside LA basin: {access.can_access_location('alice', 34.05, -118.24)}")
    print(f"   alice in New York:     {access.can_access_location('alice', 40.71, -74.00)}")

    # 3. Audit logging: data-access events in a temp log.
    print("\n3. Recording Audit Events...")
    with tempfile.TemporaryDirectory() as tmp:
        audit = AuditLogger(
            log_file=Path(tmp) / "audit.log", enable_console=False, enable_file=True
        )
        audit.log_data_access(
            "alice", username="Alice", resource="facility_locations", action="read"
        )
        audit.log_data_access(
            "mallory",
            username="Mallory",
            resource="facility_locations",
            action="delete",
            result="denied",
            ip_address="203.0.113.7",
        )
        report = audit.generate_compliance_report(
            start_time=audit.events[0].timestamp,
            end_time=audit.events[-1].timestamp,
            report_type="summary",
        )
        print(f"   Events logged: {len(audit.events)}")
        print(f"   Results: {report.get('result_counts', {})}")

    # 4. Anonymization: seeded perturbation and k-anonymity (EPSG:4326).
    print("\n4. Anonymizing Point Data...")
    gdf = gpd.GeoDataFrame(
        {"facility": ["plant_a", "water_b", "dc_alpha"]},
        geometry=[
            Point(-118.2437, 34.0522),
            Point(-118.3965, 34.1128),
            Point(-118.4912, 34.0195),
        ],
        crs="EPSG:4326",
    )
    anonymizer = GeospatialAnonymizer(seed=42)
    perturbed = anonymizer.location_perturbation(gdf, epsilon=500.0)
    grouped = anonymizer.spatial_k_anonymity(gdf, k=2, h3_resolution=8)
    print(f"   Perturbation displacement (max, deg): "
          f"{max(a.distance(b) for a, b in zip(gdf.geometry, perturbed.geometry)):.6f}")
    print(f"   K-anonymity output rows: {len(grouped)} (from {len(gdf)} input points)")

    print("\n" + "=" * 60)
    print("Secure Data Handling Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
