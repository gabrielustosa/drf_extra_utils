import pytest

from django.db import models

from rest_framework import serializers

from .annotations import TestAnnotations

from drf_extra_utils.annotations.base import _get_rest_field_by_annotation
from drf_extra_utils.annotations.fields import AnnotationField, AnnotationDictField

annotation_class = TestAnnotations()


def test_annotation_fields_collect():
    expected_fields = ['count_foo', 'complex_foo', 'list_foo']

    annotation_fields = list(annotation_class.annotation_fields)

    assert len(annotation_fields) == 3
    for field in expected_fields:
        assert field in annotation_fields


def test_intersection_fields():
    fields = ['id', 'name', 'count_foo', 'test', 'complex_foo']

    intersection_fields = annotation_class.intersection_fields(fields)

    expected_fields = ['count_foo', 'complex_foo']

    assert len(intersection_fields) == 2
    for field in expected_fields:
        assert field in intersection_fields


def test_intersection_star_in_fields():
    fields = ['id', 'name', 'test', '*']

    intersection_fields = list(annotation_class.intersection_fields(fields))

    expected_fields = ['count_foo', 'complex_foo', 'list_foo']

    assert len(intersection_fields) == 3
    for field in expected_fields:
        assert field in intersection_fields


def test_get_annotation_value():
    annotation = annotation_class.get_annotation_value('count_foo')

    expected_annotation = models.Count('foo', distinct=True)

    assert annotation == expected_annotation


def test_get_none_annotation_value():
    annotation = annotation_class.get_annotation_value('undefined')

    assert annotation is None


def test_get_annotation():
    annotation = annotation_class.get_annotation('count_foo')

    expected_annotation = {
        'count_foo': annotation_class.count_foo()
    }

    assert annotation == expected_annotation


def test_get_list_annotation():
    annotation = annotation_class.get_annotation('list_foo')

    expected_annotation = {
        'test_1': models.Count('foo__id', filter=models.Q(foo__bar='test_1')),
        'test_2': models.Count('foo__id', filter=models.Q(foo__bar='test_2')),
        'test_3': models.Count('foo__id', filter=models.Q(foo__bar='test_3')),
    }

    assert len(annotation) == 3
    for key, value in expected_annotation.items():
        assert key in annotation
        assert value == annotation[key]


def test_get_annotations():
    fields = ('id', 'title', 'name', 'count_foo', 'test', 'complex_foo', 'list_foo')
    annotations = annotation_class.get_annotations(*fields)

    expected_annotations = {
        'count_foo': models.Count,
        'complex_foo': models.Sum,
        'test_1': models.Count,
        'test_2': models.Count,
        'test_3': models.Count,
    }

    assert len(annotations) == 5
    for key, value in expected_annotations.items():
        assert key in annotations
        assert isinstance(annotations[key], value)


def test_get_annotation_serializer_field():
    annotation_field = annotation_class.get_annotation_serializer_field('count_foo')

    assert isinstance(annotation_field, AnnotationField)
    assert isinstance(annotation_field.child, serializers.IntegerField)
    assert annotation_field.annotation_name == 'count_foo'


def test_get_annotation_dict_serializer_field():
    annotation_field = annotation_class.get_annotation_serializer_field('list_foo')

    expected_children = {
        'test_1': AnnotationField(annotation_name='test_1', child=serializers.IntegerField()),
        'test_2': AnnotationField(annotation_name='test_2', child=serializers.IntegerField()),
        'test_3': AnnotationField(annotation_name='test_3', child=serializers.IntegerField()),
    }

    assert isinstance(annotation_field, AnnotationDictField)
    assert len(annotation_field.children) == 3
    for child in annotation_field.children:
        expected_child = expected_children[child.annotation_name]
        assert child.annotation_name == expected_child.annotation_name
        assert child.child.__class__ == expected_child.child.__class__


def test_get_annotation_serializer_fields():
    annotation_fields = annotation_class.get_annotation_serializer_fields()

    expected_fields = {
        'count_foo': AnnotationField(annotation_name='count_foo', child=serializers.IntegerField()),
        'complex_foo': AnnotationField(annotation_name='complex_foo', child=serializers.IntegerField()),
        'list_foo': AnnotationDictField(children=[
            AnnotationField(annotation_name='test_1', child=serializers.IntegerField()),
            AnnotationField(annotation_name='test_2', child=serializers.IntegerField()),
            AnnotationField(annotation_name='test_3', child=serializers.IntegerField())
        ])
    }

    assert len(annotation_fields) == 3
    for key, value in expected_fields.items():
        assert key in annotation_fields
        assert annotation_fields[key].__class__ == value.__class__


def test_get_rest_field_by_annotation():
    annotation = models.Count('test')
    rest_field = _get_rest_field_by_annotation(annotation)

    assert isinstance(rest_field, serializers.IntegerField)


def test_get_rest_field_by_annotation_without_output_field():
    annotation = models.Avg('test')
    rest_field = _get_rest_field_by_annotation(annotation)

    assert isinstance(rest_field, serializers.ReadOnlyField)
