from django.db import models

from drf_extra_utils.models import TimeStampedBase, CreatorBase


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


# GenericField model

class Text(models.Model):
    content = models.TextField()


class Link(models.Model):
    url = models.URLField()
