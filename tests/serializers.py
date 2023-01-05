from rest_framework.serializers import ModelSerializer

from drf_extra_utils.annotations.serializer import AnnotationFieldMixin
from drf_extra_utils.related_object.serializer import RelatedObjectMixin

from tests import models


class FooSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.FooModel
        fields = '__all__'
        related_objects = {
            'related_foreign': {
                'serializer': f'{__name__}.RelatedForeignSerializer',
                'many': True,
            }
        }


class RelatedForeignSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedForeignModel
        fields = '__all__'
        related_objects = {
            'foo': {
                'serializer': FooSerializer
            },
        }


class RelatedManySerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedManyModel
        fields = '__all__'
        related_objects = {
            'foes': {
                'serializer': FooSerializer,
                'many': True
            }
        }


class M21Serializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.M21Model
        fields = '__all__'


class RelatedMultipleSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedMultipleRelatedModel
        fields = '__all__'
        related_objects = {
            'foo': {
                'serializer': FooSerializer
            },
            'foes': {
                'serializer': FooSerializer,
                'many': True,
            },
            'bars': {
                'serializer': M21Serializer,
                'many': True
            }
        }


# RelatedObject Annotations

class FooAnnotatedSerializer(RelatedObjectMixin, AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = models.FooModelAnnotated
        fields = '__all__'
        related_objects = {
            'related_foreign': {
                'serializer': f'{__name__}.RelatedForeignAnnotationSerializer',
                'many': True,
            }
        }
        min_fields = ('value_1',)
        default_fields = ('my_id',)


class RelatedForeignAnnotationSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedForeignModelAnnotation
        fields = '__all__'
        related_objects = {
            'foo': {
                'serializer': FooAnnotatedSerializer
            },
        }


class RelatedManyAnnotationSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedManyModelAnnotation
        fields = '__all__'
        related_objects = {
            'foes': {
                'serializer': FooAnnotatedSerializer,
                'many': True
            }
        }


class M21AnnotationSerializer(RelatedObjectMixin, AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = models.M21ModelAnnotation
        fields = '__all__'


class RelatedMultipleAnnotationSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.RelatedMultipleRelatedModelAnnotation
        fields = '__all__'
        related_objects = {
            'foo': {
                'serializer': FooAnnotatedSerializer
            },
            'foes': {
                'serializer': FooAnnotatedSerializer,
                'many': True,
            },
            'bars': {
                'serializer': M21AnnotationSerializer,
                'many': True
            }
        }


class BarAnnotationSerializer(RelatedObjectMixin, ModelSerializer):
    class Meta:
        model = models.BarAnnotation
        fields = '__all__'
        related_objects = {
            'bars': {
                'serializer': f'{__name__}.M21BarAnnotationSerializer',
                'many': True
            }
        }


class M21BarAnnotationSerializer(RelatedObjectMixin, AnnotationFieldMixin, ModelSerializer):
    class Meta:
        model = models.M21BarAnnotation
        fields = '__all__'
