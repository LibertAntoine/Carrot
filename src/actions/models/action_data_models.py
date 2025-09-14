from abc import ABCMeta, abstractmethod
from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

class AbstractActionData(ABCMeta, type(models.Model)):
    pass


class ActionData(models.Model, metaclass=AbstractActionData):
    TYPE = None
    history = HistoricalRecords(inherit=True)

    def save(self, *args, **kwargs):
        # Avoid new version if nothing changed
        if self.pk:
            old = type(self).objects.get(pk=self.pk)
            if all(
                getattr(self, field.name) == getattr(old, field.name)
                for field in self._meta.fields
                if field.name not in ["updated_at", "id"]
            ):
                return
        super().save(*args, **kwargs)

    @property
    def type(self):
        return self.TYPE

    class Meta:
        abstract = True


class PythonActionData(ActionData):
    TYPE = "Python"
    code = models.TextField(default="def run():\r\n    print('Hello world')")
    use_combobox = models.BooleanField(default=False)
    combobox_code = models.TextField(
        default="def get_options(context):\r\n    return ['Option 1', 'Option 2']"
    )


class WindowsCMDActionData(ActionData):
    TYPE = "Windows CMD"
    code = models.TextField(default="@echo off\r\n\r\necho Hello world")
    use_combobox = models.BooleanField(default=False)
    combobox_code = models.TextField(
        default="def get_options(context):\r\n    return ['Option 1', 'Option 2']"
    )


def validate_url_format(value):
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValidationError("Enter a valid URL (with http:// or https://).")


class LinkActionData(ActionData):
    TYPE = "Link"
    url = models.CharField(
        max_length=1048,
        default="https://example.com",
        validators=[validate_url_format],
    )
