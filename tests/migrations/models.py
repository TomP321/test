try:
    from psycopg2.extras import DateTimeTZRange
    from django.contrib.postgres.fields import DateTimeRangeField
except ImportError:
    pass  # psycopg2 isn't installed.

from django.apps.registry import Apps
from django.db import models


class CustomModelBase(models.base.ModelBase):
    pass


class ModelWithCustomBase(models.Model, metaclass=CustomModelBase):
    pass


class UnicodeModel(models.Model):
    title = models.CharField('ÚÑÍ¢ÓÐÉ', max_length=20, default='“Ðjáñgó”')

    class Meta:
        # Disable auto loading of this model as we load it on our own
        apps = Apps()
        verbose_name = 'úñí©óðé µóðéø'
        verbose_name_plural = 'úñí©óðé µóðéøß'

    def __str__(self):
        return self.title


class ClassSerializable:
    """
    An object that migration for class serializer.
    """
    pass


class ClassSerializableModel(models.Model):
    title = models.CharField(max_length=20, default=ClassSerializable())
    date = DateTimeRangeField(default=DateTimeTZRange(None, None, '[]'))

    class Meta:
        # Disable auto loading of this model as we load it on our own
        apps = Apps()


class Unserializable:
    """
    An object that migration doesn't know how to serialize.
    """
    def __init__(self, args1):
        self.args1 = args1


class UnserializableModel(models.Model):
    title = models.CharField(max_length=20, default=Unserializable(args1="args1"))

    class Meta:
        # Disable auto loading of this model as we load it on our own
        apps = Apps()


class UnmigratedModel(models.Model):
    """
    A model that is in a migration-less app (which this app is
    if its migrations directory has not been repointed)
    """
    pass


class EmptyManager(models.Manager):
    use_in_migrations = True


class FoodQuerySet(models.query.QuerySet):
    pass


class BaseFoodManager(models.Manager):
    def __init__(self, a, b, c=1, d=2):
        super().__init__()
        self.args = (a, b, c, d)


class FoodManager(BaseFoodManager.from_queryset(FoodQuerySet)):
    use_in_migrations = True


class NoMigrationFoodManager(BaseFoodManager.from_queryset(FoodQuerySet)):
    pass
