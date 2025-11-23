from django.conf import settings
from django.db import models
from django.utils import timezone

from auths.reset_password.encrypt_utils import (
    get_reset_token_key,
    hash_token,
    is_same_hash,
)


class PasswordResetRequest(models.Model):
    MAX_ATTEMPTS = 5

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_code",
    )
    otp_hash = models.CharField(max_length=128)
    is_otp_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return (
            f"{self.user.email} - expires at {self.expires_at:%Y-%m-%d %H:%M}"
        )

    def is_otp_valid(self, otp: str) -> bool:
        """Check if the provided OTP is valid."""
        if self.expires_at < timezone.now():
            self.delete()
            return False

        if (
            not self.otp_hash
            or self.is_otp_used
            or not is_same_hash(self.otp_hash, hash_token(otp))
        ):
            self.attempts += 1
            if self.attempts >= PasswordResetRequest.MAX_ATTEMPTS:
                self.delete()
            else:
                self.save(update_fields=["attempts"])
            return False
        self.is_otp_used = True
        self.save(update_fields=["is_otp_used"])
        return True

    def is_token_valid(self, token: str) -> bool:
        """Check if the provided reset token is valid."""
        if self.expires_at < timezone.now():
            self.delete()
            return False

        if not self.reset_token or not is_same_hash(
            self.reset_token, hash_token(token)
        ):
            self.attempts += 1
            if self.attempts >= PasswordResetRequest.MAX_ATTEMPTS:
                self.delete()
            else:
                self.save(update_fields=["attempts"])
            return False
        return True

    def set_reset_token(self) -> str:
        """Generate and set a reset token."""
        token = get_reset_token_key()
        self.reset_token = hash_token(token)
        self.save(update_fields=["reset_token"])
        return token
