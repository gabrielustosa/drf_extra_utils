import pytest

from collections import OrderedDict

from django.core.paginator import Paginator

from rest_framework.fields import IntegerField

from drf_extra_utils.utils.fields import PaginatedListSerializer

from tests.models import FooModel
from tests.serializers import FooSerializer


class FakePaginator:

    def paginate_data(self, data):
        self.paginator = Paginator(data, 2)

        page = self.paginator.page(1)

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

    def test_list_serializer_model_filtering(self):
        serializer = PaginatedListSerializer(
            child=FooSerializer(),
            filter={'id__gte': 5}
        )
        data = serializer.to_representation(self.models)

        expected_data = FooSerializer(self.models[4:], many=True).data

        assert data == expected_data

    def test_list_serializer_model_pagination(self):
        serializer = PaginatedListSerializer(
            child=FooSerializer(),
            paginator=FakePaginator(),
        )
        data = serializer.to_representation(self.models)

        expected_data = {
            'count': 10,
            'results': FooSerializer(self.models[:2], many=True).data
        }

        assert data == expected_data

    def test_list_serializer_model_without_paginator(self):
        serializer = PaginatedListSerializer(child=FooSerializer())
        data = serializer.to_representation(self.models)

        expected_data = FooSerializer(self.models, many=True).data

        assert data == expected_data

    def test_list_serializer_model_pagination_and_filtering(self):
        serializer = PaginatedListSerializer(
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

    def test_list_serializer_model_filtering_without_matching(self):
        serializer = PaginatedListSerializer(
            child=FooSerializer(),
            paginator=FakePaginator(),
            filter={'bar': '123'}
        )
        data = serializer.to_representation(self.models)

        expected_data = []

        assert data == expected_data

    def test_list_serializer_pagination(self):
        serializer = PaginatedListSerializer(child=IntegerField(), paginator=FakePaginator())
        data = serializer.to_representation(self.objects)

        expected_data = {
            'count': 10,
            'results': self.objects[:2]
        }

        assert data == expected_data

    def test_list_serializer_without_paginator(self):
        serializer = PaginatedListSerializer(child=IntegerField())
        data = serializer.to_representation(self.objects)

        assert data == self.objects

    def test_list_serializer_filtering(self):
        serializer = PaginatedListSerializer(
            child=IntegerField(),
            filter=lambda n: n >= 5,
        )
        data = serializer.to_representation(self.objects)

        expected_data = self.objects[5:]

        assert data == expected_data

    def test_list_serializer_filtering_and_pagination(self):
        serializer = PaginatedListSerializer(
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

    def test_list_serializer_filtering_without_matching(self):
        serializer = PaginatedListSerializer(
            child=IntegerField(),
            filter=lambda n: n >= 10,
        )
        data = serializer.to_representation(self.objects)

        expected_data = []

        assert data == expected_data
