from rest_framework import serializers

from django.db.models import Manager


class RelatedObjectListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        self.filter = kwargs.pop('filter', None)
        self.paginator = kwargs.pop('paginator', None)

        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, Manager) else data

        if self.filter is not None:
            if hasattr(iterable, 'filter'):
                iterable = iterable.filter(**self.filter)
            elif isinstance(iterable, list):
                iterable = list(filter(self.filter, iterable))

        if self.paginator:
            iterable = self.paginator.paginate_data(iterable)

        ret = [self.child.to_representation(item) for item in iterable]

        if self.paginator and self.paginator.num_pages > 1:
            return self.paginator.get_paginated_data(ret)

        return ret
