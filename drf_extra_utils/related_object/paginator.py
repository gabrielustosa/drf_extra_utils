import re

from collections import OrderedDict
from dataclasses import dataclass
from typing import List

from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.utils.urls import replace_query_param

from django.core.paginator import Paginator, InvalidPage
from django.utils.functional import cached_property

RELATED_OBJECT_PAGINATED_BY = 100


@dataclass
class RelatedObjectPaginator:
    """
    Paginator for related objects.
    """

    related_object_name: str
    related_object_fields: List[str]
    request: Request

    def paginate_data(self, data):
        if int(self.page_size) <= 0:
            raise NotFound(f'Invalid page size for `{self.related_object_name}`.')

        self.paginator = Paginator(data, self.page_size)

        try:
            self.page = self.paginator.page(self.page_number)
        except InvalidPage:
            raise NotFound(f'Invalid page for `{self.related_object_name}`.')

        return list(self.page)

    @property
    def num_pages(self):
        return self.paginator.num_pages

    @cached_property
    def page_number(self):
        """
        Return a page number which is in related objects fields list.

        example:
            ['id', 'title', 'page(3)'] - it'll return 3.
            ['id', 'title'] - it'll return 1.
        """
        pattern = re.compile(r'page\(([0-9_]+)\)')
        for field_name in self.related_object_fields:
            match = pattern.match(field_name)
            if match:
                return match.group(1)
        return 1

    @cached_property
    def page_size(self):
        """
        Return a page size number which is in related objects fields list.

        example:
            ['id', 'title', 'page_size(50)'] - it'll return 50.
            ['id', 'title'] - it'll return the default RELATED_OBJECT_PAGINATED_BY value.
        """
        pattern = re.compile(r'page_size\(([0-9_]+)\)')
        for field_name in self.related_object_fields:
            match = pattern.match(field_name)
            if match:
                return match.group(1)
        return RELATED_OBJECT_PAGINATED_BY

    @property
    def field_param(self):
        return f'fields[{self.related_object_name}]'

    def get_page_param(self, page_number):
        return f'page({page_number})'

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.field_param, self.replace_page_param(page_number))

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return replace_query_param(url, self.field_param, self.remove_page_param())
        return replace_query_param(url, self.field_param, self.replace_page_param(page_number))

    def replace_page_param(self, page):
        """
        Replace url query page param.

        example:
            replace_page_param(4) -> https://example/?fields[model]=@all,page(3)
            result -> https://example/?fields[model]=@all,page(4)
        """
        if self.get_page_param(self.page_number) not in self.related_object_fields:
            self.related_object_fields.append(self.get_page_param(self.page_number))
        query_fields = ','.join(self.related_object_fields)
        return query_fields.replace(self.get_page_param(self.page_number), self.get_page_param(page))

    def remove_page_param(self):
        """
        Remove url query page param
        example:
            remove_page_param() -> https://example/?fields[model]=@all,page(3)
            result -> https://example/?fields[model]=@all
        """
        fields_list = [field for field in self.related_object_fields if field != self.get_page_param(self.page_number)]
        return ','.join(fields_list)

    def get_paginated_data(self, data):
        return OrderedDict([
            ('count', self.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])
