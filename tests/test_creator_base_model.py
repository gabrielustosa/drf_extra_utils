from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from tests.models import CreatorModel


@pytest.mark.django_db
class TestCreatorBaseModel:
    def test_creator_assigned_on_create(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
        )
        obj = CreatorModel.objects.create(creator=user)
        assert obj.creator == user

    def test_creator_assigned_automatically(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
        )

        with patch('drf_extra_utils.utils.models.get_current_user', return_value=user):
            obj = CreatorModel.objects.create()
            assert obj.creator == user
