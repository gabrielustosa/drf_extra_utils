from django.db import models
from rest_framework.fields import IntegerField, ReadOnlyField

from drf_extra_utils.annotations.decorator import model_annotation
from drf_extra_utils.annotations.handler import ModelAnnotationHandler
from drf_extra_utils.annotations.objects import ANNOTATION_PREFIX, ANNOTATION_LIST_PREFIX
from drf_extra_utils.annotations.utils import get_serializer_field_from_annotation


def test_get_serializer_field_from_annotation():
    annotation = models.Count('test')
    field = get_serializer_field_from_annotation(annotation)

    assert isinstance(field, IntegerField)


def test_get_serializer_field_from_annotation_without_output_field():
    annotation = models.Avg('test')
    rest_field = get_serializer_field_from_annotation(annotation)

    assert isinstance(rest_field, ReadOnlyField)


class HandlerModel(models.Model):
    test = models.TextField()

    def func(self):
        pass

    @model_annotation
    def annotation_test(self):
        return 'annotation_test'

    def func_2(self):
        pass

    @model_annotation
    def annotation_list(self):
        return {
            'list_1': 1,
            'list_2': 2
        }

    class Meta:
        pass


class EmptyHandlerModel(models.Model):
    test = models.TextField()
    test_b = models.TextField()

    def test_1(self):
        pass


handler = ModelAnnotationHandler(model=HandlerModel)
empty_handler = ModelAnnotationHandler(model=EmptyHandlerModel)

annotation_test_name = '{0}{1}'.format(ANNOTATION_PREFIX, 'annotation_test')
annotation_list_1_name = '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_1')
annotation_list_2_name = '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_2')


def test_model_annotation_handler_collect_annotations():
    annotations = handler.annotations

    expected_annotations = ['annotation_test', 'annotation_list']

    assert len(annotations) == 2
    for annotation in expected_annotations:
        assert annotation in annotations


def test_model_annotation_empty_handler_collect_annotations():
    annotations = empty_handler.annotations

    assert annotations == {}


def test_model_annotation_handler_get_annotations():
    annotations = handler.get_annotations('id', 'annotation_test', 'name', 'test')

    expected_annotations = {
        annotation_test_name: 'annotation_test'
    }

    assert annotations == expected_annotations


def test_model_annotation_empty_handler_get_annotations():
    annotations = empty_handler.get_annotations('id', 'annotation_test', 'name', 'test')

    assert annotations == {}


def test_model_annotation_handler_get_annotations_with_star():
    annotations = handler.get_annotations('*')

    expected_annotations = {
        annotation_test_name: 'annotation_test',
        annotation_list_1_name: 1,
        annotation_list_2_name: 2,
    }

    for name, annotation in expected_annotations.items():
        assert name in annotations
        assert annotations[name] == annotation


def test_model_annotation_empty_handler_get_annotations_with_star():
    annotations = empty_handler.get_annotations('*')

    assert annotations == {}
