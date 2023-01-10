from django.urls import path
from django.test import TestCase, override_settings, RequestFactory

from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from tests.related_object_tests.models import FooModel

from drf_extra_utils.serializers import DynamicModelFieldsMixin
from drf_extra_utils.views import DynamicFieldsViewMixin


class FooSerializer(DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        model = FooModel
        fields = '__all__'


class FooViewSet(DynamicFieldsViewMixin, ModelViewSet):
    queryset = FooModel.objects.all()
    serializer_class = FooSerializer


urlpatterns = [
    path('foo/<int:pk>/', FooViewSet.as_view({'get': 'retrieve'}), name='foo-retrieve')
]

factory = RequestFactory()
request = factory.get('/')


@override_settings(ROOT_URLCONF=__name__)
class TestDynamicFieldsView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.foo = FooModel.objects.create(bar='test')
        self.url = reverse('foo-retrieve', kwargs={'pk': self.foo.id})

    def test_dynamic_view_fields(self):
        response = self.client.get(f'{self.url}?fields=id')

        expected_data = {
            'id': self.foo.id
        }

        assert response.data == expected_data

    def test_dynamic_view_fields_with_invalid_fields(self):
        response = self.client.get(f'{self.url}?fields=invalid,model,test')

        expected_data = {}

        assert response.data == expected_data

    def test_dynamic_fields_in_get_serializer(self):
        view = FooViewSet(format_kwarg=None)
        request.query_params = {'fields': 'test,field,model'}
        view.request = request

        serializer = view.get_serializer()

        assert 'fields' in serializer._kwargs
        assert serializer._kwargs['fields'] == ['test', 'field', 'model']
