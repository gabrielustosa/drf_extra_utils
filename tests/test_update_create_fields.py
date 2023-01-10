from django.test import TestCase

from rest_framework.serializers import ModelSerializer

from drf_extra_utils.serializers import CreateOrUpdateOnlyMixin

from tests.models import BarModel


class CreateOnlySerializer(CreateOrUpdateOnlyMixin, ModelSerializer):
    class Meta:
        model = BarModel
        fields = '__all__'
        create_only_fields = ('bar',)


class UpdateOnlySerializer(CreateOrUpdateOnlyMixin, ModelSerializer):
    class Meta:
        model = BarModel
        fields = '__all__'
        update_only_fields = ('bar',)


class TestCreateOnlyFields(TestCase):

    def setUp(self):
        self.bar = BarModel.objects.create(foo='test')

    def test_create_only_model(self):
        data = {'foo': 'new foo', 'bar': 8}
        serializer = CreateOnlySerializer(data=data)
        serializer.is_valid()
        model = serializer.save()

        assert model.foo == data['foo']
        assert model.bar == data['bar']

    def test_create_only_attribute_are_not_defined(self):
        data = {'foo': 'new foo', 'bar': 8}
        serializer = CreateOnlySerializer(self.bar, data=data)
        serializer.is_valid()
        model = serializer.save()

        assert model.foo == data['foo']
        assert model.bar == 0

    def test_create_only_fields_internal_value(self):
        data = {'foo': 'new foo', 'bar': 8}

        ret = CreateOnlySerializer(self.bar, ).to_internal_value(data)

        assert ret == {'foo': 'new foo'}

    def test_create_only_fields_are_setting_to_required_false(self):
        extra_kwargs = CreateOnlySerializer(self.bar, ).get_extra_kwargs()

        assert extra_kwargs == {'bar': {'required': False}}


class TestUpdateOnlyFields(TestCase):

    def test_update_only_model(self):
        data = {'foo': 'new foo', 'bar': 8}
        bar = BarModel.objects.create(foo='test')
        serializer = UpdateOnlySerializer(bar, data=data)
        serializer.is_valid()
        model = serializer.save()

        assert model.foo == data['foo']
        assert model.bar == data['bar']

    def test_update_only_attribute_are_not_defined(self):
        data = {'foo': 'new foo', 'bar': 8}
        serializer = UpdateOnlySerializer(data=data)
        serializer.is_valid()
        model = serializer.save()

        assert model.foo == data['foo']
        assert model.bar == 0

    def test_update_only_fields_internal_value(self):
        data = {'foo': 'new foo', 'bar': 8}

        ret = UpdateOnlySerializer().to_internal_value(data)

        assert ret == {'foo': 'new foo'}
