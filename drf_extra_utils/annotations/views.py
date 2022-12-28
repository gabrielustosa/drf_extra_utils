class AnnotationViewMixin:
    """
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer = self.get_serializer_class()
        model = serializer.Meta.model

        annotation_class = getattr(model, 'annotation_class', None)
        if annotation_class:
            annotations = None

            fields = self.request.query_params.get('fields')
            if fields:
                try:
                    # TODO ADD CUSTOM FIELDS TO SERIALIZER AND TEST
                    fields = serializer(fields=fields.split(',')).fields.keys()
                    annotations = annotation_class.get_annotations(*fields)
                except TypeError:
                    pass

            if annotations is None:
                annotations = annotation_class.get_annotations('*')

            queryset = queryset.annotate(**annotations)

        return queryset
