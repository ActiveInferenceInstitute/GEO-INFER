"""Tests for SecurityUtils token lifecycle: issue, validate, expire, tamper, context."""

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta

import pytest

from geo_infer_sec.utils.security_utils import SecurityConfig, SecurityUtils

pytestmark = [pytest.mark.unit]

SECRET_A = "lifecycle-test-secret-a"
SECRET_B = "lifecycle-test-secret-b"


def make_utils(secret: str) -> SecurityUtils:
    """Build a SecurityUtils pinned to a stable HMAC secret."""
    return SecurityUtils(SecurityConfig(token_secret=secret))


class TestTokenLifecycle:
    def test_round_trip(self):
        utils = make_utils(SECRET_A)
        token = utils.generate_secure_token("user-42")
        assert utils.validate_token(token) == "user-42"

    def test_tokens_are_unique(self):
        utils = make_utils(SECRET_A)
        assert (
            utils.generate_secure_token("user-42")
            != utils.generate_secure_token("user-42")
        )

    def test_expiry_rejected(self):
        utils = make_utils(SECRET_A)
        token = utils.generate_secure_token("user-42", expiration_hours=-1)
        assert utils.validate_token(token) is None

    def test_expired_payload_rejected_even_with_valid_signature(self):
        utils = make_utils(SECRET_A)
        # Forge a correctly-signed token whose exp is in the past.
        payload = {
            "user_id": "user-42",
            "exp": (datetime.now() - timedelta(hours=2)).isoformat(),
        }
        payload_bytes = json.dumps(payload, default=str).encode("utf-8")
        signature = hmac.new(utils._token_key, payload_bytes, hashlib.sha256).digest()
        token = (
            base64.urlsafe_b64encode(payload_bytes)
            + b"."
            + base64.urlsafe_b64encode(signature)
        ).decode("utf-8")
        assert utils.validate_token(token) is None

    def test_signature_tamper_rejected(self):
        utils = make_utils(SECRET_A)
        token = utils.generate_secure_token("user-42")
        p_b64, sig_b64 = token.split(".", 1)
        sig = bytearray(base64.urlsafe_b64decode(sig_b64))
        sig[0] ^= 0xFF
        tampered = p_b64 + "." + base64.urlsafe_b64encode(bytes(sig)).decode("utf-8")
        assert utils.validate_token(tampered) is None

    def test_payload_tamper_rejected(self):
        utils = make_utils(SECRET_A)
        token = utils.generate_secure_token("user-42")
        p_b64, sig_b64 = token.split(".", 1)
        payload = base64.urlsafe_b64decode(p_b64)
        tampered_payload = payload.replace(b"user-42", b"user-99")
        assert tampered_payload != payload
        tampered = (
            base64.urlsafe_b64encode(tampered_payload).decode("utf-8")
            + "."
            + sig_b64
        )
        assert utils.validate_token(tampered) is None

    def test_wrong_context_rejected(self):
        """A token minted under one signing secret is invalid elsewhere."""
        issuer = make_utils(SECRET_A)
        verifier = make_utils(SECRET_B)
        token = issuer.generate_secure_token("user-42")
        assert verifier.validate_token(token) is None

    def test_malformed_token_rejected(self):
        utils = make_utils(SECRET_A)
        assert utils.validate_token("not-a-token") is None
        assert utils.validate_token("") is None
        assert utils.validate_token("a.b.c") is None
