from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_system_info(sender, **kwargs):
    from .models import SystemInfo
    SystemInfo.get_instance()


class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "system"

    def ready(self):
        post_migrate.connect(create_system_info, sender=self)