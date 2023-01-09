# Annotation API


### ModelAnnotationHandler

If you want to manage model annotations, you can use the ModelAnnotationHandler class. This class provides the tools and 
methods necessary to handle model annotations.

```.py3
from drf_extra_utils.annotations.handler import ModelAnnotationHandler

handler = ModelAnnotationHandler(model=YourModel)

# retrieve annotations from your model, which can then be used in a queryset
all_annotations = handler.get_annotations('*')
annotations = handler.get_annotations('annotation_field', 'annotation_test') 

# annotating in a queryset
queryset.annotate(**annotations)

# check if model has annotations
if handler.annotations:
    # has annotations

```

### ModelAnnotationFieldHandler

To get the serializer fields for model annotations, you can use the ModelAnnotationFieldHandler class.

```.py3
from drf_extra_utils.annotations.handler import ModelAnnotationFieldHandler

handler = ModelAnnotationFieldHander(model=YourModel)

fields = handler.get_annotation_serializer_fields()

```