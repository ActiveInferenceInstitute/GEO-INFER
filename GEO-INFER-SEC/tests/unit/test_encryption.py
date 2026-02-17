"""Tests for the encryption module."""
import pytest

from geo_infer_sec.core.encryption import (
    GeospatialEncryption,
    AsymmetricEncryption,
)


class TestGeospatialEncryption:
    def test_init(self):
        enc = GeospatialEncryption()
        assert enc is not None

    def test_encrypt_decrypt_coordinates(self):
        enc = GeospatialEncryption()
        lat, lon = 37.7749, -122.4194
        encrypted = enc.encrypt_coordinates(lat, lon)
        assert encrypted != f"{lat},{lon}"
        dec_lat, dec_lon = enc.decrypt_coordinates(encrypted)
        assert abs(dec_lat - lat) < 0.0001
        assert abs(dec_lon - lon) < 0.0001

    def test_encrypt_coordinates_different_values(self):
        enc = GeospatialEncryption()
        enc1 = enc.encrypt_coordinates(10.0, 20.0)
        enc2 = enc.encrypt_coordinates(30.0, 40.0)
        assert enc1 != enc2

    def test_different_keys_produce_different_outputs(self):
        """Two GeospatialEncryption instances with different auto-generated keys
        produce different ciphertexts for the same coordinates."""
        enc1 = GeospatialEncryption()
        enc2 = GeospatialEncryption()
        # Each generates its own Fernet key, so they should differ
        assert enc1.key != enc2.key
        result1 = enc1.encrypt_coordinates(37.0, -122.0)
        result2 = enc2.encrypt_coordinates(37.0, -122.0)
        assert result1 != result2


class TestAsymmetricEncryption:
    def test_generate_keys_creates_keypair(self):
        enc = AsymmetricEncryption.generate_keys()
        assert enc.private_key is not None
        assert enc.public_key is not None

    def test_encrypt_decrypt(self):
        enc = AsymmetricEncryption.generate_keys()
        plaintext = b"Secret geospatial data"
        ciphertext = enc.encrypt(plaintext)
        assert ciphertext != plaintext
        decrypted = enc.decrypt(ciphertext)
        assert decrypted == plaintext

    def test_encrypt_empty_data(self):
        enc = AsymmetricEncryption.generate_keys()
        ciphertext = enc.encrypt(b"")
        decrypted = enc.decrypt(ciphertext)
        assert decrypted == b""

    def test_export_public_key(self):
        enc = AsymmetricEncryption.generate_keys()
        pub_pem = enc.export_public_key()
        assert b"BEGIN PUBLIC KEY" in pub_pem

    def test_default_init_has_no_keys(self):
        """Default constructor leaves keys as None (use generate_keys classmethod)."""
        enc = AsymmetricEncryption()
        assert enc.private_key is None
        assert enc.public_key is None
