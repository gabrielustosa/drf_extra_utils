from django.test import TestCase
from rest_framework import serializers
from drf_extra_utils.fields import GenericField

from .models import Text, Link


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ('content',)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('url',)


class GenericFieldTests(TestCase):
    def setUp(self):
        self.text = Text.objects.create(content='Test content')
        self.link = Link.objects.create(url='https://google.com')
        self.link2 = Link.objects.create(url='https://youtube.com')

        self.serializer = GenericField({
            Text: TextSerializer(),
            Link: LinkSerializer()
        })

        self.list_serializer = serializers.ListSerializer(child=self.serializer)

    def test_serialize(self):
        self.assertEqual(
            self.serializer.to_representation(self.text),
            {'content': 'Test content'},
        )
        self.assertEqual(
            self.serializer.to_representation(self.link),
            {'url': 'https://google.com'},
        )

    def test_deserializer(self):
        text = self.serializer.to_internal_value({'content': 'Test content'})
        link = self.serializer.to_internal_value({'url': 'https://google.com'})
        self.assertTrue(isinstance(text, Text))
        self.assertTrue(isinstance(link, Link))

    def test_serialize_list(self):
        actual = self.list_serializer.to_representation([
            self.text, self.link, self.link2, self.text,
        ])
        expected = [
            {'content': 'Test content'},
            {'url': 'https://google.com'},
            {'url': 'https://youtube.com'},
            {'content': 'Test content'},
        ]
        self.assertEqual(actual, expected)

    def test_deserializer_list(self):
        validated_data = self.list_serializer.to_internal_value([
            {'content': 'Test content'},
            {'url': 'https://google.com'},
            {'url': 'https://youtube.com'},
            {'content': 'Test content'},
        ])

        instances = [Text, Link, Link, Text]

        for index, instance in enumerate(instances):
            self.assertTrue(isinstance(validated_data[index], instance))

    def test_serializer_source_none(self):
        with self.assertRaises(RuntimeError) as exc:
            GenericField({
                Text: TextSerializer(source='test'),
                Link: LinkSerializer(source='test')
            })
            self.assertEqual(str(exc.exception), 'TextSerializer() cannot be re-used. Create a new instance.')

    def test_serializer_invalid_data(self):
        class ImproperlySerializer(serializers.ModelSerializer):
            class Meta:
                model = Text
                fields = '__all__'

        serializer = GenericField({
            Text: ImproperlySerializer(),
        })

        with self.assertRaises(serializers.ValidationError) as exc:
            serializer.to_internal_value({'ta': 'text'})
            self.assertEqual(str(exc.exception), 'Invalid model - model not available.')

    def test_get_serializer_for_invalid_instance(self):
        serializer = GenericField({
            Text: TextSerializer(),
        })
        with self.assertRaises(serializers.ValidationError) as exc:
            instance = Link.objects.create(url='https://test.com')
            serializer.get_serializer_for_instance(instance)
            self.assertEqual(str(exc.exception), 'Invalid model - model not available.')

