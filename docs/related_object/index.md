# Related Object

Related objects are fields in a model that have a relation with another model, such as ForeignKey, OneToMany or
ManyToMany fields. You can retrieve additional information about these fields by including the related object's name and 
a list of desired  fields. This allows you to "expand" the related object and retrieve more data at once.

## Example

For the purpose of this example, let's assume that you have a model that have all three types of relationships:

1. user, which is a ForeignKey relationship
2. questions, which is an OneToMany relationship
3. friends, which is a ManyToMany relationship

In the model serializer class, the related objects should be declared in the Meta class as a dictionary.

```python title='serializers.py'

from drf_extra_utils.related_object import RelatedObjectMixin


class MyModelSerializer(RelatedObjectMixin, ModelSerializer):
    ...

    class Meta:
        ...
        related_objects = {
            'user': {
                'serializer': UserSerializer
            },
            'questions': {
                'serializer': 'path.to.serializer.QuestionSerializer',
                'many': True
            },
            'friends': {
                'serializer': UserSerializer,
                'many': True
            }
        }
```

!!! note "many"
    It is required to use the many=True argument for fields that have a many-to-many or many-to-one relationship.

!!! note "string import"
    To avoid circular import you can use string reference to the serializer.

!!! warning DynamicFields
    To use the DynamicFieldsMixin in a serializer for related objects, the serializer class must subclass
    DynamicFieldsMixin. Without this mixin, the serializer will not be able to handle fields dynamically.

#### Related Objects Serialization

To use related objects in a serializer, you will need to pass a context parameter to the serializer when calling it.
The context parameter should be a dictionary containing the key 'related_objects' with a value that is another
dictionary. This inner dictionary should have keys that correspond to the names of the related objects you want to 
include, and the values should be lists of field names that you want to include for each related object.

##### Example

```python
context={
    'related_objects': {
        'user': ['@all'], 
        'questions': ['@all'], 
        'friends': ['@all'],
    }
}
serializer = MyModelSerializer(instance, context=context) 
```

##### Result

```json
{
  "id": 1,
  "user": {
    "id": 1,
    "name": "username_1"
  },
  "questions": [
    {
      "id": 1,
      "question": "test_1",
      "is_published": false
    },
    {
      "id": 2,
      "question": "test_2",
      "is_published": true
    }
  ],
  "friends": [
    {
      "id": 2,
      "name": "username_2"
    },
    {
      "id": 3,
      "name": "username_3"
    }
  ]
}
```

### Related Objects Filtering

The related object queryset can be filtered using the filter key in the related object dictionary. The keys of the
dictionary must be strings containing the names of filters, with the corresponding filter values as their
respective dictionary values.

##### Example

```python title='serializers.py'

from drf_extra_utils.related_object import RelatedObjectMixin


class MyModelSerializer(RelatedObjectMixin, ModelSerializer):
    ...

    class Meta:
        ...
        related_objects = {
            ...
        'questions': {
            'serializer': 'path.to.serializer.QuestionSerializer',
            'many': True,
            'filter': {'is_published': True}
            },
        }
```

##### Result

```json
{
  "id": 1,
  "questions": [
    {
      "id": 2,
      "question": "test_2",
      "is_published": true
    }
  ]
}
```

##### Passing additional information on the fly

To pass additional information to the filter on the fly, you can override the get_related_objects method as follows:

```python title="serializers.py"

class MyModelSerializer(RelatedObjectMixin, ModelSerializer):
    ...
    class Meta:
        ...
        related_objects = {
            ...
            'questions': {
                'serializer': 'path.to.serializer.QuestionSerializer',
                'many': True,
                'filter': {'is_published': True}
            },
        }

    def get_related_objects(self):
        related_objects = super().get_related_objects()
        user = getattr(self.context.get('request'), 'user', None)
        if user:
            related_objects['questions']['filter'] = {
                'is_friend': user
            }
        return related_objects
```


### Related Object Permissions

The related objects can have a list of permissions that can be checked to determine if a user has access to the related
object. To use this feature, you will need to set a dictionary key with the permissions as its value, which should be
a list of permissions.

##### Example

```python title='serializers.py'

from drf_extra_utils.related_object import RelatedObjectMixin


class MyModelSerializer(RelatedObjectMixin, ModelSerializer):
    ...

    class Meta:
        ...
        related_objects = {
            ...
        'friends': {
            'serializer': UserSerializer,
            'many': True,
            'permissions': [IsFriend]
        }
        }
```

##### Result

If the user does not have the required permission, they will receive a response indicating that they are not authorized
to access the related object.

```json
{
  "detail": "You do not have permission to access the related object `friends`."
}
```

### Related Object Pagination

To paginate many-to-many and many-to-one related objects, you can pass the page(page number) in the fields parameter.
You can also optionally pass a page_size(page size) parameter  to specify the number of items to include on each page. 
The page size default value is 100.

##### Example

```python
context={
    'related_objects': {
        'friends': ['@all,page(1), page_size(2)'], 
    }
}
serializer = MyModelSerializer(instance, context=context) 
```

##### Result

```json
{
  "id": 1,
  "questions": {
    "count": 10,
    "next": "http://example.com/?fields[friends]=@all,page(2),page_size(2)",
    "previous": null,
    "results": 
        [
          {
            "id": 1,
            "question": "test_1",
            "is_published": true
          },
          {
            "id": 2,
            "question": "test_2",
            "is_published": true
          }
        ]
  }
}
```

### Related Object View

To optimize and simplify the use of related objects in your Django REST framework views, you can use the 
`RelatedObjectViewMixin`.

```python title="views.py"
from drf_extra_utils.related_object import RelatedObjectViewMixin


class MyModelView(RelatedObjectViewMixin, ModelViewSet):
    ...
```

To issue a request to retrieve a related object, you can include a query parameter in the URL of the form 
fields[field_name]=model_fields, where field_name is the name of the related field and model_fields is a list 
of the fields you want to include in the response for the related object.

```
https://example.com/?fields[user]=@all&fields[questions]=@all&fields[friends]=@all
```

!!! note "pagination"
    Pagination also works normally, you just need to use page and page_size in fields as described in the 
    [Related Object Pagination](/related_object/#related-object-pagination) section.