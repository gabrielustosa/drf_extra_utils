from drf_extra_utils.annotations.decorator import model_annotation
from drf_extra_utils.annotations.objects import ANNOTATION_PREFIX, ANNOTATION_LIST_PREFIX


class Test:
    pk = 1

    @model_annotation
    def annotation_func(self):
        return 'test_value'

    @model_annotation
    def annotation_list(self):
        return {
            'list_1': 1,
            'list_2': 2
        }

    class objects:

        @staticmethod
        def filter(**kwargs):
            return Test.objects()

        def annotate(self, **kwargs):
            self.value = dict.fromkeys(kwargs.keys(), 'fetched_value')
            return self

        def first(self):
            instance = Test()
            for key, value in self.value.items():
                setattr(instance, key, value)
            return instance


annotation_func_name = '{0}{1}'.format(ANNOTATION_PREFIX, 'annotation_func')
annotation_list_1_name = '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_1')
annotation_list_2_name = '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_2')


def test_model_annotation_function():
    @model_annotation
    def annotation_func():
        return 'test_value'

    assert annotation_func.func() == 'test_value'


def test_model_annotation_name():
    @model_annotation
    def annotation_func():
        return 'test_value'

    annotation_func.__set_name__(None, 'annotation_func')

    assert annotation_func.name == 'annotation_func'


def test_model_annotation_expression():
    annotation = Test.annotation_func

    expected_annotation = {
        annotation_func_name: 'test_value'
    }

    assert annotation == expected_annotation


def test_model_annotation_list_expression():
    annotation_list = Test.annotation_list

    expected_annotation = {
        annotation_list_1_name: 1,
        annotation_list_2_name: 2
    }

    assert annotation_list == expected_annotation


def test_model_annotation_representation():
    instance = Test()
    setattr(instance, '{0}{1}'.format(ANNOTATION_PREFIX, 'annotation_func'), 'value')

    annotation = instance.annotation_func

    assert annotation == 'value'


def test_model_annotation_list_representation():
    instance = Test()
    setattr(instance, '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_1'), 'value_1')
    setattr(instance, '{0}{1}'.format(ANNOTATION_LIST_PREFIX, 'list_2'), 'value_2')

    annotation = instance.annotation_list

    expected_annotation = {
        'list_1': 'value_1',
        'list_2': 'value_2',
    }

    assert annotation == expected_annotation


def test_model_annotation_representation_fetch():
    instance = Test()

    annotation = instance.annotation_func

    assert annotation == 'fetched_value'


def test_model_annotation_list_representation_fetch():
    instance = Test()

    annotation = instance.annotation_list

    expected_annotation = {
        'list_1': 'fetched_value',
        'list_2': 'fetched_value',
    }

    assert annotation == expected_annotation
