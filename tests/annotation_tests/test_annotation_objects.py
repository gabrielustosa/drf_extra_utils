from unittest.mock import MagicMock

from django.db import models

from drf_extra_utils.annotations import objects


class AnnotationObjectModel:
    pk = 1

    class objects:

        @staticmethod
        def filter(**kwargs):
            return AnnotationObjectModel.objects()

        def annotate(self, **kwargs):
            self.value = dict.fromkeys(kwargs.keys(), 'fetched_value')
            return self

        def first(self):
            instance = AnnotationObjectModel()
            for key, value in self.value.items():
                setattr(instance, key, value)
            return instance


class TestAnnotationObject:

    def setup_method(self):
        self.annotation = objects.Annotation(
            name='test',
            annotation=models.Count('test'),
            model=AnnotationObjectModel
        )
        self.annotation_test_name = '{0}{1}'.format(objects.ANNOTATION_PREFIX, 'test')
        self.annotation_list_test_name = '{0}{1}'.format(objects.ANNOTATION_LIST_PREFIX, 'test')

    def test_annotation_object_annotation_name(self):
        assert self.annotation.annotation_name == self.annotation_test_name

    def test_annotation_object_annotation_name_custom_prefix(self):
        annotation = objects.Annotation(
            name='test',
            annotation=models.Count('test'),
            model=AnnotationObjectModel,
            annotation_prefix=objects.ANNOTATION_LIST_PREFIX
        )

        assert annotation.annotation_name == self.annotation_list_test_name

    def test_annotation_object_get_annotation_expression(self):
        expected_expression = {
            self.annotation_test_name: models.Count('test')
        }

        assert self.annotation.get_annotation_expression() == expected_expression

    def test_annotation_object_get_annotation_value(self):
        instance = MagicMock(**{self.annotation_test_name: 'annotation_value'})
        annotation_value = self.annotation.get_annotation_value(instance)

        assert annotation_value == 'annotation_value'

    def test_annotation_object_get_annotation_value_with_no_value_annotated(self):
        instance = AnnotationObjectModel()
        annotation_value = self.annotation.get_annotation_value(instance)

        assert annotation_value is None

    def test_annotation_object_get_attribute(self):
        instance = MagicMock(**{self.annotation_test_name: 'annotation_value'})
        ret = self.annotation.get_attribute(instance)

        assert ret == 'annotation_value'

    def test_annotation_object_get_attribute_with_fetch(self):
        instance = AnnotationObjectModel()
        ret = self.annotation.get_attribute(instance)

        assert ret == 'fetched_value'


class TestAnnotationListObject:

    def setup_method(self):
        self.annotation = objects.AnnotationList(
            annotations={
                'list_1': models.Count('list_1'),
                'list_2': models.Count('list_2')
            },
            model=AnnotationObjectModel
        )
        self.annotation_list_1_name = '{0}{1}'.format(objects.ANNOTATION_LIST_PREFIX, 'list_1')
        self.annotation_list_2_name = '{0}{1}'.format(objects.ANNOTATION_LIST_PREFIX, 'list_2')

    def test_annotation_object_list_children(self):
        for child in self.annotation.children:
            assert isinstance(child, objects.Annotation)
            assert child.annotation_prefix == objects.ANNOTATION_LIST_PREFIX

    def test_annotation_object_list_get_annotation_expression(self):
        annotation_expression = self.annotation.get_annotation_expression()

        expected_annotation_expression = {
            self.annotation_list_1_name: models.Count('list_1'),
            self.annotation_list_2_name: models.Count('list_2'),
        }

        assert annotation_expression == expected_annotation_expression

    def test_annotation_object_list_get_annotation_value(self):
        instance = MagicMock(**{self.annotation_list_1_name: 1, self.annotation_list_2_name: 2})
        annotation_value = self.annotation.get_annotation_value(instance)

        expected_value = {
            'list_1': 1,
            'list_2': 2,
        }

        assert annotation_value == expected_value

    def test_annotation_object_list_get_annotation_value_with_no_value_annotated(self):
        instance = AnnotationObjectModel()
        annotation_value = self.annotation.get_annotation_value(instance)

        expected_value = {
            'list_1': None,
            'list_2': None,
        }

        assert annotation_value == expected_value

    def test_annotation_object_list_get_attribute(self):
        instance = MagicMock(**{self.annotation_list_1_name: 1, self.annotation_list_2_name: 2})
        ret = self.annotation.get_attribute(instance)

        expected_ret = {
            'list_1': 1,
            'list_2': 2,
        }

        assert ret == expected_ret

    def test_annotation_object_list_get_attribute_with_fetch(self):
        instance = AnnotationObjectModel()
        ret = self.annotation.get_attribute(instance)

        expected_value = {
            'list_1': 'fetched_value',
            'list_2': 'fetched_value',
        }

        assert ret == expected_value
