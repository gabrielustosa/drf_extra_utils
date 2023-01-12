from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import path

from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from drf_extra_utils.related_object.serializers import RelatedObjectMixin
from drf_extra_utils.related_object.views import RelatedObjectViewMixin

from . import models, serializers


class FakeObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(request.user, 'fake_object_permission', False)


class FakePermission(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'fake_permission', False)


class RelatedForeignSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedForeignModel
        fields = '__all__'
        related_objects = {
            'foo': {
                'serializer': serializers.FooSerializer,
                'permissions': [FakeObjectPermission],
            },
        }


class RelatedForeignViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = RelatedForeignSerializer
    queryset = models.RelatedForeignModel.objects.all()


urlpatterns = [
    path('foreign/<int:pk>/', RelatedForeignViewSet.as_view({'get': 'retrieve'}), name='foreign-retrieve')
]

fake_permission_related_object = {
    'foo': {
        'serializer': serializers.FooSerializer,
        'permissions': [FakePermission],
    },
}


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectPermission(TestCase):
    def setUp(self):
        self.foo = models.FooModel.objects.create(bar='test')
        self.foreign_model = models.RelatedForeignModel.objects.create(foo=self.foo)
        self.client = APIClient()

    def test_related_object_permission_object(self):
        user = get_user_model().objects.create_user(
            username='admin',
            password='admin',
            email='admin@example.com',
        )

        user.fake_object_permission = True
        self.client.force_authenticate(user)

        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})
        response = self.client.get(f'{url}?fields[foo]=id,bar')

        assert response.status_code == status.HTTP_200_OK

    def test_related_object_permission_object_denied(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})
        response = self.client.get(f'{url}?fields[foo]=id,bar')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {'detail': 'You do not have permission to access the related object `foo`.'}

    @patch(f'{__name__}.RelatedForeignSerializer.Meta.related_objects', fake_permission_related_object)
    def test_related_object_permission(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
        )

        user.fake_permission = True
        self.client.force_authenticate(user)

        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})
        response = self.client.get(f'{url}?fields[foo]=id,bar')

        assert response.status_code == status.HTTP_200_OK

    @patch(f'{__name__}.RelatedForeignSerializer.Meta.related_objects', fake_permission_related_object)
    def test_related_object_permission_denied(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})
        response = self.client.get(f'{url}?fields[foo]=id,bar')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {'detail': 'You do not have permission to access the related object `foo`.'}
