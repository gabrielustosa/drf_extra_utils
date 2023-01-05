class AnnotationViewMixin:
    """
    Mixin for annotate model annotations to queryset.
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        Serializer = self.get_serializer_class()
        model = Serializer.Meta.model

        annotation_class = getattr(model, 'annotation_class', None)
        if annotation_class:
            annotations = None

            # optimize annotations 
            fields = self.request.query_params.get('fields')
            if fields:
                try:
                    # pass fields to serializer to handle if there are a field type in fields like @min,@default or @all
                    fields = Serializer(fields=fields.split(',')).fields.keys()
                    annotations = annotation_class.get_annotations(*fields)
                except TypeError:
                    # if the serializer don't inherit DynamicModelFieldsMixin
                    pass

            if annotations is None:
                annotations = annotation_class.get_annotations('*')

            queryset = queryset.annotate(**annotations)

        return queryset
