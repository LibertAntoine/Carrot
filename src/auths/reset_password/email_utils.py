import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger("django")


def send_password_reset_otp_email(email: str, username: str, otp: str, ip_address: str):
    """
    Send a password reset OTP email to the user.

    Arguments:
        email: recipient email
        username: user name (for personalization)
        otp: the one-time password code
        ip_address: IP address from which the reset was requested
    """

    context = {
        "username": username,
        "otp": otp,
        "ip_address": ip_address,
        "app_name": "Jumper",
    }

    # Render HTML and plaintext versions
    email_html_message = render_to_string("user_reset_password_otp_email.html", context)
    email_plaintext_message = render_to_string(
        "user_reset_password_otp_email.txt", context
    )

    # Create the email
    subject = f"[{context['app_name']}] Password Reset Request"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    msg = EmailMultiAlternatives(
        subject=subject,
        body=email_plaintext_message,
        from_email=from_email,
        to=recipient_list,
    )
    # Attach HTML alternative
    msg.attach_alternative(email_html_message, "text/html")

    # Send and log
    try:
        msg.send(fail_silently=False)
        logger.info("Password reset OTP sent to %s from IP %s", email, ip_address)
    except Exception as e:
        logger.error(
            "Failed to send password reset OTP to %s from IP %s: %s",
            email,
            ip_address,
            e,
        )
        raise


def send_password_reset_confirm_email(email: str, username: str, ip_address: str):
    """
    Send a confirmation email after a successful password reset.

    Arguments:
        email: recipient email
        username: user name
        ip_address: IP address from which the reset was performed
    """

    context = {
        "username": username,
        "ip_address": ip_address,
        "app_name": "Jumper",
    }

    # Render HTML and plaintext versions
    email_html_message = render_to_string(
        "user_password_reset_confirm_email.html", context
    )
    email_plaintext_message = render_to_string(
        "user_password_reset_confirm_email.txt", context
    )

    # Create the email
    subject = f"[{context['app_name']}] Password Successfully Reset"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    msg = EmailMultiAlternatives(
        subject=subject,
        body=email_plaintext_message,
        from_email=from_email,
        to=recipient_list,
    )
    # Attach HTML alternative
    msg.attach_alternative(email_html_message, "text/html")

    # Send and log
    try:
        msg.send(fail_silently=False)
        logger.info(
            "Password reset confirmation sent to %s from IP %s", email, ip_address
        )
    except Exception as e:
        logger.error(
            "Failed to send password reset confirmation to %s from IP %s: %s",
            email,
            ip_address,
            e,
        )
        raise
