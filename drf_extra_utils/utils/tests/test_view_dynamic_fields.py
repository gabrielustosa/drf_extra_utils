from django.urls import path
from django.test import TestCase, override_settings

from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin
from drf_extra_utils.utils.tests.models import FooModel
from drf_extra_utils.utils.views import DynamicFieldViewMixin


class FooSerializer(DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        model = FooModel
        fields = '__all__'


class FooViewSet(DynamicFieldViewMixin, ModelViewSet):
    queryset = FooModel.objects.all()
    serializer_class = FooSerializer


urlpatterns = [
    path('foo/<int:pk>/', FooViewSet.as_view({'get': 'retrieve'}), name='foo-retrieve')
]


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
