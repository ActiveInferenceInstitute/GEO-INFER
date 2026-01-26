# Agent
: models ## Scope
 This directory contains models components for the module. It provides 18 classes and 1 functions. ## Classes
 and Functions ### RiskSeverit
y
 Severity levels for security risks. ### RiskLikelihoo
d
 Likelihood levels for security risks. ### RiskCategor
y
 Categories of geospatial security risks. ### GeospatialSecurityRis
k
 Model representing a security risk in a geospatial context. **Methods**: - `calculate_risk_score() -> int`: Calculate a numerical risk score. - `to_dict() -> Dict`: Convert the risk to a dictionary. - `from_dict(cls, data: Dict) -> 'GeospatialSecurityRisk'`: Create a risk from a dictionary. ### RiskAssessmen
t
 Assessment of multiple security risks for a geospatial system. **Methods**: - `add_risk(risk: GeospatialSecurityRisk) -> None`: Add a risk to the assessment. - `remove_risk(risk_name: str) -> bool`: Remove a risk from the assessment. - `get_risk_by_name(risk_name: str) -> Optional[GeospatialSecurityRisk]`: Get a risk by its name. - `get_risks_by_category(category: RiskCategory) -> List[GeospatialSecurityRisk]`: Get all risks in a specific category. - `get_risks_by_severity(severity: RiskSeverity) -> List[GeospatialSecurityRisk]`: Get all risks with a specific severity. - `get_risks_by_likelihood(likelihood: RiskLikelihood) -> List[GeospatialSecurityRisk]`: Get all risks with a specific likelihood. - `calculate_total_risk_score() -> int`: Calculate the total risk score for the assessment. - `get_highest_risks(count: int) -> List[GeospatialSecurityRisk]`: Get the highest-scoring risks. - `to_dict() -> Dict`: Convert the assessment to a dictionary. - `from_dict(cls, data: Dict) -> 'RiskAssessment'`: Create an assessment from a dictionary. - `to_json(indent: int) -> str`: Convert the assessment to a JSON string. - `from_json(cls, json_str: str) -> 'RiskAssessment'`: Create an assessment from a JSON string. - `generate_risk_matrix() -> pd.DataFrame`: Generate a risk matrix showing the distribution of risks. - `generate_risk_report(format: str) -> str`: Generate a risk assessment report. ### ThreatLeve
l
 Standardized threat severity levels. ### SecurityEventCategor
y
 Categories of security events. ### SecurityEven
t
 Base security event model. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert event to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> 'SecurityEvent'`: Create event from dictionary. ### SecurityAler
t
 Security alert model. **Methods**: - `update_status(new_status: str, notes: str)`: Update alert status. ### ThreatIntelligenc
e
 Threat intelligence indicator model. ### SecurityAsse
t
 Security asset model. ### SecurityPolic
y
 Security policy model. ### SecurityComplianc
e
 Security compliance model. ### SecurityMetric
s
 Security metrics model. ### RiskAssessmen
t
 Risk assessment model. ### SecurityIncidentWorkflo
w
 Security incident workflow model. ### SecurityConfiguratio
n
 Security configuration model. ### SecurityModelUtil
s
 Utility functions for security models. **Methods**: - `serialize_event(event: SecurityEvent) -> str`: Serialize security event to JSON string. - `deserialize_event(json_str: str) -> SecurityEvent`: Deserialize security event from JSON string. - `calculate_risk_score(impact: float, likelihood: float, control_effectiveness: float) -> float`: Calculate risk score with controls. - `get_risk_level(risk_score: float) -> ThreatLevel`: Convert risk score to threat level. - `merge_metadata(base_metadata: Dict[str, Any], additional_metadata: Dict[str, Any]) -> Dict[str, Any]`: Safely merge metadata dictionaries. - `filter_events_by_timeframe(events: List[SecurityEvent], start_time: datetime, end_time: datetime) -> List[SecurityEvent]`: Filter events by time frame. - `group_events_by_category(events: List[SecurityEvent]) -> Dict[str, List[SecurityEvent]]`: Group events by category. - `calculate_confidence_score(indicators: List[str], evidence_strength: Dict[str, float]) -> float`: Calculate confidence score based on indicators and evidence. - `generate_event_signature(event: SecurityEvent) -> str`: Generate a unique signature for an event. ### create_common_geospatial_risk
s
 `create_common_geospatial_risks() -> List[GeospatialSecurityRisk]` Create a list of common geospatial security risks. ## Capabilities
 - **18 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SEC/src/geo_infer_sec/models` - **Type**: Directory Node 