from django.db import models
from django.db.models.functions import Concat

from drf_extra_utils.annotations.base import AnnotationBase


class TestAnnotations(AnnotationBase):
    def count_foo(self):
        return models.Count('foo', distinct=True)

    def complex_foo(self):
        return models.Sum(
            models.Case(
                models.When(
                    foo__bar='test_1', then=models.Value(1),
                ),
                models.When(
                    foo__bar='test_2', then=models.Value(2),
                ),
                models.When(
                    foo__bar='test_3', then=models.Value(3),
                ),
                default=models.Value(0),
                output_field=models.SmallIntegerField()
            ), default=0, output_field=models.PositiveIntegerField()
        )

    def list_foo(self):
        return {
            option: models.Count('foo__id', filter=models.Q(foo__bar=option))
            for option in ('test_1', 'test_2', 'test_3')
        }


class RelatedObjectAnnotations(AnnotationBase):
    def value_1(self):
        return models.Value('value_1', output_field=models.CharField())

    def my_id(self):
        return Concat(models.Value('my id is: '), models.F('id'), output_field=models.CharField())