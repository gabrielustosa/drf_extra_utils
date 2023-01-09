# Annotation

An annotation is a field that is not stored in the database, but rather is calculated or derived from other
fields in the model. These fields can be useful for adding additional information to a model without the need
to store it in the database.

The annotation value will be annotated in instance queryset otherwise calculated on the fly by the ORM.

There are two types of annotations available: default annotations and list annotations. Default annotations represent a
single annotation, while list annotations represent a collection of annotations. 

To create a default annotation, you can define a function that returns a simple django function annotation. To create a 
list annotation, you can define a function that returns a dictionary of django function annotations.

## Example

Imagine you have two models in your django application.

```.py3
from django.db import models

class Project(models.Model):
    status = models.CharField(max_length=10)
    created = models.DateTime()

class User(models.Model):
    projects = models.ManyToMany(Project)
```

Let's create a few annotations for this model.

```.py3 title='models.py'
from drf_extra_utils.annotations.decorator import model_annotation
from drf_extra_utils.utils.middleware import get_current_user

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models

class User(models.Model):
    ...
    
    @model_annotation
    def projects_count(self):
        return models.Count('projects')
     
    @model_annotation
    def projects_status_count(self):
        return {
            option: models.Count('projects', filter=models.Q(status=option))
            for option in ('done', 'in_progress', 'canceled')
        }
       
    @model_annotation
    def in_progress_projects_id(self):
        return ArrayAgg('projects__id', filter=models.Q(status='in_progress'))
    
    @model_annotation 
    def last_project_id(self):
        user = get_current_user()
        user_projects = user.projects.all()
        
        return models.Subquery(
            user_projects.order_by('-created').values('id')[:1]
        )
```

Now, four annotations have been defined for the User model:

1. The total number of projects belonging to a user.
2. An annotation list showing the count of projects with each status for the user.
3. A list of projects currently in progress for the user.
4. The most recent project belonging to the user.

!!! note "self"
    Do not use self in annotation functions. Instead, use models.OuterRef to reference instance attributes.

!!! note "get_current_user"
    The get_current_user only works if you are using it in your middlewares.

!!! danger "optimization"
    To avoid unnecessary queries and improve the performance ensure that all annotations of your model are fetched in a 
    single query, otherwise it'll issue a separate query for each annotation. To include annotations for your model in 
    a queryset, you can use the [ModelAnnotationHandler](/annotation/annotation_api/#modelannotationhandler) class,
    or you can use the [AnnotationViewMixin](/annotation/#using-annotation-view-mixin) in your Django REST
    views for automatic query optimization

### AnnotationSerializerMixin

To activate the annotations in your serializer you'll need to apply the ``AnnotationSerializerMixin`` to your model
serializer.

```.py3 title="serializers.py"
from drf_extra_utils.annotations.serializer import AnnotationSerializerMixin

class UserSerializer(AnnotationSerializerMixin, ModelSerializer):
    ...
```

##### Result

```json
{
  "id": 1,
  "projects_count": 11,
  "projects_status_count": {
    "done": 5,
    "in_progress": 5,
    "canceled": 1
  },
  "in_progress_projects_id": [
    54,
    10,
    887,
    51,
    36
  ],
  "last_project_id": 36
}
```

### AnnotationViewMixin

To annotate and optimize these model annotations to the model queryset you'll need to apply the ``AnnotationViewMixin`` 
to your model view.

```.py3 title="views.py"
from drf_extra_utils.annotations.view import AnnotationViewMixin

class UserView(AnnotationViewMixin, APIView):
    ...
```



