from django.db import models

from drf_extra_utils.utils.models import TimeStampedBase, CreatorBase


# CreateUpdateOnly Model

class BarModel(models.Model):
    foo = models.CharField(max_length=100)
    bar = models.IntegerField(null=True, default=0)


# TimeStampedBase model

class DateTimeModel(TimeStampedBase):
    pass


# CreatorBase model

class CreatorModel(CreatorBase):
    pass
