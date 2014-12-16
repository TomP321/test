from django.template.base import TemplateSyntaxError
from django.template.loader import get_template
from django.test import SimpleTestCase

from ..utils import render, setup, TestObj


class IfTagTests(SimpleTestCase):

    @setup({'if-tag01': '{% if foo %}yes{% else %}no{% endif %}'})
    def test_if_tag01(self):
        output = render('if-tag01', {'foo': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag02': '{% if foo %}yes{% else %}no{% endif %}'})
    def test_if_tag02(self):
        output = render('if-tag02', {'foo': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag03': '{% if foo %}yes{% else %}no{% endif %}'})
    def test_if_tag03(self):
        output = render('if-tag03')
        self.assertEqual(output, 'no')

    @setup({'if-tag04': '{% if foo %}foo{% elif bar %}bar{% endif %}'})
    def test_if_tag04(self):
        output = render('if-tag04', {'foo': True})
        self.assertEqual(output, 'foo')

    @setup({'if-tag05': '{% if foo %}foo{% elif bar %}bar{% endif %}'})
    def test_if_tag05(self):
        output = render('if-tag05', {'bar': True})
        self.assertEqual(output, 'bar')

    @setup({'if-tag06': '{% if foo %}foo{% elif bar %}bar{% endif %}'})
    def test_if_tag06(self):
        output = render('if-tag06')
        self.assertEqual(output, '')

    @setup({'if-tag07': '{% if foo %}foo{% elif bar %}bar{% else %}nothing{% endif %}'})
    def test_if_tag07(self):
        output = render('if-tag07', {'foo': True})
        self.assertEqual(output, 'foo')

    @setup({'if-tag08': '{% if foo %}foo{% elif bar %}bar{% else %}nothing{% endif %}'})
    def test_if_tag08(self):
        output = render('if-tag08', {'bar': True})
        self.assertEqual(output, 'bar')

    @setup({'if-tag09': '{% if foo %}foo{% elif bar %}bar{% else %}nothing{% endif %}'})
    def test_if_tag09(self):
        output = render('if-tag09')
        self.assertEqual(output, 'nothing')

    @setup({'if-tag10': '{% if foo %}foo{% elif bar %}bar{% elif baz %}baz{% else %}nothing{% endif %}'})
    def test_if_tag10(self):
        output = render('if-tag10', {'foo': True})
        self.assertEqual(output, 'foo')

    @setup({'if-tag11': '{% if foo %}foo{% elif bar %}bar{% elif baz %}baz{% else %}nothing{% endif %}'})
    def test_if_tag11(self):
        output = render('if-tag11', {'bar': True})
        self.assertEqual(output, 'bar')

    @setup({'if-tag12': '{% if foo %}foo{% elif bar %}bar{% elif baz %}baz{% else %}nothing{% endif %}'})
    def test_if_tag12(self):
        output = render('if-tag12', {'baz': True})
        self.assertEqual(output, 'baz')

    @setup({'if-tag13': '{% if foo %}foo{% elif bar %}bar{% elif baz %}baz{% else %}nothing{% endif %}'})
    def test_if_tag13(self):
        output = render('if-tag13')
        self.assertEqual(output, 'nothing')

    # Filters
    @setup({'if-tag-filter01': '{% if foo|length == 5 %}yes{% else %}no{% endif %}'})
    def test_if_tag_filter01(self):
        output = render('if-tag-filter01', {'foo': 'abcde'})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-filter02': '{% if foo|upper == \'ABC\' %}yes{% else %}no{% endif %}'})
    def test_if_tag_filter02(self):
        output = render('if-tag-filter02')
        self.assertEqual(output, 'no')

    # Equality
    @setup({'if-tag-eq01': '{% if foo == bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_eq01(self):
        output = render('if-tag-eq01')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-eq02': '{% if foo == bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_eq02(self):
        output = render('if-tag-eq02', {'foo': 1})
        self.assertEqual(output, 'no')

    @setup({'if-tag-eq03': '{% if foo == bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_eq03(self):
        output = render('if-tag-eq03', {'foo': 1, 'bar': 1})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-eq04': '{% if foo == bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_eq04(self):
        output = render('if-tag-eq04', {'foo': 1, 'bar': 2})
        self.assertEqual(output, 'no')

    @setup({'if-tag-eq05': '{% if foo == \'\' %}yes{% else %}no{% endif %}'})
    def test_if_tag_eq05(self):
        output = render('if-tag-eq05')
        self.assertEqual(output, 'no')

    # Comparison
    @setup({'if-tag-gt-01': '{% if 2 > 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_gt_01(self):
        output = render('if-tag-gt-01')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-gt-02': '{% if 1 > 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_gt_02(self):
        output = render('if-tag-gt-02')
        self.assertEqual(output, 'no')

    @setup({'if-tag-gte-01': '{% if 1 >= 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_gte_01(self):
        output = render('if-tag-gte-01')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-gte-02': '{% if 1 >= 2 %}yes{% else %}no{% endif %}'})
    def test_if_tag_gte_02(self):
        output = render('if-tag-gte-02')
        self.assertEqual(output, 'no')

    @setup({'if-tag-lt-01': '{% if 1 < 2 %}yes{% else %}no{% endif %}'})
    def test_if_tag_lt_01(self):
        output = render('if-tag-lt-01')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-lt-02': '{% if 1 < 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_lt_02(self):
        output = render('if-tag-lt-02')
        self.assertEqual(output, 'no')

    @setup({'if-tag-lte-01': '{% if 1 <= 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_lte_01(self):
        output = render('if-tag-lte-01')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-lte-02': '{% if 2 <= 1 %}yes{% else %}no{% endif %}'})
    def test_if_tag_lte_02(self):
        output = render('if-tag-lte-02')
        self.assertEqual(output, 'no')

    # Contains
    @setup({'if-tag-in-01': '{% if 1 in x %}yes{% else %}no{% endif %}'})
    def test_if_tag_in_01(self):
        output = render('if-tag-in-01', {'x': [1]})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-in-02': '{% if 2 in x %}yes{% else %}no{% endif %}'})
    def test_if_tag_in_02(self):
        output = render('if-tag-in-02', {'x': [1]})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not-in-01': '{% if 1 not in x %}yes{% else %}no{% endif %}'})
    def test_if_tag_not_in_01(self):
        output = render('if-tag-not-in-01', {'x': [1]})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not-in-02': '{% if 2 not in x %}yes{% else %}no{% endif %}'})
    def test_if_tag_not_in_02(self):
        output = render('if-tag-not-in-02', {'x': [1]})
        self.assertEqual(output, 'yes')

    # AND
    @setup({'if-tag-and01': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and01(self):
        output = render('if-tag-and01', {'foo': True, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-and02': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and02(self):
        output = render('if-tag-and02', {'foo': True, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and03': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and03(self):
        output = render('if-tag-and03', {'foo': False, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and04': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and04(self):
        output = render('if-tag-and04', {'foo': False, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and05': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and05(self):
        output = render('if-tag-and05', {'foo': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and06': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and06(self):
        output = render('if-tag-and06', {'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and07': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and07(self):
        output = render('if-tag-and07', {'foo': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-and08': '{% if foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_and08(self):
        output = render('if-tag-and08', {'bar': True})
        self.assertEqual(output, 'no')

    # OR
    @setup({'if-tag-or01': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or01(self):
        output = render('if-tag-or01', {'foo': True, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-or02': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or02(self):
        output = render('if-tag-or02', {'foo': True, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-or03': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or03(self):
        output = render('if-tag-or03', {'foo': False, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-or04': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or04(self):
        output = render('if-tag-or04', {'foo': False, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-or05': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or05(self):
        output = render('if-tag-or05', {'foo': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-or06': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or06(self):
        output = render('if-tag-or06', {'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-or07': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or07(self):
        output = render('if-tag-or07', {'foo': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-or08': '{% if foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_or08(self):
        output = render('if-tag-or08', {'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-or09': '{% if foo or bar or baz %}yes{% else %}no{% endif %}'})
    def test_if_tag_or09(self):
        """
        multiple ORs
        """
        output = render('if-tag-or09', {'baz': True})
        self.assertEqual(output, 'yes')

    # NOT
    @setup({'if-tag-not01': '{% if not foo %}no{% else %}yes{% endif %}'})
    def test_if_tag_not01(self):
        output = render('if-tag-not01', {'foo': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not02': '{% if not not foo %}no{% else %}yes{% endif %}'})
    def test_if_tag_not02(self):
        output = render('if-tag-not02', {'foo': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not06': '{% if foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not06(self):
        output = render('if-tag-not06')
        self.assertEqual(output, 'no')

    @setup({'if-tag-not07': '{% if foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not07(self):
        output = render('if-tag-not07', {'foo': True, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not08': '{% if foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not08(self):
        output = render('if-tag-not08', {'foo': True, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not09': '{% if foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not09(self):
        output = render('if-tag-not09', {'foo': False, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not10': '{% if foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not10(self):
        output = render('if-tag-not10', {'foo': False, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not11': '{% if not foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not11(self):
        output = render('if-tag-not11')
        self.assertEqual(output, 'no')

    @setup({'if-tag-not12': '{% if not foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not12(self):
        output = render('if-tag-not12', {'foo': True, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not13': '{% if not foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not13(self):
        output = render('if-tag-not13', {'foo': True, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not14': '{% if not foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not14(self):
        output = render('if-tag-not14', {'foo': False, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not15': '{% if not foo and bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not15(self):
        output = render('if-tag-not15', {'foo': False, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not16': '{% if foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not16(self):
        output = render('if-tag-not16')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not17': '{% if foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not17(self):
        output = render('if-tag-not17', {'foo': True, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not18': '{% if foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not18(self):
        output = render('if-tag-not18', {'foo': True, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not19': '{% if foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not19(self):
        output = render('if-tag-not19', {'foo': False, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not20': '{% if foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not20(self):
        output = render('if-tag-not20', {'foo': False, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not21': '{% if not foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not21(self):
        output = render('if-tag-not21')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not22': '{% if not foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not22(self):
        output = render('if-tag-not22', {'foo': True, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not23': '{% if not foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not23(self):
        output = render('if-tag-not23', {'foo': True, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not24': '{% if not foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not24(self):
        output = render('if-tag-not24', {'foo': False, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not25': '{% if not foo or bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not25(self):
        output = render('if-tag-not25', {'foo': False, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not26': '{% if not foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not26(self):
        output = render('if-tag-not26')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not27': '{% if not foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not27(self):
        output = render('if-tag-not27', {'foo': True, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not28': '{% if not foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not28(self):
        output = render('if-tag-not28', {'foo': True, 'bar': False})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not29': '{% if not foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not29(self):
        output = render('if-tag-not29', {'foo': False, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not30': '{% if not foo and not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not30(self):
        output = render('if-tag-not30', {'foo': False, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not31': '{% if not foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not31(self):
        output = render('if-tag-not31')
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not32': '{% if not foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not32(self):
        output = render('if-tag-not32', {'foo': True, 'bar': True})
        self.assertEqual(output, 'no')

    @setup({'if-tag-not33': '{% if not foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not33(self):
        output = render('if-tag-not33', {'foo': True, 'bar': False})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not34': '{% if not foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not34(self):
        output = render('if-tag-not34', {'foo': False, 'bar': True})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-not35': '{% if not foo or not bar %}yes{% else %}no{% endif %}'})
    def test_if_tag_not35(self):
        output = render('if-tag-not35', {'foo': False, 'bar': False})
        self.assertEqual(output, 'yes')

    # Various syntax errors
    @setup({'if-tag-error01': '{% if %}yes{% endif %}'})
    def test_if_tag_error01(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error01')

    @setup({'if-tag-error02': '{% if foo and %}yes{% else %}no{% endif %}'})
    def test_if_tag_error02(self):
        with self.assertRaises(TemplateSyntaxError):
            render('if-tag-error02', {'foo': True})

    @setup({'if-tag-error03': '{% if foo or %}yes{% else %}no{% endif %}'})
    def test_if_tag_error03(self):
        with self.assertRaises(TemplateSyntaxError):
            render('if-tag-error03', {'foo': True})

    @setup({'if-tag-error04': '{% if not foo and %}yes{% else %}no{% endif %}'})
    def test_if_tag_error04(self):
        with self.assertRaises(TemplateSyntaxError):
            render('if-tag-error04', {'foo': True})

    @setup({'if-tag-error05': '{% if not foo or %}yes{% else %}no{% endif %}'})
    def test_if_tag_error05(self):
        with self.assertRaises(TemplateSyntaxError):
            render('if-tag-error05', {'foo': True})

    @setup({'if-tag-error06': '{% if abc def %}yes{% endif %}'})
    def test_if_tag_error06(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error06')

    @setup({'if-tag-error07': '{% if not %}yes{% endif %}'})
    def test_if_tag_error07(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error07')

    @setup({'if-tag-error08': '{% if and %}yes{% endif %}'})
    def test_if_tag_error08(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error08')

    @setup({'if-tag-error09': '{% if or %}yes{% endif %}'})
    def test_if_tag_error09(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error09')

    @setup({'if-tag-error10': '{% if == %}yes{% endif %}'})
    def test_if_tag_error10(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error10')

    @setup({'if-tag-error11': '{% if 1 == %}yes{% endif %}'})
    def test_if_tag_error11(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error11')

    @setup({'if-tag-error12': '{% if a not b %}yes{% endif %}'})
    def test_if_tag_error12(self):
        with self.assertRaises(TemplateSyntaxError):
            get_template('if-tag-error12')

    @setup({'if-tag-shortcircuit01': '{% if x.is_true or x.is_bad %}yes{% else %}no{% endif %}'})
    def test_if_tag_shortcircuit01(self):
        """
        If evaluations are shortcircuited where possible
        """
        output = render('if-tag-shortcircuit01', {'x': TestObj()})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-shortcircuit02': '{% if x.is_false and x.is_bad %}yes{% else %}no{% endif %}'})
    def test_if_tag_shortcircuit02(self):
        """
        The is_bad() function should not be evaluated. If it is, an
        exception is raised.
        """
        output = render('if-tag-shortcircuit02', {'x': TestObj()})
        self.assertEqual(output, 'no')

    @setup({'if-tag-badarg01': '{% if x|default_if_none:y %}yes{% endif %}'})
    def test_if_tag_badarg01(self):
        """
        Non-existent args
        """
        output = render('if-tag-badarg01')
        self.assertEqual(output, '')

    @setup({'if-tag-badarg02': '{% if x|default_if_none:y %}yes{% endif %}'})
    def test_if_tag_badarg02(self):
        output = render('if-tag-badarg02', {'y': 0})
        self.assertEqual(output, '')

    @setup({'if-tag-badarg03': '{% if x|default_if_none:y %}yes{% endif %}'})
    def test_if_tag_badarg03(self):
        output = render('if-tag-badarg03', {'y': 1})
        self.assertEqual(output, 'yes')

    @setup({'if-tag-badarg04': '{% if x|default_if_none:y %}yes{% else %}no{% endif %}'})
    def test_if_tag_badarg04(self):
        output = render('if-tag-badarg04')
        self.assertEqual(output, 'no')
