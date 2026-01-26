# api
 ## Overview
 This directory contains api components. It includes 5 Python modules. ## Components
 ### compliance_ap
i
.py Compliance API module for tracking and reporting on regulatory compliance. **Classes**: `ComplianceStatusCreate`, `ComplianceMetricCreate`, `EvaluationData`, `GeoPoint`, `ReportParams`, `ComplianceAPI`, `Config`, `Config`, `Config` ### legal_ap
i
.py Legal API module for geospatial legal analysis and jurisdictions. **Classes**: `GeometryModel`, `JurisdictionCreate`, `RegulationCreate`, `RegulatoryFrameworkCreate`, `PointLocation`, `LegalAPI`, `Config`, `Config`, `Config`, `Config` ### normative_ap
i
.py Normative API module for inferring, analyzing, and simulating social norms. **Classes**: `GeometryModel`, `SocialNormCreate`, `NormDiffusionRequest`, `NormativeInferenceRequest`, `NormPolicyImpactRequest`, `PointLocation`, `NormativeAPI`, `Config`, `Config`, `Config`, `Config`, `Config` ### policy_ap
i
.py Policy API module for geospatial policy analysis and impact assessment. **Classes**: `GeometryModel`, `PolicyCreate`, `PolicyImplementationCreate`, `ImpactAssessmentRequest`, `RegulationComparisonRequest`, `PolicyAPI`, `Config`, `Config`, `Config`, `Config`, `Config` ### zoning_ap
i
.py Zoning API module for geospatial zoning analysis and land use management. **Classes**: `GeometryModel`, `ZoningCodeCreate`, `ZoningDistrictCreate`, `LandUseTypeCreate`, `ZoningChangeRequest`, `PointLocation`, `LandClassificationRequest`, `ZoningAPI`, `Config`, `Config`, `Config`, `Config`, `Config`, `Config` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 