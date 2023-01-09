from django.test import TestCase

from . import models, serializers


class TestRelatedObjectSerializer(TestCase):
    def setUp(self):
        self.foo = models.FooModel.objects.create(bar='test')
        self.foreign_model = models.RelatedForeignModel.objects.create(foo=self.foo)
        self.many_model = models.RelatedManyModel.objects.create()
        self.many_model.foes.add(self.foo)

    def test_related_object_serializer_foreign(self):
        context = {'related_objects': {'foo': ['id', 'bar']}}
        serializer = serializers.RelatedForeignSerializer(self.foreign_model, context=context)

        expected_data = {
            'id': self.foreign_model.id,
            'foo': {
                'id': self.foo.id,
                'bar': self.foo.bar
            }
        }

        assert serializer.data == expected_data

    def test_related_object_serializer_many_to_many(self):
        context = {'related_objects': {'foes': ['id', 'bar']}}
        serializer = serializers.RelatedManySerializer(self.many_model, context=context)

        expected_data = {
            'id': self.many_model.id,
            'foes': [{
                'id': self.foo.id,
                'bar': self.foo.bar
            }]
        }

        assert serializer.data == expected_data

    def test_related_object_serializer_many_to_one(self):
        context = {'related_objects': {'related_foreign': ['id']}}
        serializer = serializers.FooSerializer(self.foo, context=context)

        expected_data = {
            'id': self.foo.id,
            'bar': self.foo.bar,
            'related_foreign': [{
                'id': self.foreign_model.id,
            }]
        }

        assert serializer.data == expected_data

    def test_multiple_related_objects_serializer(self):
        multiple_model = models.RelatedMultipleRelatedModel.objects.create(foo=self.foo)
        multiple_model.foes.add(self.foo)
        m21_model = models.M21Model.objects.create(multiple_model=multiple_model)

        context = {'related_objects': {'foo': ['bar'], 'foes': ['bar'], 'bars': ['id', 'multiple_model']}}
        serializer = serializers.RelatedMultipleSerializer(multiple_model, context=context)

        expected_data = {
            'id': multiple_model.id,
            'foo': {
                'bar': self.foo.bar
            },
            'foes': [{
                'bar': self.foo.bar
            }],
            'bars': [{
                'id': m21_model.id,
                'multiple_model': multiple_model.id
            }]
        }

        assert serializer.data == expected_data

    def test_related_object_serializer_with_invalid_related_object(self):
        context = {'related_objects': {'invalid_model': ['id', 'title']}}
        serializer = serializers.RelatedForeignSerializer(self.foreign_model, context=context)

        expected_data = {
            'id': self.foreign_model.id,
            'foo': self.foreign_model.foo.id
        }

        assert serializer.data == expected_data
