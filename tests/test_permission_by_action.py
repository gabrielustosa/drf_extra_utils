import pytest

from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from drf_extra_utils.views import PermissionByActionMixin


class RelatedObjectViewSet(PermissionByActionMixin, APIView):
    permission_classes_by_action = {
        'retrieve': [AllowAny],
        ('list', 'create', 'destroy'): [IsAdminUser],
        'default': [IsAuthenticated]
    }


class TestActionPermission:
    def setup_method(self):
        self.view = RelatedObjectViewSet()

    @pytest.mark.parametrize('action,expected_permissions', [
        ('retrieve', [AllowAny]),
        ('list', [IsAdminUser]),
        ('create', [IsAdminUser]),
        ('default', [IsAuthenticated])
    ])
    def test_get_permission_by_action(self, action, expected_permissions):
        permissions = self.view.get_permissions_by_action(action)

        assert permissions == expected_permissions

    @pytest.mark.parametrize('action,expected_permissions', [
        ('retrieve', [AllowAny]),
        ('list', [IsAdminUser]),
        ('create', [IsAdminUser]),
        ('default', [IsAuthenticated])
    ])
    def test_permission_by_action_view_permissions(self, action, expected_permissions):
        self.view.action = action

        permissions = [permission.__class__ for permission in self.view.get_permissions()]

        assert permissions == expected_permissions

    def test_get_permission_by_action_no_exist(self):
        permissions = self.view.get_permissions_by_action('update')

        assert permissions is None

    def test_permission_by_action_default_view_permissions(self):
        self.view.action = 'update'

        permissions = [permission.__class__ for permission in self.view.get_permissions()]

        expected_permissions = [IsAuthenticated]

        assert permissions == expected_permissions
