from django.test import TestCase, override_settings
from django.urls import path
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from ...utils.tests import models
from drf_extra_utils.related_object.views import RelatedObjectViewMixin

from . import serializers


class TestRelatedObjectAnnotationsMixin:
    def test_get_related_object_annotation(self):
        context = {'related_objects': {'foo': ['id', 'value_1', 'my_id']}}
        serializer = serializers.RelatedForeignAnnotationSerializer(context=context)

        annotations = serializer.get_related_object_annotations('foo')

        expected_annotations = ['value_1', 'my_id']

        for annotation in expected_annotations:
            assert annotation in annotations

    def test_get_related_object_annotation_class(self):
        context = {'related_objects': {'foo': ['id', 'value_1', 'my_id']}}
        serializer = serializers.RelatedForeignAnnotationSerializer(context=context)

        annotation_class = serializer.get_related_object_annotation_class('foo')

        assert annotation_class == models.FooModelAnnotated.annotation_class


class RelatedForeignViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedForeignAnnotationSerializer
    queryset = models.RelatedForeignModelAnnotation.objects.all()


class RelatedManyViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedManyAnnotationSerializer
    queryset = models.RelatedManyModelAnnotation.objects.all()


class RelatedMultipleViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.RelatedMultipleAnnotationSerializer
    queryset = models.RelatedMultipleRelatedModelAnnotation.objects.all()


class BarViewSet(RelatedObjectViewMixin, ModelViewSet):
    serializer_class = serializers.BarAnnotationSerializer
    queryset = models.BarAnnotation.objects.all()


