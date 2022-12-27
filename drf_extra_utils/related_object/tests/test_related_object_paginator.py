import pytest

from unittest.mock import patch

from django.test import RequestFactory
from rest_framework.exceptions import NotFound

from drf_extra_utils.related_object.paginator import RelatedObjectPaginator

factory = RequestFactory()
request = factory.get('/')


class TestRelatedObjectPaginator:
    def setup_method(self):
        self.related_objects = [n for n in range(5)]
        self.paginator = RelatedObjectPaginator(
            related_object_name='model',
            related_object_fields=['id', 'name', 'page_size(2)'],
            request=request
        )

    def test_related_object_paginate_queryset(self):
        queryset = self.paginator.paginate_data(self.related_objects)

        assert len(queryset) == 2
        assert queryset == self.related_objects[:2]

    def test_related_object_pagination_with_default_page_size(self):
        self.paginator.related_object_fields = ['id', 'name']

        with patch('drf_extra_utils.related_object.paginator.RELATED_OBJECT_PAGINATED_BY', 3):
            queryset = self.paginator.paginate_data(self.related_objects)

            assert len(queryset) == 3
            assert queryset == self.related_objects[:3]

    def test_related_object_pagination_selecting_page(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(3)']

        queryset = self.paginator.paginate_data(self.related_objects)

        assert len(queryset) == 1
        assert queryset == self.related_objects[4:]

    def test_related_object_pagination_with_invalid_page_size(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(0)', 'page(1)']

        with pytest.raises(NotFound) as exc:
            self.paginator.paginate_data(self.related_objects)
        assert exc.match('Invalid page size for `model`.')

    def test_related_object_pagination_with_invalid_page(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(61)']

        with pytest.raises(NotFound) as exc:
            self.paginator.paginate_data(self.related_objects)
        assert exc.match('Invalid page for `model`.')

    def test_related_object_paginator_num_pages(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)']

        self.paginator.paginate_data(self.related_objects)

        assert self.paginator.num_pages == 3

    def test_related_object_paginator_page_number(self):
        self.paginator.related_object_fields = ['id', 'name', 'page(5)', 'page_size(3)']

        page_number = self.paginator.page_number

        assert page_number == '5'

    def test_related_object_paginator_page_number_default_value(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(3)']

        page_number = self.paginator.page_number

        assert page_number == 1

    def test_related_object_paginator_page_size(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(8)', 'page(3)']

        page_size = self.paginator.page_size

        assert page_size == '8'

    @patch('drf_extra_utils.related_object.paginator.RELATED_OBJECT_PAGINATED_BY', 3)
    def test_related_object_paginator_page_size_default_value(self):
        self.paginator.related_object_fields = ['id', 'name', 'page(3)']

        page_size = self.paginator.page_size

        assert page_size == 3

    def test_related_object_paginator_get_field_param(self):
        field_param = self.paginator.field_param

        assert field_param == 'fields[model]'

    def test_related_object_paginator_get_page_param(self):
        page_param = self.paginator.get_page_param(10)

        assert page_param == 'page(10)'

    def test_related_object_paginator_get_next_link(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)']

        self.paginator.paginate_data(self.related_objects)

        next_link = self.paginator.get_next_link()

        assert next_link == 'http://testserver/?fields%5Bmodel%5D=id%2Cname%2Cpage_size%282%29%2Cpage%282%29'

    def test_related_object_paginator_get_next_link_if_there_is_no_next_page(self):
        self.paginator.related_object_fields = ['id', 'name']

        self.paginator.paginate_data(self.related_objects)

        next_link = self.paginator.get_next_link()

        assert next_link is None

    def test_related_object_paginator_get_previous_link(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(3)']

        self.paginator.paginate_data(self.related_objects)

        previous_link = self.paginator.get_previous_link()

        assert previous_link == 'http://testserver/?fields%5Bmodel%5D=id%2Cname%2Cpage_size%282%29%2Cpage%282%29'

    def test_related_object_paginator_get_previous_link_if_there_is_no_previous_page(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)']

        self.paginator.paginate_data(self.related_objects)

        previous_link = self.paginator.get_previous_link()

        assert previous_link is None

    def test_related_object_paginator_get_previous_link_removing_page_number(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(2)']

        self.paginator.paginate_data(self.related_objects)

        previous_link = self.paginator.get_previous_link()

        assert 'page%281%29' not in previous_link

    def test_related_object_paginator_replace_page_method(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(2)']

        query_param = self.paginator.replace_page(5)

        assert 'page(5)' in query_param

    def test_related_object_paginator_replace_page_method_if_page_is_not_in_fields(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)']

        query_param = self.paginator.replace_page(5)

        assert 'page(5)' in query_param

    def test_related_object_paginator_remove_page_method(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(2)']

        query_param = self.paginator.remove_page()

        assert 'page(2)' not in query_param

    def test_related_object_paginator_get_paginated_data(self):
        self.paginator.related_object_fields = ['id', 'name', 'page_size(2)', 'page(2)']

        queryset = self.paginator.paginate_data(self.related_objects)

        paginated_data = self.paginator.get_paginated_data(queryset)

        expected_data = {
            'count': 5,
            'next': 'http://testserver/?fields%5Bmodel%5D=id%2Cname%2Cpage_size%282%29%2Cpage%283%29',
            'previous': 'http://testserver/?fields%5Bmodel%5D=id%2Cname%2Cpage_size%282%29',
            'results': self.related_objects[2:4]
        }

        assert paginated_data == expected_data
