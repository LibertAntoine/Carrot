import uuid
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django_group_model.models import AbstractGroup
from django.core.validators import MinLengthValidator
from django.core.exceptions import PermissionDenied
from django_resized import ResizedImageField
from django.conf import settings
from django_scim.models import AbstractSCIMGroupMixin, AbstractSCIMUserMixin
from jumper.storage_utils.file_field import FileFieldPathFactory


class Group(AbstractSCIMGroupMixin, AbstractGroup):
    pass


def generate_profile_picture_path(self, filename):
    """Generate the upload path for the thumbnail"""
    return f"users/profile_pictures/{str(uuid.uuid4())}.${self.PROFILE_FORMAT.lower()}"


class User(AbstractSCIMUserMixin, AbstractUser):
    """Custom user model.

    This model is used to extend the default user model.
    """

    class SystemRole(models.TextChoices):
        ADMIN = "admin", "Admin"
        ACTION_MANAGER = "action_manager", "Action Manager"
        USER_MANAGER = "user_manager", "User Manager"
        USER = "user", "User"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    PROFILE_RESOLUTION = (300, 300)
    PROFILE_FORMAT = "PNG"

    username = models.CharField(
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(4)],
    )
    system_role = models.CharField(
        max_length=20,
        choices=SystemRole.choices,
        default=SystemRole.USER,
    )
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        "users.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="user_set",
        related_query_name="user_set",
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    profile_picture = ResizedImageField(
        size=PROFILE_RESOLUTION,
        crop=["middle", "center"],
        force_format=PROFILE_FORMAT,
        upload_to=generate_profile_picture_path,
        blank=True,
        null=True,
    )

    @property
    def scim_groups(self):
        return self.groups.all() if settings.SCIM_ENABLED else Group.objects.none()

    @property
    def is_superuser_group_member(self):
        if settings.ADMIN_GROUP and settings.SCIM_ENABLED:
            superadmin_group = Group.objects.filter(name=settings.ADMIN_GROUP).first()
            if superadmin_group and superadmin_group in self.groups.all():
                return True
        return False

    @property
    def is_admin(self):
        return (
            self.system_role == self.SystemRole.ADMIN or self.is_superuser_group_member
        )

    @property
    def is_action_manager(self):
        return self.system_role == self.SystemRole.ACTION_MANAGER or self.is_admin

    @property
    def is_user_manager(self):
        return self.system_role == self.SystemRole.USER_MANAGER or self.is_admin

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


@receiver(pre_delete, sender=User)
def check_last_admin_delete(sender, instance, **kwargs):
    if instance.is_admin:
        if (
            User.objects.filter(system_role=User.SystemRole.ADMIN)
            .exclude(pk=instance.pk)
            .count()
            == 0
        ):
            raise PermissionDenied("Can't delete last admin user.")


@receiver(pre_save, sender=User)
def check_last_admin_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = User.objects.get(pk=instance.pk)
    if old_instance.is_admin and not instance.is_admin:
        if (
            User.objects.filter(system_role=User.SystemRole.ADMIN)
            .exclude(pk=instance.pk)
            .count()
            == 0
        ):
            raise PermissionDenied(
                "Can't set 'is_admin' to false for the last admin user."
            )


@receiver(pre_delete, sender=User)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        instance.profile_picture.delete(save=False)


@receiver(pre_save, sender=User)
def delete_replaced_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return
    old_instance = User.objects.get(pk=instance.pk)
    if not old_instance.profile_picture:
        return
    if old_instance.profile_picture != instance.profile_picture:
        old_instance.profile_picture.delete(save=False)


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True)

    users = models.ManyToManyField(User, related_name="roles", blank=True)
    groups = models.ManyToManyField(Group, related_name="roles", blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    create_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="roles_created", null=True
    )


filePathFactory = FileFieldPathFactory(
    base_path="user-background",
    allowed_extensions=["jpg", "jpeg", "png"],
)


class UserPreferences(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    disable_default_background_image = models.BooleanField(default=False)
    custom_background_image = ResizedImageField(
        size=settings.GALLERY_BACKGROUND_IMAGE_RESOLUTION,
        crop=["middle", "center"],
        force_format=settings.GALLERY_BACKGROUND_IMAGE_FORMAT,
        upload_to=filePathFactory.build_instance_path,
        blank=True,
        null=True,
    )


@receiver(pre_save, sender=User)
def create_user_preferences(sender, instance, **kwargs):
    if not instance.pk:
        UserPreferences.objects.create(user=instance)
