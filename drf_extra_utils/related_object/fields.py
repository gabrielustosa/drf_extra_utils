from rest_framework import serializers

from django.db.models import Manager


class RelatedObjectListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        self.filter = kwargs.pop('filter', None)
        self.paginator = kwargs.pop('paginator', None)

        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        if isinstance(data, Manager):
            if self.filter:
                data = data.filter(**self.filter)
            iterable = data.all()

            if self.paginator:
                iterable = self.paginator.paginate_queryset(iterable)
        else:
            iterable = data

        ret = [self.child.to_representation(item) for item in iterable]

        if self.paginator and self.paginator.num_pages > 1:
            return self.paginator.get_paginated_data(ret)

        return ret
