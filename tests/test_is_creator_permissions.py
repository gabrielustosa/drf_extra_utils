from django.contrib.auth import get_user_model
from django.urls import path
from django.test import TestCase, override_settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.test import APIClient

from drf_extra_utils.permissions import IsCreator
from .models import CreatorModel


class CreatorSerializer(ModelSerializer):
    class Meta:
        model = CreatorModel
        fields = '__all__'


class IsCreatorView(ModelViewSet):
    queryset = CreatorModel.objects.all()
    serializer_class = CreatorSerializer
    permission_classes = [IsCreator]


urlpatterns = [
    path('test/<int:pk>/', IsCreatorView.as_view({'get': 'retrieve'}), name='test-retrieve')
]


@override_settings(ROOT_URLCONF=__name__)
class TestIsCreatorPermission(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
        )

        self.obj = CreatorModel.objects.create(creator=self.user)
        self.url = reverse('test-retrieve', kwargs={'pk': self.obj.id})
        self.client = APIClient()

    def test_creator_permission_view(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_not_creator_do_not_have_access(self):
        not_creator = get_user_model().objects.create_user(
            username='admin',
            password='admin',
            email='admin@example.com',
        )
        self.client.force_authenticate(not_creator)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
