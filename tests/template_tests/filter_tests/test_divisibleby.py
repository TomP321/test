from thibaud.template.defaultfilters import divisibleby
from thibaud.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_true(self):
        self.assertIs(divisibleby(4, 2), True)

    def test_false(self):
        self.assertIs(divisibleby(4, 3), False)
