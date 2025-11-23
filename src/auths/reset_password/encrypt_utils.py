import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

OTP_LENGTH = 6
OTP_EXPIRATION_MINUTES = 15
HMAC_KEY = getattr(settings, "SECRET_KEY", secrets.token_bytes(32)).encode()


def generate_otp(length=OTP_LENGTH):
    """Generate a numeric OTP of given length."""
    range_start = 10 ** (length - 1)
    range_end = (10**length) - 1
    return str(secrets.randbelow(range_end - range_start + 1) + range_start)


def otp_expiration_dt(minutes=OTP_EXPIRATION_MINUTES):
    """Return OTP expiration datetime."""
    return timezone.now() + timedelta(minutes=minutes)


def hash_token(token: str) -> str:
    """Return HMAC-SHA256 hash of the token."""
    return hmac.new(HMAC_KEY, token.encode(), hashlib.sha256).hexdigest()


def is_same_hash(hash1: str, hash2: str) -> bool:
    """Compare OTP with its hash securely."""
    return hmac.compare_digest(hash1, hash2)


def get_reset_token_key():
    """Generate a secure reset token key."""
    return secrets.token_urlsafe(32)
