from django.test import TestCase, RequestFactory, override_settings
from django.urls import path

from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from . import serializers

from drf_extra_utils.related_object.views import RelatedObjectViewMixin
from ...utils.tests import models


class FooViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.FooSerializer
    queryset = models.FooModel.objects.all()


class RelatedForeignViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedForeignSerializer
    queryset = models.RelatedForeignModel.objects.all()


class RelatedManyViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedManySerializer
    queryset = models.RelatedManyModel.objects.all()


class RelatedMultipleViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedMultipleSerializer
    queryset = models.RelatedMultipleRelatedModel.objects.all()


factory = RequestFactory()
request = factory.get('/')

urlpatterns = [
    path('foo/<int:pk>/', FooViewSet.as_view({'get': 'retrieve'}), name='foo-retrieve'),
    path('foreign/<int:pk>/', RelatedForeignViewSet.as_view({'get': 'retrieve'}), name='foreign-retrieve'),
    path('many/<int:pk>/', RelatedManyViewSet.as_view({'get': 'retrieve'}), name='many-retrieve'),
    path('multiple/<int:pk>/', RelatedMultipleViewSet.as_view({'get': 'retrieve'}), name='multiple-retrieve'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectView(TestCase):
    def setUp(self):
        self.foo = models.FooModel.objects.create()
        self.foreign_model = models.RelatedForeignModel.objects.create(foo=self.foo)
        self.many_model = models.RelatedManyModel.objects.create()
        self.many_model.foes.add(self.foo)

    def test_related_objects_fields(self):
        view = RelatedForeignViewSet(request=request)
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name', 'fields[test]': 'a,b'}

        assert view.related_objects == {'model_test': ['id', 'name'], 'test': ['a', 'b']}

    def test_fields_in_serializer_context(self):
        view = RelatedForeignViewSet(request=request)
        view.format_kwarg = None
        request.query_params = {'teste': 1, 'new': 2, 'fields[model_test]': 'id,name'}

        assert view.get_serializer_context()['related_objects'] == {'model_test': ['id', 'name']}

    def test_related_object_foreign_serialization(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})

        response = self.client.get(f'{url}?fields[foo]=@all')

        expected_data = {
            'id': self.foreign_model.id,
            'foo': {
                'id': self.foo.id,
                'bar': self.foo.bar
            }
        }

        assert response.data == expected_data

    def test_related_object_many_to_many_serialization(self):
        url = reverse('many-retrieve', kwargs={'pk': self.many_model.id})

        response = self.client.get(f'{url}?fields[foes]=@all')

        expected_data = {
            'id': self.many_model.id,
            'foes': [
                {
                    'id': self.foo.id,
                    'bar': self.foo.bar
                }
            ]
        }

        assert response.data == expected_data

    def test_related_object_many_to_one_serialization(self):
        url = reverse('foo-retrieve', kwargs={'pk': self.foo.id})

        response = self.client.get(f'{url}?fields[related_foreign]=@all')

        expected_data = {
            'id': self.foo.id,
            'bar': self.foo.bar,
            'related_foreign': [
                {
                    'id': self.foreign_model.id,
                    'foo': self.foreign_model.foo.id,
                }
            ]
        }

        assert response.data == expected_data

    def test_multiple_related_objects_serialization(self):
        multiple_model = models.RelatedMultipleRelatedModel.objects.create(foo=self.foo)
        multiple_model.foes.add(self.foo)
        m21_model = models.M21Model.objects.create(multiple_model=multiple_model)

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})
        response = self.client.get(f'{url}?fields[foo]=@all&fields[foes]=@all&fields[bars]=@all')

        expected_data = {
            'id': multiple_model.id,
            'foo': {
                'id': self.foo.id,
                'bar': self.foo.bar
            },
            'foes': [{
                'id': self.foo.id,
                'bar': self.foo.bar,
            }],
            'bars': [{
                'id': m21_model.id,
                'multiple_model': m21_model.multiple_model.id,
            }]
        }

        assert response.data == expected_data

    def test_related_object_many_to_many_pagination(self):
        many_model = models.RelatedManyModel.objects.create()
        foes = [models.FooModel.objects.create(bar='test') for _ in range(5)]
        many_model.foes.add(*foes)

        url = reverse('many-retrieve', kwargs={'pk': many_model.id})
        response = self.client.get(f'{url}?fields[foes]=@all,page_size(1),page(1)')

        expected_data = {
            'id': many_model.id,
            'foes': {
                'count': 5,
                'next': 'http://testserver/many/2/?fields%5Bfoes%5D=%40all%2Cpage_size%281%29%2Cpage%282%29',
                'previous': None,
                'results': [{
                    'id': foes[0].id,
                    'bar': foes[0].bar
                }]
            },
        }

        assert response.data == expected_data

    def test_related_object_many_to_one_pagination(self):
        foo = models.FooModel.objects.create(bar='test')
        foreign_models = [models.RelatedForeignModel.objects.create(foo=foo) for _ in range(5)]

        url = reverse('foo-retrieve', kwargs={'pk': foo.id})
        response = self.client.get(f'{url}?fields[related_foreign]=@all,page_size(1)')

        expected_data = {
            'id': foo.id,
            'bar': foo.bar,
            'related_foreign': {
                'count': 5,
                'next': 'http://testserver/foo/2/?fields%5Brelated_foreign%5D=%40all%2Cpage_size%281%29%2Cpage%282%29',
                'previous': None,
                'results': [{
                    'id': foreign_models[0].id,
                    'foo': foreign_models[0].foo.id,
                }]
            },
        }

        assert response.data == expected_data

    def test_multiple_related_objects_pagination(self):
        multiple_model = models.RelatedMultipleRelatedModel.objects.create(foo=self.foo)
        foes = [models.FooModel.objects.create(bar='test') for _ in range(5)]
        multiple_model.foes.add(*foes)
        m21_models = [models.M21Model.objects.create(multiple_model=multiple_model) for _ in range(5)]

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})
        response = self.client.get(f'{url}?fields[foes]=@all,page_size(1)&fields[bars]=@all,page_size(1)')

        expected_data = {
            'id': multiple_model.id,
            'foo': multiple_model.foo.id,
            'foes': {
                'count': 5,
                'next': 'http://testserver/multiple/1/?fields%5Bbars%5D=%40all%2Cpage_size%281%29&fields%5Bfoes%5D=%40all%2Cpage_size%281%29%2Cpage%282%29',
                'previous': None,
                'results': [{
                    'id': foes[0].id,
                    'bar': foes[0].bar
                }]
            },
            'bars': {
                'count': 5,
                'next': 'http://testserver/multiple/1/?fields%5Bbars%5D=%40all%2Cpage_size%281%29%2Cpage%282%29&fields%5Bfoes%5D=%40all%2Cpage_size%281%29',
                'previous': None,
                'results': [{
                    'id': m21_models[0].id,
                    'multiple_model': m21_models[0].multiple_model.id
                }]
            }
        }

        assert response.data == expected_data

    def test_related_object_foreign_key_optimization(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})

        with self.assertNumQueries(1):
            self.client.get(f'{url}?fields[foo]=@all')

    def test_related_object_many_to_many_optimization(self):
        url = reverse('many-retrieve', kwargs={'pk': self.many_model.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[foes]=@all')

    def test_related_object_many_to_one_optimization(self):
        url = reverse('foo-retrieve', kwargs={'pk': self.foo.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[related_foreign]=@all')

    def test_multiple_related_objects_optimization(self):
        multiple_model = models.RelatedMultipleRelatedModel.objects.create(foo=self.foo)
        multiple_model.foes.add(self.foo)
        models.M21Model.objects.create(multiple_model=multiple_model)

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})

        with self.assertNumQueries(3):
            self.client.get(f'{url}?fields[foo]=@all&fields[foes]=@all&fields[bars]=@all')
