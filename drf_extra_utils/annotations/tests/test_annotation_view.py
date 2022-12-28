from parameterized import parameterized

from django.test import TestCase, override_settings
from django.urls import path

from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from drf_extra_utils.annotations.serializer import AnnotationFieldMixin
from drf_extra_utils.utils.tests.models import DummyModelAnnotation, FooModel
from drf_extra_utils.annotations.views import AnnotationViewMixin
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin
from drf_extra_utils.utils.views import DynamicFieldViewMixin


class DummySerializer(AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = DummyModelAnnotation
        fields = '__all__'


class DummyViewSet(AnnotationViewMixin, ModelViewSet):
    serializer_class = DummySerializer
    queryset = DummyModelAnnotation.objects.all()


class DummySerializerDynamicFields(AnnotationFieldMixin, DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        model = DummyModelAnnotation
        fields = '__all__'
        min_fields = ('count_foo', 'list_foo')
        default_fields = ('list_foo', 'complex_foo')


class DummyViewSetDynamicFields(AnnotationViewMixin, DynamicFieldViewMixin, ModelViewSet):
    serializer_class = DummySerializerDynamicFields
    queryset = DummyModelAnnotation.objects.all()


urlpatterns = [
    path('test/<int:pk>/', DummyViewSet.as_view({'get': 'retrieve'}), name='test-retrieve'),
    path('dynamic/<int:pk>/', DummyViewSetDynamicFields.as_view({'get': 'retrieve'}), name='dynamic-retrieve'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestAnnotationView(TestCase):

    def setUp(self):
        self.dummy_object = DummyModelAnnotation.objects.create()
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_3'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_2'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_1'))
        self.dummy_object.foo.add(FooModel.objects.create(bar=f'test_1'))

        self.url = reverse('test-retrieve', kwargs={'pk': self.dummy_object.id})
        self.dynamic_url = reverse('dynamic-retrieve', kwargs={'pk': self.dummy_object.id})

        self.client = APIClient()

    def test_annotation_view(self):
        response = self.client.get(self.url)

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

        assert response.data == expected_data

    def test_annotation_dynamic_fields_doest_work_without_dynamic_mixin(self):
        response = self.client.get(f'{self.url}?fields=count_foo,list_foo')

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

        assert response.data == expected_data

    def test_annotation_dynamic_fields_view(self):
        response = self.client.get(f'{self.dynamic_url}?fields=count_foo,list_foo')

        expected_data = {
            'count_foo': 6,
            'list_foo': {
                'test_1': 2,
                'test_2': 1,
                'test_3': 3
            }
        }

        assert response.data == expected_data

    @parameterized.expand([
        ('@default', {'complex_foo': 13, 'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 3}}),
        ('@min', {'count_foo': 6, 'list_foo': {'test_1': 2, 'test_2': 1, 'test_3': 3}}),
    ])
    def test_annotation_dynamic_fields_in_field_types(self, field_type, expected):
        response = self.client.get(f'{self.dynamic_url}?fields={field_type}')

        assert response.data == expected

    def tset_annotation_dynamic_fields_all(self):
        response = self.client.get(f'{self.dynamic_url}?fields=@all')

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

        assert response.data == expected_data
