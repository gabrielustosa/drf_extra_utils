# Dynamic Fields

Dynamic fields are fields that can be displayed or hidden in an object serialization based on the user's choice. This 
is useful in situations where the user may want to only display relevant fields , rather than displaying all available
fields on an object.

## Dynamic Serializer Fields

A mixin for ModelSerializer that takes an additional fields argument that controls which fields should be displayed.

### Example 


```python
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin


class Serializer(DynamicModelFieldsMixin, ModelSerializer):
    ...

serializer = Serializer(instance, fields=['test', 'id'])
```

#### Field Mapping

The field mapping is a dictionary that maps field types to attribute names in the serializer's Meta class. The keys are 
the symbol that will be in the fields query parameter, and the values are the field names defined in the serializer's 
Meta.

The default field mapping are:

* @min - min_fields
* @default - default_fields

You can modify this field mapping as you want.

##### Example

```python
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin

class Serializer(DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        ...
        min_fields = ('id', 'name', 'test')
        default_fields = ('title', 'name', 'url')

# the same effect as specifying fields=['id', 'name', 'test']  
serializer = Serializer(instance, fields=['@min'])
```

##### Modifying field mapping

```python
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin

class Serializer(DynamicModelFieldsMixin, ModelSerializer):
    field_type_mapping = {'@self', 'self_fields'}
    class Meta:
        ...
        self_fields = ('id', 'name', 'test')

# the same effect as specifying fields=['id', 'name', 'test']  
serializer = Serializer(instance, fields=['@self'])
```

#### All Fields

If you want to return all fields of the model in the object serialization, you can use the @all symbol in the fields 
argument when instantiating the serializer. This will include all fields of the model in the serialized output. You can
modify this field symbol.

```python
from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin

# default 
class Serializer(DynamicModelFieldsMixin, ModelSerializer):
    ...

serializer = Serializer(instance, fields=['@all'])

class StarSymbolSerializer(DynamicModelFieldsMixin, ModelSerializer):
    all_symbol = '*'
    
serializer = StarSymbolSerializer(instance, fields=['*'])
```

## Dynamic View fields

To add dynamic fields to a Django REST framework view for a model, you can use the DynamicFieldsViewMixin mixin.

```python
from drf_extra_utils.views import DynamicFieldsViewMixin


class ModelView(DynamicFieldsViewMixin, ModelViewSet):
    ...
```