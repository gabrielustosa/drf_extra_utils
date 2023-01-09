from django.db import models


# CreateUpdateOnly Model

class BarModel(models.Model):
    foo = models.CharField(max_length=100)
    bar = models.IntegerField(null=True, default=0)
