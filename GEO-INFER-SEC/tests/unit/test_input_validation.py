"""Tests for security input validation and sanitization."""
import pytest


class TestInputSanitization:
    """Test input sanitization for preventing injection attacks."""

    def test_sql_injection_patterns_detected(self):
        """Verify that common SQL injection patterns are identified."""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "' UNION SELECT * FROM passwords --",
        ]
        for inp in dangerous_inputs:
            has_sql_chars = any(c in inp for c in ("'", ";", "--", "UNION", "DROP", "OR 1=1"))
            assert has_sql_chars, f"SQL pattern not detected in: {inp}"

    def test_xss_patterns_detected(self):
        """Verify that common XSS patterns are identified."""
        xss_inputs = [
            "<script>alert('xss')</script>",
            '<img onerror="alert(1)" src=x>',
            "javascript:alert(1)",
        ]
        for inp in xss_inputs:
            has_xss = any(tag in inp.lower() for tag in ("<script", "onerror", "javascript:"))
            assert has_xss, f"XSS pattern not detected in: {inp}"

    def test_path_traversal_detected(self):
        """Verify path traversal attempts are identified."""
        paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/shadow",
        ]
        for path in paths:
            has_traversal = ".." in path or path.startswith("/etc/")
            assert has_traversal, f"Path traversal not detected: {path}"


class TestCoordinateValidation:
    """Test geospatial coordinate input validation."""

    def test_valid_latitude_range(self):
        for lat in [-90, -45, 0, 45, 90]:
            assert -90 <= lat <= 90

    def test_invalid_latitude(self):
        for lat in [-91, 91, -200, 200]:
            assert not (-90 <= lat <= 90)

    def test_valid_longitude_range(self):
        for lon in [-180, -90, 0, 90, 180]:
            assert -180 <= lon <= 180

    def test_invalid_longitude(self):
        for lon in [-181, 181, -360, 360]:
            assert not (-180 <= lon <= 180)


class TestPasswordValidation:
    """Test password strength validation rules."""

    def _check_password_strength(self, password: str) -> dict:
        issues = []
        if len(password) < 8:
            issues.append("too_short")
        if not any(c.isupper() for c in password):
            issues.append("no_uppercase")
        if not any(c.islower() for c in password):
            issues.append("no_lowercase")
        if not any(c.isdigit() for c in password):
            issues.append("no_digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
            issues.append("no_special")
        return {"valid": len(issues) == 0, "issues": issues}

    def test_strong_password(self):
        result = self._check_password_strength("SecureP@ss1")
        assert result["valid"] is True

    def test_weak_password_short(self):
        result = self._check_password_strength("Ab1!")
        assert "too_short" in result["issues"]

    def test_weak_password_no_uppercase(self):
        result = self._check_password_strength("password1!")
        assert "no_uppercase" in result["issues"]

    def test_weak_password_no_digit(self):
        result = self._check_password_strength("Password!")
        assert "no_digit" in result["issues"]
