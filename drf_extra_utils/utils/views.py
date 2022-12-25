from rest_framework.permissions import AllowAny


class DynamicFieldViewMixin:
    """
    Mixin that takes additional fields in query_params that controls which fields should be displayed

    Example:
        https://example.com/resource/?fields=name,@default
    """

    def get_serializer(self, *args, **kwargs):
        fields = self.request.query_params.get('fields')
        if fields is not None:
            kwargs['fields'] = fields.split(',')
        return super().get_serializer(*args, **kwargs)


class PermissionByActionMixin:
    permission_classes_by_action = {
        ('default',): [AllowAny],
    }

    def get_permissions_by_action(self, action):
        for actions, permissions in self.permission_classes_by_action.items():
            if action in actions:
                return [permission() for permission in permissions]

    def get_permissions(self):
        permissions = self.get_permissions_by_action(self.action)
        return permissions if permissions else self.get_permissions_by_action('default')
