import inspect

from collections import ChainMap, OrderedDict

from rest_framework.serializers import ModelSerializer, ReadOnlyField

from drf_extra_utils.annotations.fields import AnnotationDictField, AnnotationField


def _get_rest_field_by_annotation(annotation):
    try:
        return ModelSerializer.serializer_field_mapping[annotation.output_field.__class__]()
    except (AttributeError, KeyError):
        return ReadOnlyField()


class AnnotationBase:
    def get_annotation_serializer_fields(self):
        annotation_fields = OrderedDict()

        for annotation_name in self.annotation_fields:
            annotation_fields[annotation_name] = self.get_annotation_serializer_field(annotation_name)

        return annotation_fields

    def get_annotation_serializer_field(self, annotation_name):
        annotation = self.get_annotation_value(annotation_name)

        if isinstance(annotation, dict):
            return AnnotationDictField(children=[
                AnnotationField(
                    annotation_name=annotation_name,
                    child=_get_rest_field_by_annotation(annotation)
                )
                for annotation_name, annotation in annotation.items()
            ])

        return AnnotationField(annotation_name=annotation_name, child=_get_rest_field_by_annotation(annotation))

    def get_annotation_value(self, annotation_name):
        annotation = getattr(self, annotation_name, None)

        if annotation is None:
            return None

        return annotation()

    def get_annotation(self, annotation_name):
        annotation_value = self.get_annotation_value(annotation_name)

        if isinstance(annotation_value, dict):
            return annotation_value

        return {annotation_name: annotation_value}

    def get_annotations(self, *fields):
        fields = self.intersection_fields(fields)

        annotations_list = [self.get_annotation(field) for field in fields]
        return ChainMap(*annotations_list)

    def intersection_fields(self, fields):
        if '@all' in fields or '*' in fields:
            return self.annotation_fields

        return set(self.annotation_fields).intersection(fields)

    @property
    def annotation_fields(self):
        return (
            name
            for klass in [klass for klass in self.__class__.mro() if klass != AnnotationBase]
            for name, attr in vars(klass).items() if inspect.isfunction(attr)
        )
