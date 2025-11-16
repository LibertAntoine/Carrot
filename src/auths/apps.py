import smtplib
import ssl
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("django")


class AuthsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auths"
    email_config_valid = False

    def ready(self):
        if not getattr(settings, "PASSWORD_BASED_AUTHENTICATION", False):
            return

        self.email_config_valid = check_smtp_config(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            use_tls=getattr(settings, "EMAIL_USE_TLS", False),
            use_ssl=getattr(settings, "EMAIL_USE_SSL", False),
            username=getattr(settings, "EMAIL_HOST_USER", None),
            password=getattr(settings, "EMAIL_HOST_PASSWORD", None),
        )


def check_smtp_config(
    host: str,
    port: int,
    use_tls: bool = False,
    use_ssl: bool = False,
    username: str | None = None,
    password: str | None = None,
    timeout: int = 5,
) -> bool:
    """Check if the SMTP configuration is valid by attempting to connect and authenticate."""

    if not host:
        logger.warning("SMTP configuration invalid: EMAIL_HOST not defined.")
        return False

    try:
        if use_ssl:
            smtp = smtplib.SMTP_SSL(
                host=host,
                port=port,
                timeout=timeout,
                context=ssl.create_default_context(),
            )
        else:
            smtp = smtplib.SMTP(host=host, port=port, timeout=timeout)

        if use_tls and not use_ssl:
            smtp.starttls(context=ssl.create_default_context())

        if username and password:
            smtp.login(username, password)

        code, message = smtp.noop()
        smtp.quit()

        if code == 250:
            logger.info("SMTP configuration valid")
            return True
        else:
            logger.warning("SMTP configuration invalid: %s %s", code, message)
            return False

    except Exception as e:
        logger.warning("SMTP configuration invalid: %s", e)
        return False
