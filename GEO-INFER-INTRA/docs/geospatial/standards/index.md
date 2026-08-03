# Geospatial Standards

This section provides information about geospatial standards developed by
organizations such as the Open Geospatial Consortium (OGC), ISO, and others
that ensure interoperability and data quality across geospatial systems.

## Contents

- [GEO-INFER Geospatial Standards](../../geospatial_standards.md) — the
  repository's own geospatial conventions and contracts.
- [Coordinate Systems](../concepts/coordinate_systems.md) — geographic and
  projected coordinate systems.
- [Spatial Reference Systems](../concepts/spatial_reference_systems.md) —
  EPSG and datum standards.
- [Data Formats](../data_formats/index.md) — H3 and other data formats.
- [Uncertainty and Accuracy](../concepts/uncertainty_accuracy.md) — data
  quality considerations.

## Key Standards Organizations

### Open Geospatial Consortium (OGC)

The OGC is an international consortium of more than 500 businesses, government
agencies, research organizations, and universities working to make geospatial
information and services FAIR — Findable, Accessible, Interoperable, and
Reusable.

### International Organization for Standardization (ISO)

ISO Technical Committee 211 (ISO/TC 211) is responsible for the ISO geographic
information series of standards, which includes standards for metadata,
services, data models, and more.

### Federal Geographic Data Committee (FGDC)

The FGDC coordinates the development of the National Spatial Data
Infrastructure in the United States and has developed standards for geospatial
metadata.

## Common Geospatial Standards

### Data Format Standards

- **GeoJSON** — JSON format for encoding geographic data structures.
- **KML** — XML language for expressing geographic annotation and
  visualization.
- **GML** — XML grammar for expressing geographical features.
- **GeoPackage** — platform-independent, standards-based data format for GIS.

### Web Service Standards

- **Web Map Service (WMS)** — standard for serving georeferenced map images.
- **Web Feature Service (WFS)** — standard for requesting and transmitting
  vector features.
- **Web Coverage Service (WCS)** — standard for accessing raster coverages.
- **Web Processing Service (WPS)** — standard for executing spatial processes.

### Metadata Standards

- **ISO 19115** — standard for geospatial metadata.
- **ISO 19139** — XML schema implementation of ISO 19115.
- **Dublin Core** — minimal metadata element set for cross-domain resource
  description.

### Coordinate Reference System Standards

- **EPSG Geodetic Parameter Dataset** — registry of coordinate reference
  systems and transformations.
- **ISO 19111** — standard for spatial referencing by coordinates.

## Importance of Standards

Geospatial standards are crucial for:

- Ensuring interoperability between different systems and platforms.
- Facilitating data exchange and sharing.
- Reducing development costs through common interfaces.
- Enabling long-term data preservation and access.
- Supporting spatial data infrastructures.

## GEO-INFER Implementation

GEO-INFER implements these standards through:

- Standards-compliant data models and APIs.
- Support for standard data formats and encodings (GeoJSON, H3, and related).
- Integration with standardized web services.
- Metadata management using standard schemas.
- Documentation of standard compliance.

## Related Resources

- [Data Formats](../data_formats/index.md)
- [API Documentation](../../api/index.md)
- [Architecture](../../architecture/index.md)
