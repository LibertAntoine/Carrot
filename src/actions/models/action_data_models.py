from abc import ABCMeta, abstractmethod
from django.db import models
from simple_history.models import HistoricalRecords


class AbstractActionData(ABCMeta, type(models.Model)):
    pass

class ActionData(models.Model, metaclass=AbstractActionData):
    TYPE = None
    history = HistoricalRecords(inherit=True)

    @property
    def type(self):
        return self.TYPE

    class Meta:
        abstract = True


class PythonActionData(ActionData):
    TYPE = "Python"

    code = models.TextField()

class LinkActionData(ActionData):
    TYPE = "Link"

    url = models.URLField()

