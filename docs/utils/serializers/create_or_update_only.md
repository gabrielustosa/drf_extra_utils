# Create or Update Only

The CreateOrUpdateOnlyMixin class is a mixin for Django REST framework's ModelSerializer that allows fields to be 
sent only in create methods or fields that can only be sent in update methods.

## Example

```python
from drf_extra_utils.serializers import CreateOrUpdateOnlyMixin


class MySerializer(CreateOrUpdateOnlyMixin, ModelSerializer):
    class Meta:
        model = MyModel
        create_only_fields = ('name', 'num')
        update_only_fields = ('title', 'description')
```

This will allow the name and num fields to be sent only in create methods, and the title and description fields to be 
sent only in update methods. Any attempt to send these fields in incorrect contexts will be ignored.