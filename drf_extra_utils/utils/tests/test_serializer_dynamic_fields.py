import pytest

from rest_framework.serializers import ModelSerializer

from drf_extra_utils.utils.serializer import DynamicModelFieldsMixin
from drf_extra_utils.utils.tests.models import FooModel


class FooSerializer(DynamicModelFieldsMixin, ModelSerializer):
    class Meta:
        model = FooModel
        fields = ('id', 'bar')
        min_fields = ('id',)
        default_fields = ('bar',)


class FooCustomSerializer(DynamicModelFieldsMixin, ModelSerializer):
    field_types = {'@custom': 'custom_fields', '@test': 'test_fields'}
    all_field_type = '*'

    class Meta:
        model = FooModel
        fields = ('id', 'bar')
        custom_fields = ('id',)
        test_fields = ('bar',)


@pytest.mark.django_db
class TestSerializerDynamicFields:

    def setup_method(self):
        self.foo = FooModel.objects.create(bar='test')

    def test_serializer_dynamic_fields(self):
        serializer = FooSerializer(self.foo, fields=('id',))

        expected_data = {
            'id': self.foo.id
        }

        assert serializer.data == expected_data

    def test_serializer_dynamic_with_invalid_fields(self):
        serializer = FooSerializer(self.foo, fields=('invalid', 'test', 'test_1'))

        expected_data = {}

        assert serializer.data == expected_data

    @pytest.mark.parametrize('field_type,field_name', [
        ('@min', 'min_fields'),
        ('@default', 'default_fields'),
    ])
    def test_serializer_dynamic_field_types(self, field_type, field_name):
        serializer = FooSerializer(self.foo, fields=(field_type,))

        fields = getattr(FooSerializer.Meta, field_name)

        expected_data = {
            field: getattr(self.foo, field)
            for field in fields
        }

        assert serializer.data == expected_data

    def test_serializer_dynamic_all_fields(self):
        serializer = FooSerializer(self.foo, fields=('@all',))

        expected_data = {
            'id': self.foo.id,
            'bar': self.foo.bar
        }

        assert serializer.data == expected_data

    @pytest.mark.parametrize('field_type,field_name', [
        ('@custom', 'custom_fields'),
        ('@test', 'test_fields'),
    ])
    def test_serializer_custom_dynamic_field_types(self, field_type, field_name):
        serializer = FooCustomSerializer(self.foo, fields=(field_type,))

        fields = getattr(FooCustomSerializer.Meta, field_name)

        expected_data = {
            field: getattr(self.foo, field)
            for field in fields
        }

        assert serializer.data == expected_data

    def test_serializer_custom_dynamic_all_fields(self):
        serializer = FooCustomSerializer(self.foo, fields=('*',))

        expected_data = {
            'id': self.foo.id,
            'bar': self.foo.bar
        }

        assert serializer.data == expected_data
