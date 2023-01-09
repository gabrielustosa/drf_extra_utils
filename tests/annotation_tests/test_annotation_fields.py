from django.db import models

from drf_extra_utils.annotations.fields import AnnotationListField


def test_annotation_list_field_is_read_only():
    field = AnnotationListField(annotations={})

    assert field.read_only


def test_annotation_list_field_to_representation():
    annotations = {
        'list_1': models.Value(1, output_field=models.IntegerField()),
        'list_2': models.Value(2, output_field=models.IntegerField()),
    }

    field = AnnotationListField(annotations=annotations)

    value = {
        'list_1': '1',
        'list_2': '2',
    }
    ret = field.to_representation(value)

    expected_value = {
        'list_1': 1,
        'list_2': 2
    }

    assert ret == expected_value


def test_annotation_list_field_to_representation_with_none_values():
    annotations = {
        'list_1': models.Value(1, output_field=models.IntegerField()),
        'list_2': models.Value(2, output_field=models.IntegerField()),
    }

    field = AnnotationListField(annotations=annotations)

    value = {
        'list_1': None,
        'list_2': None
    }
    ret = field.to_representation(value)

    expected_value = {
        'list_1': None,
        'list_2': None
    }

    assert ret == expected_value
