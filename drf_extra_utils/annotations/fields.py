from rest_framework import serializers


class AnnotationDictField(serializers.Field):
    """
    AnnotationDictField is a field  to handle a list of annotations in a serializer. It allows you to specify
    which annotations should be included in the serialized representation of a model instance and how they
    should be represented.

    * Children of this field must be AnnotationField
    """

    def __init__(self, *args, **kwargs):
        self.children = kwargs.pop('children')
        kwargs['read_only'] = True

        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return {
            child.annotation_name: child.get_attribute(instance)
            for child in self.children
        }

    def to_representation(self, value):
        return {
            key: child.to_representation(val) if val is not None else None
            for child in self.children
            for key, val in value.items()
        }


class AnnotationField(serializers.Field):
    """
     It's used to represent a specific field in a Django model that has been annotated with an additional value.
     This field can be used in a serializer to return the annotated value along with the other fields of the model.
    """

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child')
        self.annotation_name = kwargs.pop('annotation_name', None)
        kwargs['read_only'] = True

        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return getattr(instance, self.annotation_name, None)

    def to_representation(self, value):
        return self.child.to_representation(value)
