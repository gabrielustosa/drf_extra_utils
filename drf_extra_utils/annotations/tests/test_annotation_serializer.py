from django.test import TestCase

from rest_framework.serializers import ModelSerializer

from drf_extra_utils.annotations.serializer import AnnotationFieldMixin

from .models import DummyModelAnnotation, FooModel


def annotate_in_model(model):
    return model.__class__.objects.annotate(
        **model.annotation_class.get_annotations('*')
    ).get(id=model.id)


class DummySerializer(AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = DummyModelAnnotation
        fields = '__all__'


class TestAnnotationSerializer(TestCase):
    def setUp(self):
        self.dummy_object = DummyModelAnnotation.objects.create()
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_2'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_1'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_1'))

    def test_model_serializer_annotations(self):
        self.dummy_object = annotate_in_model(self.dummy_object)

        serializer = DummySerializer(self.dummy_object)

        expected_data = {
            'id': self.dummy_object.id,
            'foo': [foo.id for foo in self.dummy_object.foo.all()],
            'count_foo': 6,
            'complex_foo': 13,
            'list_foo': {
                'test_1': 2,
                'test_2': 1,
                'test_3': 3
            }
        }

        assert serializer.data == expected_data

    def test_model_serializer_annotations_with_no_annotations(self):
        serializer = DummySerializer(self.dummy_object)

        expected_data = {
            'id': self.dummy_object.id,
            'foo': [foo.id for foo in self.dummy_object.foo.all()],
            'count_foo': None,
            'complex_foo': None,
            'list_foo': {
                'test_1': None,
                'test_2': None,
                'test_3': None
            }
        }

        assert serializer.data == expected_data
