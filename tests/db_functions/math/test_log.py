import math
from decimal import Decimal

from django.db.models.functions import Log
from django.test import TestCase

from ..models import DecimalModel, FloatModel, IntegerModel


class LogTests(TestCase):

    def test_decimal(self):
        DecimalModel.objects.create(n1=Decimal('12.9'), n2=Decimal('3.6'))
        obj = DecimalModel.objects.annotate(n_log=Log('n1', 'n2')).first()
        self.assertAlmostEqual(obj.n_log, Decimal(math.log(obj.n2, obj.n1)))

    def test_float(self):
        FloatModel.objects.create(f1=27.5, f2=31.5)
        obj = FloatModel.objects.annotate(f_log=Log('f1', 'f2')).first()
        self.assertAlmostEqual(obj.f_log, math.log(obj.f2, obj.f1))

    def test_integer(self):
        IntegerModel.objects.create(small=4, normal=8, big=2)
        obj = IntegerModel.objects.annotate(
            small_log=Log('small', 'big'),
            normal_log=Log('normal', 'big'),
            big_log=Log('big', 'big'),
        ).first()
        self.assertAlmostEqual(obj.small_log, math.log(obj.big, obj.small))
        self.assertAlmostEqual(obj.normal_log, math.log(obj.big, obj.normal))
        self.assertAlmostEqual(obj.big_log, math.log(obj.big, obj.big))
