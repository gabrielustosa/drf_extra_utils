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

from drf_extra_utils.serializers import PermissionForFieldMixin
from drf_extra_utils.views import PermissionByActionMixin

from tests.related_object_tests.models import FooModel, RelatedForeignModel


class FakePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(request.user, 'fake_permission', False)


class RelatedForeignModelSerializer(PermissionForFieldMixin, ModelSerializer):
    class Meta:
        model = RelatedForeignModel
        fields = '__all__'
        permissions_for_field = {
            'foo': [FakePermission]
        }


class RelatedForeignViewSetView(PermissionByActionMixin, ModelViewSet):
    queryset = RelatedForeignModel.objects.all()
    serializer_class = RelatedForeignModelSerializer


urlpatterns = [
    path('test/', RelatedForeignViewSetView.as_view({'post': 'create'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestPermissionForField(TestCase):

    def setUp(self):
        self.foo = FooModel.objects.create(bar='test')
        self.url = reverse('test-retrieve')
        self.client = APIClient()

    def test_permission_for_field(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
        )
        user.fake_permission = True
        self.client.force_authenticate(user)

        response = self.client.post(self.url, {'foo': self.foo.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_for_field_denied(self):
        response = self.client.post(self.url, {'foo': self.foo.id})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {'detail': f'You do not have permission to use `foo` with id `{self.foo.id}`.'}


class TestPermissionForFieldMixin:

    def setup_method(self):
        self.serializer = RelatedForeignModelSerializer()

    def test_permission_for_field(self):
        expected_permissions = {
            ('foo',): [FakePermission]
        }

        assert self.serializer.permissions_for_field == expected_permissions

    @patch.object(RelatedForeignModelSerializer.Meta, 'permissions_for_field', {('test', 'model'): [FakePermission]})
    def test_permission_for_field_tuple_fields(self):
        expected_permissions = {
            ('test', 'model'): [FakePermission]
        }

        assert self.serializer.permissions_for_field == expected_permissions

    def test_get_permissions_for_field(self):
        permissions = self.serializer.get_permissions_for_field('foo')

        expected_permissions = [FakePermission]

        assert permissions == expected_permissions

    @patch.object(RelatedForeignModelSerializer.Meta, 'permissions_for_field', {('test', 'model'): [FakePermission]})
    def test_get_permission_for_tuple_fields(self):
        permissions = self.serializer.get_permissions_for_field('test')

        expected_permissions = [FakePermission]

        assert permissions == expected_permissions
