from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.db.models import CharField, TextField, Value as V
from django.db.models.functions import (
    Coalesce, Concat, Greatest, Least, Length, Lower, Now, Substr, Upper,
)
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature
from django.utils import six, timezone

from .models import Article, Author, Fan


lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua."""


class FunctionTests(TestCase):

    def test_coalesce(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(display_name=Coalesce('alias', 'name'))

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'smithj',
                'Rhonda',
            ],
            lambda a: a.display_name
        )

        with self.assertRaisesMessage(ValueError, 'Coalesce must take at least two expressions'):
            Author.objects.annotate(display_name=Coalesce('alias'))

    def test_coalesce_datetime_value(self):
        now = timezone.now().replace(microsecond=0)
        Article.objects.create(title='Testing, testing.', written=now)

        articles = Article.objects.annotate(
            publised_default=Coalesce('published', now),
        )
        article = articles.get()
        self.assertEqual(article.publised_default, now)

    def test_coalesce_mixed_values(self):
        a1 = Author.objects.create(name='John Smith', alias='smithj')
        a2 = Author.objects.create(name='Rhonda')
        ar1 = Article.objects.create(
            title="How to Django",
            text=lorem_ipsum,
            written=timezone.now(),
        )
        ar1.authors.add(a1)
        ar1.authors.add(a2)

        # mixed Text and Char
        article = Article.objects.annotate(
            headline=Coalesce('summary', 'text', output_field=TextField()),
        )

        self.assertQuerysetEqual(
            article.order_by('title'), [
                lorem_ipsum,
            ],
            lambda a: a.headline
        )

        # mixed Text and Char wrapped
        article = Article.objects.annotate(
            headline=Coalesce(Lower('summary'), Lower('text'), output_field=TextField()),
        )

        self.assertQuerysetEqual(
            article.order_by('title'), [
                lorem_ipsum.lower(),
            ],
            lambda a: a.headline
        )

    def test_coalesce_ordering(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')

        authors = Author.objects.order_by(Coalesce('alias', 'name'))
        self.assertQuerysetEqual(
            authors, [
                'Rhonda',
                'John Smith',
            ],
            lambda a: a.name
        )

        authors = Author.objects.order_by(Coalesce('alias', 'name').asc())
        self.assertQuerysetEqual(
            authors, [
                'Rhonda',
                'John Smith',
            ],
            lambda a: a.name
        )

        authors = Author.objects.order_by(Coalesce('alias', 'name').desc())
        self.assertQuerysetEqual(
            authors, [
                'John Smith',
                'Rhonda',
            ],
            lambda a: a.name
        )

    def test_greatest(self):
        now = timezone.now()
        before = now - timedelta(hours=1)

        Article.objects.create(
            title="Testing with Django",
            written=before,
            published=now,
        )

        articles = Article.objects.annotate(
            last_updated=Greatest('written', 'published'),
        )
        self.assertEqual(articles.first().last_updated, now)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_greatest_ignores_null(self):
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            last_updated=Greatest('written', 'published'),
        )
        self.assertEqual(articles.first().last_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_greatest_propogates_null(self):
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            last_updated=Greatest('written', 'published'),
        )
        self.assertIsNone(articles.first().last_updated)

    def test_greatest_coalesce_workaround(self):
        past = datetime(1900, 1, 1)
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            last_updated=Greatest(
                Coalesce('written', past),
                Coalesce('published', past),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    def test_greatest_all_null(self):
        Article.objects.create(title="Testing with Django", written=timezone.now())

        articles = Article.objects.annotate(last_updated=Greatest('published', 'updated'))
        self.assertIsNone(articles.first().last_updated)

    def test_greatest_one_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Greatest must take at least two expressions'):
            Greatest('written')

    def test_greatest_related_field(self):
        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)

        authors = Author.objects.annotate(
            highest_age=Greatest('age', 'fans__age'),
        )
        self.assertEqual(authors.first().highest_age, 50)

    def test_greatest_update(self):
        author = Author.objects.create(name='James Smith', goes_by='Jim')

        Author.objects.update(alias=Greatest('name', 'goes_by'))

        author.refresh_from_db()
        self.assertEqual(author.alias, 'Jim')

    def test_least(self):
        now = timezone.now()
        before = now - timedelta(hours=1)

        Article.objects.create(
            title="Testing with Django",
            written=before,
            published=now,
        )

        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertEqual(articles.first().first_updated, before)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_least_ignores_null(self):
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertEqual(articles.first().first_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_least_propogates_null(self):
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertIsNone(articles.first().first_updated)

    def test_least_coalesce_workaround(self):
        future = datetime(2100, 1, 1)
        now = timezone.now()

        Article.objects.create(title="Testing with Django", written=now)

        articles = Article.objects.annotate(
            last_updated=Least(
                Coalesce('written', future),
                Coalesce('published', future),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    def test_least_all_null(self):
        Article.objects.create(title="Testing with Django", written=timezone.now())

        articles = Article.objects.annotate(first_updated=Least('published', 'updated'))
        self.assertIsNone(articles.first().first_updated)

    def test_least_one_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Least must take at least two expressions'):
            Least('written')

    def test_least_related_field(self):
        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)

        authors = Author.objects.annotate(
            lowest_age=Least('age', 'fans__age'),
        )
        self.assertEqual(authors.first().lowest_age, 45)

    def test_least_update(self):
        author = Author.objects.create(name='James Smith', goes_by='Jim')

        Author.objects.update(alias=Least('name', 'goes_by'))

        author.refresh_from_db()
        self.assertEqual(author.alias, 'James Smith')

    def test_concat(self):
        Author.objects.create(name='Jayden')
        Author.objects.create(name='John Smith', alias='smithj', goes_by='John')
        Author.objects.create(name='Margaret', goes_by='Maggie')
        Author.objects.create(name='Rhonda', alias='adnohR')

        authors = Author.objects.annotate(joined=Concat('alias', 'goes_by'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                '',
                'smithjJohn',
                'Maggie',
                'adnohR',
            ],
            lambda a: a.joined
        )

        with self.assertRaisesMessage(ValueError, 'Concat must take at least two expressions'):
            Author.objects.annotate(joined=Concat('alias'))

    def test_concat_many(self):
        Author.objects.create(name='Jayden')
        Author.objects.create(name='John Smith', alias='smithj', goes_by='John')
        Author.objects.create(name='Margaret', goes_by='Maggie')
        Author.objects.create(name='Rhonda', alias='adnohR')

        authors = Author.objects.annotate(
            joined=Concat('name', V(' ('), 'goes_by', V(')'), output_field=CharField()),
        )

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'Jayden ()',
                'John Smith (John)',
                'Margaret (Maggie)',
                'Rhonda ()',
            ],
            lambda a: a.joined
        )

    def test_concat_mixed_char_text(self):
        Article.objects.create(title='The Title', text=lorem_ipsum, written=timezone.now())
        article = Article.objects.annotate(
            title_text=Concat('title', V(' - '), 'text', output_field=TextField()),
        ).get(title='The Title')
        self.assertEqual(article.title + ' - ' + article.text, article.title_text)

        # wrap the concat in something else to ensure that we're still
        # getting text rather than bytes
        article = Article.objects.annotate(
            title_text=Upper(Concat('title', V(' - '), 'text', output_field=TextField())),
        ).get(title='The Title')
        expected = article.title + ' - ' + article.text
        self.assertEqual(expected.upper(), article.title_text)

    def test_lower(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(lower_name=Lower('name'))

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'john smith',
                'rhonda',
            ],
            lambda a: a.lower_name
        )

        Author.objects.update(name=Lower('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ('john smith', 'john smith'),
                ('rhonda', 'rhonda'),
            ],
            lambda a: (a.lower_name, a.name)
        )

    def test_upper(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(upper_name=Upper('name'))

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'JOHN SMITH',
                'RHONDA',
            ],
            lambda a: a.upper_name
        )

        Author.objects.update(name=Upper('name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ('JOHN SMITH', 'JOHN SMITH'),
                ('RHONDA', 'RHONDA'),
            ],
            lambda a: (a.upper_name, a.name)
        )

    def test_length(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(
            name_length=Length('name'),
            alias_length=Length('alias'))

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                (10, 6),
                (6, None),
            ],
            lambda a: (a.name_length, a.alias_length)
        )

        self.assertEqual(authors.filter(alias_length__lte=Length('name')).count(), 1)

    def test_length_ordering(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='John Smith', alias='smithj1')
        Author.objects.create(name='Rhonda', alias='ronny')

        authors = Author.objects.order_by(Length('name'), Length('alias'))

        self.assertQuerysetEqual(
            authors, [
                ('Rhonda', 'ronny'),
                ('John Smith', 'smithj'),
                ('John Smith', 'smithj1'),
            ],
            lambda a: (a.name, a.alias)
        )

    def test_substr(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(name_part=Substr('name', 5, 3))

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ' Sm',
                'da',
            ],
            lambda a: a.name_part
        )

        authors = Author.objects.annotate(name_part=Substr('name', 2))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'ohn Smith',
                'honda',
            ],
            lambda a: a.name_part
        )

        # if alias is null, set to first 5 lower characters of the name
        Author.objects.filter(alias__isnull=True).update(
            alias=Lower(Substr('name', 1, 5)),
        )

        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'smithj',
                'rhond',
            ],
            lambda a: a.alias
        )

    def test_substr_start(self):
        Author.objects.create(name='John Smith', alias='smithj')
        a = Author.objects.annotate(
            name_part_1=Substr('name', 1),
            name_part_2=Substr('name', 2),
        ).get(alias='smithj')

        self.assertEqual(a.name_part_1[1:], a.name_part_2)

        with six.assertRaisesRegex(self, ValueError, "'pos' must be greater than 0"):
            Author.objects.annotate(raises=Substr('name', 0))

    def test_substr_with_expressions(self):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(name_part=Substr('name', 5, 3))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                ' Sm',
                'da',
            ],
            lambda a: a.name_part
        )

    def test_nested_function_ordering(self):
        Author.objects.create(name='John Smith')
        Author.objects.create(name='Rhonda Simpson', alias='ronny')

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')))
        self.assertQuerysetEqual(
            authors, [
                'Rhonda Simpson',
                'John Smith',
            ],
            lambda a: a.name
        )

        authors = Author.objects.order_by(Length(Coalesce('alias', 'name')).desc())
        self.assertQuerysetEqual(
            authors, [
                'John Smith',
                'Rhonda Simpson',
            ],
            lambda a: a.name
        )

    def test_now(self):
        ar1 = Article.objects.create(
            title='How to Django',
            text=lorem_ipsum,
            written=timezone.now(),
        )
        ar2 = Article.objects.create(
            title='How to Time Travel',
            text=lorem_ipsum,
            written=timezone.now(),
        )

        num_updated = Article.objects.filter(id=ar1.id, published=None).update(published=Now())
        self.assertEqual(num_updated, 1)

        num_updated = Article.objects.filter(id=ar1.id, published=None).update(published=Now())
        self.assertEqual(num_updated, 0)

        ar1.refresh_from_db()
        self.assertIsInstance(ar1.published, datetime)

        ar2.published = Now() + timedelta(days=2)
        ar2.save()
        ar2.refresh_from_db()
        self.assertIsInstance(ar2.published, datetime)

        self.assertQuerysetEqual(
            Article.objects.filter(published__lte=Now()),
            ['How to Django'],
            lambda a: a.title
        )
        self.assertQuerysetEqual(
            Article.objects.filter(published__gt=Now()),
            ['How to Time Travel'],
            lambda a: a.title
        )
