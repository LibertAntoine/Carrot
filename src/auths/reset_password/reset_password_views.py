from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from users.models import User
from .password_reset_request_model import PasswordResetRequest
from .encrypt_utils import (
    generate_otp,
    hash_token,
    otp_expiration_dt,
)
from .email_utils import (
    send_password_reset_otp_email,
    send_password_reset_confirm_email,
)


class RequestResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


@api_view(["POST"])
def request_reset_password(request):
    """Init user password reset by sending an OTP by email."""
    serializer = RequestResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]

    user = User.objects.filter(email=email).first()
    oidc_enabled = getattr(settings, "OIDC_ENABLED", False)
    if user and (not user.scim_external_id or not oidc_enabled):
        PasswordResetRequest.objects.filter(user=user).delete()
        otp = generate_otp()
        ip_address = get_client_ip(request)
        PasswordResetRequest.objects.create(
            user=user,
            otp_hash=hash_token(otp),
            expires_at=otp_expiration_dt(),
            request_ip=ip_address,
        )
        send_password_reset_otp_email(user.email, user.username, otp, ip_address)
    return Response(
        {"detail": "If the email is registered, a password reset code has been sent."},
        status=status.HTTP_200_OK,
    )


class VerifyResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


@api_view(["POST"])
def verify_reset_password_otp(request):
    """Confirm reset password otp and return a reset token to confirm password reset."""
    serializer = VerifyResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    otp = serializer.validated_data["otp"]

    reset_request = get_user_reset_request(email)
    if not reset_request or not reset_request.is_otp_valid(otp):
        return Response(
            {"detail": "Invalid email or otp, or the otp has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    reset_token = reset_request.set_reset_token()
    return Response({"token": reset_token}, status=status.HTTP_200_OK)


class ConfirmResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField()

@api_view(["POST"])
def confirm_reset_password(request):
    """Confirm reset password with token and set new password."""
    serializer = ConfirmResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    token = serializer.validated_data["token"]
    new_password = serializer.validated_data["new_password"]

    reset_request = get_user_reset_request(email)
    if not reset_request.is_token_valid(token):
        return Response(
            {"detail": "Invalid email or code."}, status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    validate_password(new_password, user)
    user.set_password(new_password)
    user.save()
    send_password_reset_confirm_email(user.email, user.username, get_client_ip(request))
    return Response({"detail": "Password has been reset."}, status=status.HTTP_200_OK)


def get_user_reset_request(email):
    """Get user OTP record."""
    user = User.objects.filter(email=email).first()
    if not user:
        return None
    return PasswordResetRequest.objects.filter(user=user).first()


def get_client_ip(request):
    """Get client IP address from request."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
