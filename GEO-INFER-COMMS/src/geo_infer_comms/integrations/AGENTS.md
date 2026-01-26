# Agent
: integrations ## Scope
 This directory contains integrations components for the module. It provides 5 classes and 0 functions. ## Classes
 and Functions ### EmailProvide
r
 Base class for email provider integrations. **Methods**: - `format_email_with_geospatial_context(subject: str, body: str, geospatial_context: Optional[GeospatialMetadata]) -> Dict[str, str]`: Format email content with geospatial context information. - `validate_email_address(email: str) -> bool`: Validate email address format. - `create_mime_message(to_email: str, subject: str, body: str, html_body: Optional[str]) -> MimeMultipart`: Create MIME message for email. - `get_provider_stats() -> Dict[str, Any]`: Get provider-specific statistics. ### SendGridProvide
r
 SendGrid email provider integration. ### SESProvide
r
 Amazon SES email provider integration. ### MailgunProvide
r
 Mailgun email provider integration. ### EmailProviderFactor
y
 Factory for creating email provider instances. **Methods**: - `create_provider(provider_type: str, config: Dict[str, Any]) -> EmailProvider`: Create an email provider instance. - `get_available_providers() -> List[str]`: Get list of available email provider types. ## Capabilities
 - **5 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-COMMS/src/geo_infer_comms/integrations` - **Type**: Directory Node 