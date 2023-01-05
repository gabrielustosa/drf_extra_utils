from rest_framework.fields import IntegerField, CharField
from rest_framework.serializers import ListSerializer

from .. import serializers


class TestRelatedObjectMixin:
    def test_related_objects(self):
        context = {'related_objects': {'foo': ['bar'], 'foes': ['bar'], 'bars': ['id', 'multiple_model']}}
        serializer = serializers.RelatedMultipleSerializer(context=context)

        expected_related_objects = {'foo': ['bar'], 'foes': ['bar'], 'bars': ['id', 'multiple_model']}

        assert serializer.related_objects == expected_related_objects

    def test_related_objects_with_invalid_fields(self):
        context = {'related_objects': {'foo': ['bar'], 'invalid_field': ['test']}}
        serializer = serializers.RelatedMultipleSerializer(context=context)

        expected_related_objects = {'foo': ['bar']}

        assert serializer.related_objects == expected_related_objects

    def test_get_related_objects(self):
        serializer = serializers.RelatedMultipleSerializer()

        expected_related_objects = {
            'foo': {
                'serializer': serializers.FooSerializer
            },
            'foes': {
                'serializer': serializers.FooSerializer,
                'many': True,
            },
            'bars': {
                'serializer': serializers.M21Serializer,
                'many': True
            }
        }

        assert serializer.get_related_objects() == expected_related_objects

    def test_get_related_object_serializer(self):
        serializer = serializers.RelatedMultipleSerializer()

        Serializer = serializer.get_related_object_serializer('foo')

        assert Serializer == serializers.FooSerializer

    def test_get_related_object_serializer_from_string(self):
        serializer = serializers.FooSerializer()

        Serializer = serializer.get_related_object_serializer('related_foreign')

        assert Serializer == serializers.RelatedForeignSerializer

    def test_related_object_fields(self):
        context = {'related_objects': {'foo': ['bar'], 'foes': ['bar'], 'bars': ['id', 'multiple_model']}}
        serializer = serializers.RelatedMultipleSerializer(context=context)

        fields = serializer._get_related_objects_fields()

        expected_fields = ['foo', 'foes', 'bars']

        for field_name in expected_fields:
            assert field_name in fields

    def test_related_objects_get_fields(self):
        context = {'related_objects': {'related_foreign': ['id']}}
        serializer = serializers.FooSerializer(context=context)

        fields = serializer.get_fields()

        expected_fields = {
            'id': IntegerField,
            'bar': CharField,
            'related_foreign': ListSerializer
        }

        for field_name, serializer in expected_fields.items():
            assert field_name in fields
            assert isinstance(fields[field_name], serializer)

