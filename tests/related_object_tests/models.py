from django.db import models
from django.db.models.functions import Concat

from drf_extra_utils.annotations.decorator import model_annotation


class FooModel(models.Model):
    bar = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class RelatedForeignModel(models.Model):
    foo = models.ForeignKey(FooModel, on_delete=models.CASCADE, related_name='related_foreign')

    class Meta:
        ordering = ['id']


class RelatedManyModel(models.Model):
    foes = models.ManyToManyField(FooModel)

    class Meta:
        ordering = ['id']


class RelatedMultipleRelatedModel(models.Model):
    foes = models.ManyToManyField(FooModel)
    foo = models.ForeignKey(FooModel, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class M21Model(models.Model):
    multiple_model = models.ForeignKey(
        RelatedMultipleRelatedModel,
        on_delete=models.CASCADE,
        related_name='bars'
    )

    class Meta:
        ordering = ['id']


# RelatedObject Annotations

class FooModelAnnotated(models.Model):
    @model_annotation
    def value_1(self):
        return models.Value('value_1', output_field=models.CharField())

    @model_annotation
    def my_id(self):
        return Concat(models.Value('my id is: '), models.F('id'), output_field=models.CharField())

    class Meta:
        ordering = ['id']


class RelatedForeignModelAnnotation(models.Model):
    foo = models.ForeignKey(FooModelAnnotated, on_delete=models.CASCADE, related_name='related_foreign')

    class Meta:
        ordering = ['id']


class RelatedManyModelAnnotation(models.Model):
    foes = models.ManyToManyField(FooModelAnnotated)

    class Meta:
        ordering = ['id']


class RelatedMultipleRelatedModelAnnotation(models.Model):
    foes = models.ManyToManyField(FooModelAnnotated)
    foo = models.ForeignKey(FooModelAnnotated, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class M21ModelAnnotation(models.Model):
    multiple_model = models.ForeignKey(
        RelatedMultipleRelatedModelAnnotation,
        on_delete=models.CASCADE,
        related_name='bars'
    )

    @model_annotation
    def value_1(self):
        return models.Value('value_1', output_field=models.CharField())

    @model_annotation
    def my_id(self):
        return Concat(models.Value('my id is: '), models.F('id'), output_field=models.CharField())

    class Meta:
        ordering = ['id']


class BarAnnotation(models.Model):
    class Meta:
        ordering = ['id']


class M21BarAnnotation(models.Model):
    bar = models.ForeignKey(
        BarAnnotation,
        on_delete=models.CASCADE,
        related_name='bars',
    )

    @model_annotation
    def value_1(self):
        return models.Value('value_1', output_field=models.CharField())

    @model_annotation
    def my_id(self):
        return Concat(models.Value('my id is: '), models.F('id'), output_field=models.CharField())

    class Meta:
        ordering = ['id']
