# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 0 classes and 25 functions. ## Classes
 and Functions ### validate_coordinate
s
 `validate_coordinates(longitude: float, latitude: float) -> bool` Validate longitude and latitude coordinates. ### validate_cr
s
 `validate_crs(crs: str) -> bool` Validate coordinate reference system string. ### validate_emai
l
 `validate_email(email: str) -> bool` Validate email address format. ### validate_phon
e
 `validate_phone(phone: str) -> bool` Validate phone number format. ### validate_message_conten
t
 `validate_message_content(content: str, max_length: int) -> bool` Validate message content. ### validate_message_priorit
y
 `validate_message_priority(priority: str) -> bool` Validate message priority level. ### validate_message_typ
e
 `validate_message_type(message_type: str) -> bool` Validate message type. ### validate_user_i
d
 `validate_user_id(user_id: str) -> bool` Validate user identifier format. ### validate_channel_i
d
 `validate_channel_id(channel_id: str) -> bool` Validate channel identifier format. ### validate_spatial_bound
s
 `validate_spatial_bounds(bounds: Dict[str, Any]) -> bool` Validate spatial bounds structure. ### validate_geojson_featur
e
 `validate_geojson_feature(feature: Dict[str, Any]) -> bool` Validate GeoJSON Feature structure. ### validate_geojson_geometr
y
 `validate_geojson_geometry(geometry: Dict[str, Any]) -> bool` Validate GeoJSON Geometry structure. ### validate_notification_typ
e
 `validate_notification_type(notification_type: str) -> bool` Validate notification type. ### validate_delivery_method
s
 `validate_delivery_methods(methods: List[str]) -> bool` Validate notification delivery methods. ### validate_event_typ
e
 `validate_event_type(event_type: str) -> bool` Validate event type. ### validate_timestam
p
 `validate_timestamp(timestamp: Union[str, datetime]) -> bool` Validate timestamp format and value. ### validate_ur
l
 `validate_url(url: str) -> bool` Validate URL format. ### validate_file_siz
e
 `validate_file_size(size_bytes: int, max_size_mb: float) -> bool` Validate file size. ### validate_message_recipient
s
 `validate_message_recipients(recipients: List[str]) -> bool` Validate list of message recipients. ### validate_spatial_filte
r
 `validate_spatial_filter(filter_config: Dict[str, Any]) -> bool` Validate spatial filter configuration. ### validate_collaboration_sessio
n
 `validate_collaboration_session(session_config: Dict[str, Any]) -> bool` Validate collaboration session configuration. ### validate_stream_confi
g
 `validate_stream_config(stream_config: Dict[str, Any]) -> bool` Validate data stream configuration. ### sanitize_message_conten
t
 `sanitize_message_content(content: str) -> str` Sanitize message content to prevent XSS and other issues. ### validate_and_sanitize_input
s
 `validate_and_sanitize_inputs(**kwargs) -> Dict[str, Any]` Validate and sanitize multiple input parameters. ### validate_configuratio
n
 `validate_configuration(config: Dict[str, Any], required_keys: List[str]) -> bool` Validate configuration dictionary against required keys. ## Capabilities
 - **25 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-COMMS/src/geo_infer_comms/utils` - **Type**: Directory Node 