urlpatterns = [
    path('foreign/<int:pk>/', RelatedForeignViewSet.as_view({'get': 'retrieve'}), name='foreign-retrieve'),
    path('many/<int:pk>/', RelatedManyViewSet.as_view({'get': 'retrieve'}), name='many-retrieve'),
    path('multiple/<int:pk>/', RelatedMultipleViewSet.as_view({'get': 'retrieve'}), name='multiple-retrieve'),
    path('bar/<int:pk>/', BarViewSet.as_view({'get': 'retrieve'}), name='bar-retrieve'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestRelatedObjectAnnotations(TestCase):

    def setUp(self):
        self.foo = models.FooModelAnnotated.objects.create()
        self.foreign_model = models.RelatedForeignModelAnnotation.objects.create(foo=self.foo)
        self.many_model = models.RelatedManyModelAnnotation.objects.create()
        self.many_model.foes.add(self.foo)

    def test_related_object_foreign_annotation_serialization(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})

        response = self.client.get(f'{url}?fields[foo]=@all')

        expected_data = {
            'id': self.foreign_model.id,
            'foo': {
                'id': self.foo.id,
                'value_1': 'value_1',
                'my_id': f'my id is: {self.foo.id}'
            }
        }

        assert response.data == expected_data

    def test_related_object_annotation_many_to_many_serialization(self):
        url = reverse('many-retrieve', kwargs={'pk': self.many_model.id})

        response = self.client.get(f'{url}?fields[foes]=@all')

        expected_data = {
            'id': self.many_model.id,
            'foes': [
                {
                    'id': self.foo.id,
                    'value_1': 'value_1',
                    'my_id': f'my id is: {self.foo.id}'
                }
            ]
        }

        assert response.data == expected_data

    def test_related_object_annotation_many_to_one_serialization(self):
        bar = models.BarAnnotation.objects.create()
        m21 = models.M21BarAnnotation.objects.create(bar=bar)

        url = reverse('bar-retrieve', kwargs={'pk': bar.id})
        response = self.client.get(f'{url}?fields[bars]=id,value_1,my_id')

        expected_data = {
            'id': bar.id,
            'bars': [
                {
                    'id': m21.id,
                    'value_1': 'value_1',
                    'my_id': f'my id is: {m21.id}'
                }
            ]
        }

        assert response.data == expected_data

    def test_multiple_related_annotation_objects_serialization(self):
        multiple_model = models.RelatedMultipleRelatedModelAnnotation.objects.create(foo=self.foo)
        multiple_model.foes.add(self.foo)
        m21_model = models.M21ModelAnnotation.objects.create(multiple_model=multiple_model)

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})
        response = self.client.get(f'{url}?fields[foo]=@all&fields[foes]=@all&fields[bars]=id,value_1,my_id')

        expected_data = {
            'id': multiple_model.id,
            'foo': {
                'id': self.foo.id,
                'value_1': 'value_1',
                'my_id': f'my id is: {self.foo.id}'
            },
            'foes': [{
                'id': self.foo.id,
                'value_1': 'value_1',
                'my_id': f'my id is: {self.foo.id}'
            }],
            'bars': [{
                'id': m21_model.id,
                'value_1': 'value_1',
                'my_id': f'my id is: {m21_model.id}'
            }]
        }

        assert response.data == expected_data

    def test_related_object_many_to_many_annotation_pagination(self):
        many_model = models.RelatedManyModelAnnotation.objects.create()
        foes = [models.FooModelAnnotated.objects.create() for _ in range(5)]
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
                    'value_1': 'value_1',
                    'my_id': f'my id is: {foes[0].id}'
                }]
            },
        }

        assert response.data == expected_data

    def test_related_object_many_to_one_annotation_pagination(self):
        bar = models.BarAnnotation.objects.create()
        m21_models = [models.M21BarAnnotation.objects.create(bar=bar) for _ in range(5)]

        url = reverse('bar-retrieve', kwargs={'pk': bar.id})
        response = self.client.get(f'{url}?fields[bars]=id,value_1,my_id,page_size(1)')

        expected_data = {
            'id': bar.id,
            'bars': {
                'count': 5,
                'next': 'http://testserver/bar/1/?fields%5Bbars%5D=id%2Cvalue_1%2Cmy_id%2Cpage_size%281%29%2Cpage%282%29',
                'previous': None,
                'results': [{
                    'id': m21_models[0].id,
                    'value_1': 'value_1',
                    'my_id': f'my id is: {m21_models[0].id}'
                }]
            },
        }

        assert response.data == expected_data

    def test_multiple_related_objects_annotation_pagination(self):
        multiple_model = models.RelatedMultipleRelatedModelAnnotation.objects.create(foo=self.foo)
        foes = [models.FooModelAnnotated.objects.create() for _ in range(5)]
        multiple_model.foes.add(*foes)
        m21_models = [models.M21ModelAnnotation.objects.create(multiple_model=multiple_model) for _ in range(5)]

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})
        response = self.client.get(f'{url}?fields[foes]=@all,page_size(1)&fields[bars]=id,value_1,my_id,page_size(1)')

        expected_data = {
            'id': multiple_model.id,
            'foo': multiple_model.foo.id,
            'foes': {
                'count': 5,
                'next': 'http://testserver/multiple/1/?fields%5Bbars%5D=id%2Cvalue_1%2Cmy_id%2Cpage_size%281%29&fields%5Bfoes%5D=%40all%2Cpage_size%281%29%2Cpage%282%29',
                'previous': None,
                'results': [{
                    'id': foes[0].id,
                    'value_1': 'value_1',
                    'my_id': f'my id is: {foes[0].id}'
                }]
            },
            'bars': {
                'count': 5,
                'next': 'http://testserver/multiple/1/?fields%5Bbars%5D=id%2Cvalue_1%2Cmy_id%2Cpage_size%281%29%2Cpage%282%29&fields%5Bfoes%5D=%40all%2Cpage_size%281%29',
                'previous': None,
                'results': [{
                    'id': m21_models[0].id,
                    'value_1': 'value_1',
                    'my_id': f'my id is: {m21_models[0].id}'
                }]
            }
        }

        assert response.data == expected_data

    def test_related_object_foreign_annotation_key_optimization(self):
        url = reverse('foreign-retrieve', kwargs={'pk': self.foreign_model.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[foo]=@all')

    def test_related_object_many_to_many_annotation_optimization(self):
        url = reverse('many-retrieve', kwargs={'pk': self.many_model.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[foes]=@all')

    def test_related_object_many_to_one_annotation_optimization(self):
        bar = models.BarAnnotation.objects.create()
        models.M21BarAnnotation.objects.create(bar=bar)

        url = reverse('bar-retrieve', kwargs={'pk': bar.id})

        with self.assertNumQueries(2):
            self.client.get(f'{url}?fields[bars]=@all')

    def test_multiple_related_objects_annotation_optimization(self):
        multiple_model = models.RelatedMultipleRelatedModelAnnotation.objects.create(foo=self.foo)
        multiple_model.foes.add(self.foo)
        models.M21ModelAnnotation.objects.create(multiple_model=multiple_model)

        url = reverse('multiple-retrieve', kwargs={'pk': multiple_model.id})

        with self.assertNumQueries(4):
            self.client.get(f'{url}?fields[foo]=@all&fields[foes]=@all&fields[bars]=@all')
