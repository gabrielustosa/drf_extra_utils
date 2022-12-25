from django.core.exceptions import ValidationError
from django.db import models


class OrderedModel(models.Model):
    order_in_respect = None
    order = models.PositiveIntegerField(null=True)

    class Meta:
        abstract = True
        ordering = ('order',)

    def get_queryset(self):
        query = {field: getattr(self, field) for field in self.order_in_respect}
        return self.__class__.objects.filter(**query)

    def get_last_order(self):
        last_order = self.get_queryset().aggregate(ls=models.Max('order'))['ls']
        return last_order

    def get_next_order(self):
        last_order = self.get_last_order()
        return last_order + 1 if last_order is not None else 1

    def do_after_update(self):
        pass

    def do_after_create(self):
        pass

    def save(self, force_insert=False, **kwargs):
        if force_insert:
            self.order = self.get_next_order()

            self.do_after_create()
        else:
            new_order = self.order

            if new_order > self.get_last_order():
                raise ValidationError('The order can not be greater than last order of the object.')

            current_order = self.get_queryset().filter(id=self.id).first().order

            number, query = (1, {'order__gte': new_order, 'order__lte': current_order}) if current_order > new_order \
                else (-1, {'order__lte': new_order, 'order__gte': current_order})

            self.get_queryset().filter(**query).update(
                order=models.ExpressionWrapper(models.F('order') + number, output_field=models.PositiveIntegerField()))

            self.do_after_update()
        super().save(force_insert, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.get_queryset().filter(order__gt=self.order).update(
            order=models.ExpressionWrapper(models.F('order') - 1, output_field=models.PositiveIntegerField()))
        return super().delete(using, keep_parents)
