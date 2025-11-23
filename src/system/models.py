import uuid

from django.conf import settings
from django.db import models
from django_resized import ResizedImageField


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


def generate_default_background_path(instance, filename, uuid_value=None):
    """Generate path for thumbnail"""
    ext = filename.split(".")[-1]
    unique_id = uuid_value or uuid.uuid4().hex
    base_key = get_default_background_base_key()
    return f"{base_key}{unique_id}.{ext}"


def get_default_background_base_key():
    """Get the base key for thumbnails of an action."""
    return "v1/system-info/default-background/"


class SystemInfo(SingletonModel):
    allow_action_workspaces = models.BooleanField(default=False)

    allow_background_image = models.BooleanField(default=False)
    default_background_image = ResizedImageField(
        size=settings.GALLERY_BACKGROUND_IMAGE_RESOLUTION,
        crop=["middle", "center"],
        force_format=settings.GALLERY_BACKGROUND_IMAGE_FORMAT,
        upload_to=generate_default_background_path,
        blank=True,
        null=True,
    )
    allow_user_custom_background_image = models.BooleanField(default=False)

    allow_action_sections = models.BooleanField(default=False)
    allow_users_to_hide_actions = models.BooleanField(default=False)
