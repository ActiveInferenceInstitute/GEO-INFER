"""
External integrations for GEO-INFER-COMMS.

This package currently exposes the implemented external email-provider
adapters. Other integration families require their own tracked modules before
they can become public exports.
"""

from geo_infer_comms.integrations.email_providers import (
    EmailDeliveryError,
    EmailErrorCategory,
    EmailProvider,
    EmailProviderFactory,
    MailgunProvider,
    SendGridProvider,
    SESProvider,
)

__all__ = [
    "EmailDeliveryError",
    "EmailErrorCategory",
    "EmailProvider",
    "EmailProviderFactory",
    "MailgunProvider",
    "SESProvider",
    "SendGridProvider",
]
