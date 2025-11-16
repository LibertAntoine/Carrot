import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django_resized import ResizedImageField
from simple_history.models import HistoricalRecords
from users.models import User


def generate_thumbnail_path(instance, filename, uuid_value=None):
    """Generate path for thumbnail"""
    ext = filename.split('.')[-1]
    unique_id = uuid_value or uuid.uuid4().hex
    base_key = get_thumbnail_base_key(instance)
    return f"{base_key}{unique_id}.{ext}"


def get_thumbnail_base_key(instance):
    """Get the base key for thumbnails of an action."""
    return f"v1/actions/{instance.id}/thumbnails/"


class Action(models.Model):
    """Action model"""

    PYTHON = "Python"
    TYPE_CHOICES = [(PYTHON, "Python")]

    THUMBNAIL_RESOLUTION = (80, 80)
    THUMBNAIL_FORMAT = "PNG"
    history = HistoricalRecords(m2m_fields=["users", "groups", "roles"])
    name = models.CharField(
        max_length=25,
        unique=True,
        validators=[MinLengthValidator(3)],
    )
    description = models.TextField(
        max_length=500,
        blank=True,
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Is the action active?",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Is the action public?",
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    create_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="actions_created",
        blank=True,
        null=True,
    )
    last_update = models.DateTimeField(auto_now=True)
    thumbnail = ResizedImageField(
        size=THUMBNAIL_RESOLUTION,
        force_format=THUMBNAIL_FORMAT,
        upload_to=generate_thumbnail_path,
        blank=True,
        null=True,
    )
    users = models.ManyToManyField(
        User,
        related_name="actions",
        blank=True,
    )
    groups = models.ManyToManyField(
        "users.Group",
        related_name="actions",
        blank=True,
    )
    roles = models.ManyToManyField(
        "users.Role",
        related_name="actions",
        blank=True,
    )
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.SET_NULL,
        related_name="actions",
        blank=True,
        null=True,
    )
    section = models.CharField(
        max_length=100,
        blank=True,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    data = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
