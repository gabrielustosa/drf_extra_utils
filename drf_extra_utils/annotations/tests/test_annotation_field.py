from unittest.mock import MagicMock

from rest_framework import serializers
from rest_framework.fields import empty

from drf_extra_utils.annotations.fields import AnnotationField, AnnotationDictField

model = MagicMock(annotation='test', list_1='test_1', list_2='test_2', list_3='test_3')
not_annotated = empty()


def test_annotation_field_get_attribute():
    field = AnnotationField(annotation_name='annotation', child=serializers.CharField())

    attribute = field.get_attribute(model)

    expected_attribute = 'test'

    assert attribute == expected_attribute


def test_annotation_field_get_none_attribute():
    field = AnnotationField(annotation_name='annotation', child=serializers.CharField())

    attribute = field.get_attribute(not_annotated)

    assert attribute is None


def test_annotation_field_to_representation():
    field = AnnotationField(annotation_name='annotation', child=serializers.CharField())

    ret = field.to_representation(10)

    assert ret == '10'


def test_annotation_dict_field_get_attribute():
    field = AnnotationDictField(children=[
        AnnotationField(
            annotation_name=option,
            child=serializers.CharField()
        )
        for option in ('list_1', 'list_2', 'list_3')
    ])

    attribute = field.get_attribute(model)

    expected_attribute = {
        'list_1': 'test_1',
        'list_2': 'test_2',
        'list_3': 'test_3'
    }

    assert attribute == expected_attribute


def test_annotation_dict_field_get_none_attribute():
    field = AnnotationDictField(children=[
        AnnotationField(
            annotation_name=option,
            child=serializers.CharField()
        )
        for option in ('list_1', 'list_2', 'list_3')
    ])

    attribute = field.get_attribute(not_annotated)

    expected_attribute = {
        'list_1': None,
        'list_2': None,
        'list_3': None,
    }

    assert attribute == expected_attribute


def test_annotation_dict_field_to_representation():
    field = AnnotationDictField(children=[
        AnnotationField(
            annotation_name=option,
            child=serializers.CharField()
        )
        for option in ('list_1', 'list_2', 'list_3')
    ])

    ret = field.to_representation({
        1: 2,
        3: 4,
        5: 6
    })

    expected_ret = {
        1: '2',
        3: '4',
        5: '6',
    }

    assert ret == expected_ret
