from django.db import models
from users.models import User


class Workspace(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="workspaces_created",
        blank=True,
        null=True,
    )
    users = models.ManyToManyField(
        User,
        related_name="workspaces",
        blank=True,
    )
    groups = models.ManyToManyField(
        "users.Group",
        related_name="workspaces",
        blank=True,
    )
    roles = models.ManyToManyField(
        "users.Role",
        related_name="workspaces",
        blank=True,
    )
