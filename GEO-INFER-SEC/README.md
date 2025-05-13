# GEO-INFER-SEC

## Overview
GEO-INFER-SEC provides security and privacy frameworks for sensitive geospatial information within the GEO-INFER ecosystem. This module ensures that geospatial data is collected, processed, shared, and stored in a manner that protects individual privacy, organizational security, and complies with relevant regulations.

## Key Features
- **Geospatial data anonymization techniques**
  - Location perturbation with configurable privacy parameter
  - Spatial k-anonymity using H3 hexagonal grid
  - Geographic masking through administrative boundary aggregation
- **Role-based access control for location data**
  - Spatial permissions with geographic boundaries
  - Attribute-level access control
  - JWT token-based authentication
- **Compliance frameworks for international data regulations**
  - GDPR, CCPA, HIPAA, and other regulatory support
  - Compliance validation and reporting
  - Risk assessment and management
- **Secure data handling**
  - Symmetric and asymmetric encryption for geospatial data
  - Secure key management
  - Coordinate-level encryption
- **Privacy-preserving utilities**
  - PII detection and redaction
  - Spatial outlier detection
  - Audit logging and reporting

## Installation

### Prerequisites
- Python 3.8 or newer
- GDAL/OGR libraries for geospatial operations
- H3 for hexagonal grid indexing

### Install from Source
```bash
# Clone the repository
git clone https://github.com/your-organization/INFER-GEO.git
cd INFER-GEO/GEO-INFER-SEC

# Install dependencies and the package
pip install -e .
```

## Usage Examples

### Anonymizing Geospatial Data

```python
import geopandas as gpd
from geo_infer_sec.core.anonymization import GeospatialAnonymizer

# Load point data
points = gpd.read_file("sensitive_locations.geojson")

# Create anonymizer
anonymizer = GeospatialAnonymizer()

# Apply location perturbation (random noise)
perturbed = anonymizer.location_perturbation(points, epsilon=100.0)  # 100 meter max distance

# Apply spatial k-anonymity
k_anon = anonymizer.spatial_k_anonymity(points, k=5, h3_resolution=9)

# Save anonymized data
perturbed.to_file("perturbed_locations.geojson", driver="GeoJSON")
k_anon.to_file("k_anonymized_locations.geojson", driver="GeoJSON")
```

### Encrypting Sensitive Data

```python
import geopandas as gpd
from geo_infer_sec.core.encryption import GeospatialEncryption

# Load data
data = gpd.read_file("sensitive_data.geojson")

# Create encryptor with a password
encryptor = GeospatialEncryption.from_password("secure-password")

# Encrypt sensitive columns and geometry
encrypted = encryptor.encrypt_geodataframe(
    data, 
    sensitive_columns=["name", "address", "phone"],
    encrypt_coordinates=True
)

# Save encrypted data
encrypted.to_file("encrypted_data.geojson", driver="GeoJSON")

# Save encryption key for later decryption
with open("encryption_key.bin", "wb") as f:
    f.write(encryptor.get_key())
```

### Managing Access Control

```python
from geo_infer_sec.core.access_control import (
    GeospatialAccessManager, Role, SpatialPermission
)
from shapely.geometry import Polygon

# Create access manager
manager = GeospatialAccessManager(secret_key="your-secret-key")

# Create a spatial permission (area of NYC)
nyc_area = Polygon([
    (-74.02, 40.70), (-73.92, 40.70),
    (-73.92, 40.80), (-74.02, 40.80)
])
nyc_permission = SpatialPermission(
    name="nyc_access", 
    geometry=nyc_area,
    attributes=["category", "value"]
)

# Create a role with the permission
analyst_role = Role(name="data_analyst")
analyst_role.add_permission(nyc_permission)

# Add role to manager
manager.add_role(analyst_role)

# Assign role to a user
manager.assign_role_to_user("user123", "data_analyst")

# Generate access token
token = manager.generate_token("user123", expiration_hours=24)
print(f"Access token: {token}")

# Check if a user can access a location
has_access = manager.can_access_location("user123", 40.75, -73.98)  # In NYC
print(f"Has access: {has_access}")
```

## Command-Line Interface

GEO-INFER-SEC provides a comprehensive CLI for security operations.

```bash
# Get help
python -m geo_infer_sec.cli --help

# Anonymize geospatial data
python -m geo_infer_sec.cli anonymize sensitive_data.geojson anonymized_data.geojson --method k-anonymity --k 5

# Encrypt sensitive data
python -m geo_infer_sec.cli encrypt sensitive_data.geojson encrypted_data.geojson --password "secure-password" --encrypt-geometry

# Check compliance with regulations
python -m geo_infer_sec.cli check-compliance data.geojson --regimes gdpr,ccpa --format html --output-file compliance_report.html

# Perform a security audit
python -m geo_infer_sec.cli audit data.geojson --check-pii --check-bounds --detect-outliers

# Generate a risk assessment
python -m geo_infer_sec.cli risk-assessment --format html --output-file risk_report.html
```

## Security Best Practices

When using GEO-INFER-SEC, follow these best practices:

1. **Least privilege principle**: Only provide access to the minimal spatial areas and attributes needed.
2. **Data minimization**: Collect and retain only the necessary geospatial data.
3. **Key management**: Store encryption keys securely, separate from encrypted data.
4. **Regular auditing**: Periodically review access logs and permissions.
5. **Layered security**: Use multiple anonymization techniques for sensitive data.
6. **Privacy by design**: Consider privacy implications early in application design.

## Module Structure

```
GEO-INFER-SEC/
├── src/
│   └── geo_infer_sec/
│       ├── api/           # API definitions
│       │   └── security_api.py
│       ├── core/          # Core functionality 
│       │   ├── access_control.py
│       │   ├── anonymization.py
│       │   ├── compliance.py
│       │   └── encryption.py
│       ├── models/        # Data models
│       │   └── risk_assessment.py
│       └── utils/         # Utility functions
│           └── security_utils.py
├── tests/                 # Test suite
├── examples/              # Example scripts
└── config/                # Configuration
```

## Integration with Other GEO-INFER Modules

GEO-INFER-SEC integrates with:
- **GEO-INFER-OPS** for secure operations and monitoring
- **GEO-INFER-DATA** for secure data management and storage
- **GEO-INFER-API** for API security and access control
- **GEO-INFER-APP** for user authentication and authorization
- **GEO-INFER-SPACE** for spatial indexing and query security

## Contributing

Please follow the contribution guidelines in the main GEO-INFER documentation. All code should adhere to the standards defined in `.cursorrules`.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 