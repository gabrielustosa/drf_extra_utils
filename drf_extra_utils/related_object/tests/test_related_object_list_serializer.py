import pytest

from collections import OrderedDict

from django.core.paginator import Paginator, InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.fields import IntegerField

from drf_extra_utils.related_object.fields import RelatedObjectListSerializer
from drf_extra_utils.related_object.tests.serializers import FooSerializer
from drf_extra_utils.tests.models import FooModel


class FakePaginator:

    def paginate_data(self, data):
        self.paginator = Paginator(data, 2)

        try:
            page = self.paginator.page(1)
        except InvalidPage:
            raise NotFound('Invalid page.')

        return list(page)

    @property
    def num_pages(self):
        return self.paginator.num_pages

    def get_paginated_data(self, data):
        return OrderedDict([
            ('count', self.paginator.count),
            ('results', data)
        ])


@pytest.mark.django_db
class TestRelatedObjectListSerializer:
    def setup_method(self):
        self.objects = [n for n in range(10)]
        self.models = FooModel.objects.filter(id__in=[FooModel.objects.create(bar='test').id for _ in range(10)])

    def test_related_object_list_serializer_model_filtering(self):
        serializer = RelatedObjectListSerializer(
            child=FooSerializer(),
            filter={'id__gte': 5}
        )
        data = serializer.to_representation(self.models)

        expected_data = FooSerializer(self.models[4:], many=True).data

        assert data == expected_data

    def test_related_object_list_serializer_model_pagination(self):
        serializer = RelatedObjectListSerializer(
            child=FooSerializer(),
            paginator=FakePaginator(),
        )
        data = serializer.to_representation(self.models)

        expected_data = {
            'count': 10,
            'results': FooSerializer(self.models[:2], many=True).data
        }

        assert data == expected_data

    def test_related_object_list_serializer_model_without_paginator(self):
        serializer = RelatedObjectListSerializer(child=FooSerializer())
        data = serializer.to_representation(self.models)

        expected_data = FooSerializer(self.models, many=True).data

        assert data == expected_data

    def test_related_object_list_serializer_pagination_and_filtering(self):
        serializer = RelatedObjectListSerializer(
            child=FooSerializer(),
            paginator=FakePaginator(),
            filter={'id__gte': 5}
        )
        data = serializer.to_representation(self.models)

        expected_data = {
            'count': 6,
            'results': FooSerializer(self.models[4:6], many=True).data
        }

        assert data == expected_data

    def test_related_object_list_serializer_pagination(self):
        serializer = RelatedObjectListSerializer(child=IntegerField(), paginator=FakePaginator())
        data = serializer.to_representation(self.objects)

        expected_data = {
            'count': 10,
            'results': self.objects[:2]
        }

        assert data == expected_data

    def test_related_object_list_serializer_without_paginator(self):
        serializer = RelatedObjectListSerializer(child=IntegerField())
        data = serializer.to_representation(self.objects)

        assert data == self.objects

    def test_related_object_list_serializer_filtering(self):
        serializer = RelatedObjectListSerializer(
            child=IntegerField(),
            filter=lambda n: n >= 5,
        )
        data = serializer.to_representation(self.objects)

        expected_data = self.objects[5:]

        assert data == expected_data

    def test_related_object_list_serializer_filtering_and_pagination(self):
        serializer = RelatedObjectListSerializer(
            child=IntegerField(),
            paginator=FakePaginator(),
            filter=lambda n: n >= 5,
        )
        data = serializer.to_representation(self.objects)

        expected_data = {
            'count': 5,
            'results': self.objects[5:7]
        }

        assert data == expected_data
