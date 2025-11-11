from django.db import models
from jumper.storage_utils.file_field import FileFieldPathFactory
from django_resized import ResizedImageField
from django.conf import settings


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


filePathFactory = FileFieldPathFactory(
    base_path="background",
    allowed_extensions=["jpg", "jpeg", "png"],
)

def background_upload_to(instance, filename):
    return filePathFactory.build_instance_path(instance, filename)

class SystemInfo(SingletonModel):
    allow_action_workspaces = models.BooleanField(default=False)

    allow_background_image = models.BooleanField(default=False)
    default_background_image = ResizedImageField(
        size=settings.GALLERY_BACKGROUND_IMAGE_RESOLUTION,
        crop=["middle", "center"],
        force_format=settings.GALLERY_BACKGROUND_IMAGE_FORMAT,
        upload_to=background_upload_to,
        blank=True,
        null=True,
    )
    allow_user_custom_background_image = models.BooleanField(default=False)

    allow_action_sections = models.BooleanField(default=False)
    allow_users_to_hide_actions = models.BooleanField(default=False)
