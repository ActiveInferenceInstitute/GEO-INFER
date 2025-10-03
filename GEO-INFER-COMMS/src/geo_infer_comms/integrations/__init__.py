"""
External integrations for GEO-INFER-COMMS.

This module provides comprehensive integration adapters for external services
including email providers, SMS gateways, push notification services, and
geospatial data sources for seamless communication capabilities.
"""

from geo_infer_comms.integrations.email_providers import (
    EmailProvider, SendGridProvider, SESProvider, MailgunProvider
)
from geo_infer_comms.integrations.sms_providers import (
    SMSProvider, TwilioProvider, AWS_SNS_Provider
)
from geo_infer_comms.integrations.push_providers import (
    PushProvider, FirebaseProvider, APNsProvider, OneSignalProvider
)
from geo_infer_comms.integrations.geospatial_sources import (
    GeospatialDataSource, OpenStreetMapProvider, GoogleMapsProvider,
    HERE_Maps_Provider, MapboxProvider
)
from geo_infer_comms.integrations.iot_protocols import (
    IoTProtocol, MQTT_Protocol, CoAP_Protocol, LoRaWAN_Protocol
)
from geo_infer_comms.integrations.webhook_manager import (
    WebhookManager, WebhookDeliveryTracker
)

__all__ = [
    "EmailProvider", "SendGridProvider", "SESProvider", "MailgunProvider",
    "SMSProvider", "TwilioProvider", "AWS_SNS_Provider",
    "PushProvider", "FirebaseProvider", "APNsProvider", "OneSignalProvider",
    "GeospatialDataSource", "OpenStreetMapProvider", "GoogleMapsProvider",
    "HERE_Maps_Provider", "MapboxProvider",
    "IoTProtocol", "MQTT_Protocol", "CoAP_Protocol", "LoRaWAN_Protocol",
    "WebhookManager", "WebhookDeliveryTracker"
]
