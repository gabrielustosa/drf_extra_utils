class AnnotationFieldMixin:
    """
    A mixin that allows adding fields to the serializer based on annotations defined in a model's annotation_class.
    """

    def get_fields(self):
        fields = super().get_fields()

        annotation_class = getattr(self.Meta.model, 'annotation_class', None)
        if annotation_class:
            fields.update(annotation_class.get_annotation_serializer_fields())

        return fields
