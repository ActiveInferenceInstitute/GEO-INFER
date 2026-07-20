"""
Email provider integrations for GEO-INFER-COMMS.

This module provides comprehensive email delivery integrations with
major email service providers including SendGrid, AWS SES, Mailgun,
and others for reliable email notifications and communications.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional, Any
import requests

from geo_infer_comms.models.spatial import GeospatialMetadata


class EmailProvider(ABC):
    """
    Base class for email provider integrations.

    Provides common functionality for email delivery with geospatial
    context support and comprehensive error handling.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get("provider", "generic")
        self.api_key = config.get("api_key")
        self.from_email = config.get("from_email", "noreply@geo-infer.org")
        self.from_name = config.get("from_name", "GEO-INFER Communications")

        # Rate limiting and retry configuration
        self.rate_limit_per_minute = config.get("rate_limit_per_minute", 1000)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay_seconds = config.get("retry_delay_seconds", 1.0)

        # Performance tracking
        self.emails_sent = 0
        self.emails_failed = 0
        self.last_send_time: Optional[float] = None

        self.logger = logging.getLogger(__name__)

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        geospatial_context: Optional[GeospatialMetadata] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send an email with optional geospatial context.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            geospatial_context: Optional geospatial context
            attachments: Optional email attachments

        Returns:
            True if email sent successfully
        """
        raise RuntimeError("Email provider subclasses must implement send_email")

    def format_email_with_geospatial_context(
        self,
        subject: str,
        body: str,
        geospatial_context: Optional[GeospatialMetadata] = None,
    ) -> Dict[str, str]:
        """
        Format email content with geospatial context information.

        Args:
            subject: Base email subject
            body: Base email body
            geospatial_context: Geospatial context to include

        Returns:
            Formatted email content
        """
        # Enhance subject with geospatial context if available
        enhanced_subject = subject
        if geospatial_context:
            location = geospatial_context.location
            enhanced_subject = f"[Location: {location.latitude:.4f}, {location.longitude:.4f}] {subject}"

        # Enhance body with geospatial details
        enhanced_body = body
        if geospatial_context:
            location_info = f"""
Geospatial Context:
- Location: {geospatial_context.location.latitude:.6f}, {geospatial_context.location.longitude:.6f}
- Accuracy: {geospatial_context.accuracy or 'Unknown'} meters
- Source: {geospatial_context.source or 'Unknown'}
- Timestamp: {geospatial_context.timestamp.isoformat()}
"""
            enhanced_body += location_info

        return {"subject": enhanced_subject, "body": enhanced_body}

    def validate_email_address(self, email: str) -> bool:
        """Validate email address format."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def create_mime_message(
        self, to_email: str, subject: str, body: str, html_body: Optional[str] = None
    ) -> MimeMultipart:
        """Create MIME message for email."""
        msg = MimeMultipart("alternative")

        # Add text part
        text_part = MimeText(body, "plain")
        msg.attach(text_part)

        # Add HTML part if provided
        if html_body:
            html_part = MimeText(html_body, "html")
            msg.attach(html_part)

        # Set headers
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        return msg

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get provider-specific statistics."""
        return {
            "provider": self.provider_name,
            "emails_sent": self.emails_sent,
            "emails_failed": self.emails_failed,
            "success_rate": (
                self.emails_sent / max(self.emails_sent + self.emails_failed, 1) * 100
            ),
        }


class SendGridProvider(EmailProvider):
    """SendGrid email provider integration."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        geospatial_context: Optional[GeospatialMetadata] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send email via SendGrid API."""
        try:
            # Validate email
            if not self.validate_email_address(to_email):
                self.logger.error(f"Invalid email address: {to_email}")
                return False

            # Format content with geospatial context
            formatted = self.format_email_with_geospatial_context(
                subject, body, geospatial_context
            )

            # Create SendGrid payload
            payload = {
                "personalizations": [
                    {"to": [{"email": to_email}], "subject": formatted["subject"]}
                ],
                "from": {"email": self.from_email, "name": self.from_name},
                "content": [{"type": "text/plain", "value": formatted["body"]}],
            }

            if not self.api_key:
                raise ValueError("SendGrid api_key is required")
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            self.logger.info(
                "SendGrid email sent to %s: %s", to_email, formatted["subject"]
            )
            self.emails_sent += 1

            return True

        except Exception as e:
            self.logger.error(f"SendGrid email failed: {e}")
            self.emails_failed += 1
            return False


class SESProvider(EmailProvider):
    """Amazon SES email provider integration."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.aws_region = config.get("aws_region", "us-east-1")
        self.aws_access_key = config.get("aws_access_key")
        self.aws_secret_key = config.get("aws_secret_key")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        geospatial_context: Optional[GeospatialMetadata] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send email via Amazon SES."""
        try:
            # Validate email
            if not self.validate_email_address(to_email):
                self.logger.error(f"Invalid email address: {to_email}")
                return False

            # Format content with geospatial context
            formatted = self.format_email_with_geospatial_context(
                subject, body, geospatial_context
            )

            if not self.aws_access_key or not self.aws_secret_key:
                raise ValueError("AWS credentials are required for SES")
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("boto3 is required for SES delivery") from exc
            client = boto3.client(
                "ses",
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
            )
            await asyncio.to_thread(
                client.send_email,
                Source=self.from_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": formatted["subject"]},
                    "Body": {"Text": {"Data": formatted["body"]}},
                },
            )
            self.logger.info("SES email sent to %s: %s", to_email, formatted["subject"])
            self.emails_sent += 1

            return True

        except Exception as e:
            self.logger.error(f"SES email failed: {e}")
            self.emails_failed += 1
            return False


class MailgunProvider(EmailProvider):
    """Mailgun email provider integration."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = f"https://api.mailgun.net/v3/{config.get('domain', 'geo-infer.org')}/messages"
        self.api_username = "api"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        geospatial_context: Optional[GeospatialMetadata] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send email via Mailgun API."""
        try:
            # Validate email
            if not self.validate_email_address(to_email):
                self.logger.error(f"Invalid email address: {to_email}")
                return False

            # Format content with geospatial context
            formatted = self.format_email_with_geospatial_context(
                subject, body, geospatial_context
            )

            if not self.api_key:
                raise ValueError("Mailgun api_key is required")
            response = await asyncio.to_thread(
                requests.post,
                self.api_url,
                auth=(self.api_username, self.api_key),
                data={
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": [to_email],
                    "subject": formatted["subject"],
                    "text": formatted["body"],
                },
                timeout=30,
            )
            response.raise_for_status()
            self.logger.info(
                "Mailgun email sent to %s: %s", to_email, formatted["subject"]
            )
            self.emails_sent += 1

            return True

        except Exception as e:
            self.logger.error(f"Mailgun email failed: {e}")
            self.emails_failed += 1
            return False


class EmailProviderFactory:
    """Factory for creating email provider instances."""

    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> EmailProvider:
        """
        Create an email provider instance.

        Args:
            provider_type: Type of email provider ("sendgrid", "ses", "mailgun")
            config: Provider configuration

        Returns:
            Email provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        providers = {
            "sendgrid": SendGridProvider,
            "ses": SESProvider,
            "mailgun": MailgunProvider,
        }

        provider_class = providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unsupported email provider: {provider_type}")

        return provider_class(config)

    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available email provider types."""
        return ["sendgrid", "ses", "mailgun"]
