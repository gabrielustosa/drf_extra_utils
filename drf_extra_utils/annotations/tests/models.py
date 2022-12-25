from django.db import models

from .annotations import TestAnnotations


class FooModel(models.Model):
    bar = models.CharField(max_length=100)


class DummyModelAnnotation(models.Model):
    foo = models.ManyToManyField(FooModel)
    annotation_class = TestAnnotations()
