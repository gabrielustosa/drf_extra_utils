from parameterized import parameterized

from django.test import TestCase, override_settings
from django.urls import path

from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from drf_extra_utils.annotations.view import AnnotationViewMixin
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin
from drf_extra_utils.utils.views import DynamicFieldsViewMixin

from .models import AnnotatedModel, FooModel


class AnnotatedModelSerializer(ModelSerializer):
    class Meta:
        model = AnnotatedModel
        fields = ('id', 'count_foo', 'complex_foo', 'list_foo')


class AnnotatedModelViewSet(AnnotationViewMixin, ModelViewSet):
    serializer_class = AnnotatedModelSerializer
    queryset = AnnotatedModel.objects.all()


class AnnotatedModelSerializerDynamic(DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        model = AnnotatedModel
        fields = ('id', 'count_foo', 'complex_foo', 'list_foo')
        min_fields = ('count_foo',)
        default_fields = ('list_foo',)


class AnnotatedModelViewSetDynamic(AnnotationViewMixin, DynamicFieldsViewMixin, ModelViewSet):
    serializer_class = AnnotatedModelSerializerDynamic
    queryset = AnnotatedModel.objects.all()


urlpatterns = [
    path('test/<int:pk>/', AnnotatedModelViewSet.as_view({'get': 'retrieve'}), name='test-retrieve'),
    path('dynamic/<int:pk>/', AnnotatedModelViewSetDynamic.as_view({'get': 'retrieve'}), name='dynamic-retrieve'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestAnnotationView(TestCase):

    def setUp(self):
        self.annotated_model = AnnotatedModel.objects.create()
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_1') for _ in range(2)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_2') for _ in range(1)])
        self.annotated_model.foo.add(*[FooModel.objects.create(bar='test_3') for _ in range(4)])

        self.url = reverse('test-retrieve', kwargs={'pk': self.annotated_model.id})
        self.dynamic_url = reverse('dynamic-retrieve', kwargs={'pk': self.annotated_model.id})

        self.client = APIClient()

    def test_annotation_model_view(self):
        response = self.client.get(self.url)

        expected_data = {
            'id': self.annotated_model.id,
            'count_foo': 7,
            'complex_foo': 16,
            'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 4}
        }

        assert response.data == expected_data

    def test_annotation_optimization(self):
        with self.assertNumQueries(1):
            self.client.get(self.url)

    def test_annotation_model_still_working_without_dynamic_fields_mixin(self):
        response = self.client.get(f'{self.url}?fields=count_foo')

        expected_data = {
            'id': self.annotated_model.id,
            'count_foo': 7,
            'complex_foo': 16,
            'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 4}
        }

        assert response.data == expected_data

    def test_annotation_model_view_dynamic_fields(self):
        response = self.client.get(f'{self.dynamic_url}?fields=count_foo,list_foo')

        expected_data = {
            'count_foo': 7,
            'list_foo': {
                'test_1': 2,
                'test_2': 1,
                'test_3': 4
            }
        }

        assert response.data == expected_data

    @parameterized.expand([
        ('@default', {'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 4}}),
        ('@min', {'count_foo': 7}),
    ])
    def test_annotation_model_view_dynamic_field_type(self, field_type, expected):
        response = self.client.get(f'{self.dynamic_url}?fields={field_type}')

        assert response.data == expected

    def test_annotation_model_view_dynamic_field_type_all(self):
        response = self.client.get(f'{self.dynamic_url}?fields=@all')

        expected_data = {
            'id': self.annotated_model.id,
            'count_foo': 7,
            'complex_foo': 16,
            'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 4}
        }

        assert response.data == expected_data
