from unittest.mock import patch

from django.test import TestCase, RequestFactory

from rest_framework.serializers import ModelSerializer

from drf_extra_utils.related_object.serializer import RelatedObjectMixin
from ...utils.tests import models
from drf_extra_utils.utils.tests.models import RelatedManyModel, FooModel

from .serializers import FooSerializer


class RelatedManySerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedManyModel
        fields = '__all__'
        related_objects = {
            'foes': {
                'serializer': FooSerializer,
                'many': True,
                'filter': {'bar__startswith': 'test'}
            }
        }


factory = RequestFactory()
request = factory.get('/')


class TestRelatedObjectFilter(TestCase):
    def test_related_object_filter_kwargs(self):
        serializer = RelatedManySerializer(context={'related_objects': {'foes': ['@all']}})
        filter_kwargs = serializer._get_related_object_option('foes', 'filter')

        assert filter_kwargs == {'bar__startswith': 'test'}

    def test_get_related_object_filtered(self):
        many_model = RelatedManyModel.objects.create()
        test_1 = FooModel.objects.create(bar='test_1')
        test_2 = FooModel.objects.create(bar='test_2')
        test_3 = FooModel.objects.create(bar='test_3')
        many_model.foes.add(test_1, test_2, test_3)
        many_model.foes.add(*[FooModel.objects.create(bar='ta') for _ in range(5)])

        serializer = RelatedManySerializer(many_model, context={'related_objects': {'foes': ['id']}})

        expected_data = {
            'id': many_model.id,
            'foes': [
                {
                    'id': test_1.id,
                },
                {
                    'id': test_2.id,
                },
                {
                    'id': test_3.id,
                },
            ]
        }

        assert serializer.data == expected_data

    def test_get_related_object_filtering_without_matching(self):
        many_model = RelatedManyModel.objects.create()
        many_model.foes.add(*[FooModel.objects.create(bar=f'tata-{n}') for n in range(5)])

        serializer = RelatedManySerializer(many_model, context={'related_objects': {'foes': ['@all']}})

        expected_data = {
            'id': many_model.id,
            'foes': []
        }

        assert serializer.data == expected_data

    @patch('drf_extra_utils.related_object.paginator.RELATED_OBJECT_PAGINATED_BY', 1)
    def test_get_related_object_pagination_is_filtering(self):
        many_model = RelatedManyModel.objects.create()
        test_1 = FooModel.objects.create(bar='test_1')
        test_2 = FooModel.objects.create(bar='test_2')
        test_3 = FooModel.objects.create(bar='test_3')
        many_model.foes.add(*[FooModel.objects.create(bar='ta') for _ in range(5)])
        many_model.foes.add(test_1, test_2, test_3)

        context = {'request': request, 'related_objects': {'foes': ['id']}}
        serializer = RelatedManySerializer(many_model, context=context)

        foes = serializer.data['foes']['results']

        expected_data = [
            {
                'id': test_1.id
            }
        ]

        assert foes == expected_data

    @patch('drf_extra_utils.related_object.paginator.RELATED_OBJECT_PAGINATED_BY', 1)
    def test_get_related_objet_pagination_filtering_without_matching(self):
        many_model = RelatedManyModel.objects.create()
        many_model.foes.add(*[FooModel.objects.create(bar=f'tata-{n}') for n in range(5)])

        context = {'request': request, 'related_objects': {'foes': ['id']}}
        serializer = RelatedManySerializer(many_model, context=context)

        expected_data = {
            'id': many_model.id,
            'foes': []
        }

        assert serializer.data == expected_data
