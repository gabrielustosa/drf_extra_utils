from parameterized import parameterized_class

from django.test import TestCase
from drf_extra_utils.annotations.serializer import AnnotationFieldMixin
from rest_framework.serializers import ModelSerializer

from .models import AnnotatedModel, FooModel


@parameterized_class(('annotation_name', 'expected_value'), [
    ('count_foo', 7),
    ('complex_foo', 16),
    ('list_foo', {'test_1': 2, 'test_2': 1, 'test_3': 4})
])
class TestAnnotationAttribute(TestCase):

    def setUp(self):
        self.annotated_model = AnnotatedModel.objects.create()
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_1') for _ in range(2)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_2') for _ in range(1)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_3') for _ in range(4)])

    def test_model_annotation_attribute_optimization(self):
        with self.assertNumQueries(1):
            for _ in range(10):
                getattr(self.annotated_model, self.annotation_name)

    def test_model_annotation_attribute_fetching(self):
        annotation_value = getattr(self.annotated_model, self.annotation_name)

        assert annotation_value == self.expected_value


class AnnotatedModelSerializer(AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = AnnotatedModel
        fields = ('id',)


class TestAnnotationSerialization(TestCase):

    def setUp(self):
        self.annotated_model = AnnotatedModel.objects.create()
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_1') for _ in range(2)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_2') for _ in range(1)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_3') for _ in range(4)])

    def test_model_annotation_serialization(self):
        serializer = AnnotatedModelSerializer(self.annotated_model)

        expected_data = {
            'id': self.annotated_model.id,
            'count_foo': 7,
            'complex_foo': 16,
            'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 4}
        }

        assert serializer.data == expected_data
