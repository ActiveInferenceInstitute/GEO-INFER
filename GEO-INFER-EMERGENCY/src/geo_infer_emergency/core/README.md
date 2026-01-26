# core
 ## Overview
 This directory contains core components. It includes 5 Python modules. ## Components
 ### awarenes
s
.py Situational awareness module. **Classes**: `ThreatLevel`, `DataSource`, `SensoryInput`, `LayerConfig`, `SituationalAwareness` ### coordinato
r
.py Emergency coordination module. **Classes**: `IncidentType`, `IncidentScale`, `Incident`, `Agency`, `IncidentCommand`, `EmergencyCoordinator` ### evacuatio
n
.py Evacuation planning module. **Classes**: `EvacuationLevel`, `EvacuationZone`, `Shelter`, `EvacuationRoute`, `EvacuationPlanner` ### resource
s
.py Resource deployment module. **Classes**: `ResourceStatus`, `ResourceType`, `Resource`, `ResourceRequest`, `ResourceDeployer` ### sa
r
.py Search and rescue module. **Classes**: `SearchPattern`, `SubjectType`, `SearchSubject`, `SearchTeam`, `SearchArea`, `SearchAndRescue` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 