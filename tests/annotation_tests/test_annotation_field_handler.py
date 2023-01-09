from django.db import models
from rest_framework.fields import IntegerField

from drf_extra_utils.annotations.decorator import model_annotation
from drf_extra_utils.annotations.fields import AnnotationListField
from drf_extra_utils.annotations.handler import ModelAnnotationFieldHandler, _get_annotation_serializer_field


def test_model_annotation_field_handler_get_annotation_serializer_field():
    annotation = models.Count('annotation')
    field = _get_annotation_serializer_field(annotation)

    assert isinstance(field, IntegerField)


def test_model_annotation_field_handler_get_annotation_serializer_field_list():
    annotation = {
        'test': models.Count('test'),
        'test_1': models.Count('test')
    }
    field = _get_annotation_serializer_field(annotation)

    assert isinstance(field, AnnotationListField)


class HandlerFieldModel(models.Model):
    test = models.TextField()

    def func(self):
        pass

    @model_annotation
    def annotation_test(self):
        return models.Count('test')

    def func_2(self):
        pass

    @model_annotation
    def annotation_list(self):
        return {
            'list_1': models.Count('list_1'),
            'list_2': models.Count('list_2')
        }

    class Meta:
        pass


class EmptyHandlerFieldModel(models.Model):
    test = models.TextField()
    test_b = models.TextField()

    def test_1(self):
        pass


handler = ModelAnnotationFieldHandler(model=HandlerFieldModel)
empty_handler = ModelAnnotationFieldHandler(model=EmptyHandlerFieldModel)


def test_model_annotation_field_handler_annotation_collect():
    annotations = handler.annotations

    expected_annotations = ['annotation_test', 'annotation_list']

    assert len(annotations) == 2
    for annotation in expected_annotations:
        assert annotation in annotations


def test_model_annotation_field_empty_handler_annotation_collect():
    annotations = empty_handler.annotations

    assert annotations == {}


def test_model_annotation_field_handler_get_annotation_serializer_fields():
    fields = handler.get_annotation_serializer_fields()

    expected_fields = {
        'annotation_test': IntegerField,
        'annotation_list': AnnotationListField
    }

    for name, field in expected_fields.items():
        assert name in fields
        assert isinstance(fields[name], field)


def test_model_annotation_field_empty_handler_get_annotation_serializer_fields():
    fields = empty_handler.get_annotation_serializer_fields()

    assert fields == {}
