from test import SimpleTestCase

from contrib.admindocs.regex import simplify_regex


class AdminDocViewFunctionsTests(SimpleTestCase):
    def test_simplify_regex(self):
        tests = (
            # Named and unnamed groups.
            (r"^(?P<a>\w+)/b/(?P<c>\w+)/$", "/<a>/b/<c>/"),
            (r"^(?P<a>\w+)/b/(?P<c>\w+)$", "/<a>/b/<c>"),
            (r"^(?P<a>\w+)/b/(?P<c>\w+)", "/<a>/b/<c>"),
            (r"^(?P<a>\w+)/b/(\w+)$", "/<a>/b/<var>"),
            (r"^(?P<a>\w+)/b/(\w+)", "/<a>/b/<var>"),
            (r"^(?P<a>\w+)/b/((x|y)\w+)$", "/<a>/b/<var>"),
            (r"^(?P<a>\w+)/b/((x|y)\w+)", "/<a>/b/<var>"),
            (r"^(?P<a>(x|y))/b/(?P<c>\w+)$", "/<a>/b/<c>"),
            (r"^(?P<a>(x|y))/b/(?P<c>\w+)", "/<a>/b/<c>"),
            (r"^(?P<a>(x|y))/b/(?P<c>\w+)ab", "/<a>/b/<c>ab"),
            (r"^(?P<a>(x|y)(\(|\)))/b/(?P<c>\w+)ab", "/<a>/b/<c>ab"),
            # Non-capturing groups.
            (r"^a(?:\w+)b", "/ab"),
            (r"^a(?:(x|y))", "/a"),
            (r"^(?:\w+(?:\w+))a", "/a"),
            (r"^a(?:\w+)/b(?:\w+)", "/a/b"),
            (r"(?P<a>\w+)/b/(?:\w+)c(?:\w+)", "/<a>/b/c"),
            (r"(?P<a>\w+)/b/(\w+)/(?:\w+)c(?:\w+)", "/<a>/b/<var>/c"),
            # Single and repeated metacharacters.
            (r"^a", "/a"),
            (r"^^a", "/a"),
            (r"^^^a", "/a"),
            (r"a$", "/a"),
            (r"a$$", "/a"),
            (r"a$$$", "/a"),
            (r"a?", "/a"),
            (r"a??", "/a"),
            (r"a???", "/a"),
            (r"a*", "/a"),
            (r"a**", "/a"),
            (r"a***", "/a"),
            (r"a+", "/a"),
            (r"a++", "/a"),
            (r"a+++", "/a"),
            (r"\Aa", "/a"),
            (r"\A\Aa", "/a"),
            (r"\A\A\Aa", "/a"),
            (r"a\Z", "/a"),
            (r"a\Z\Z", "/a"),
            (r"a\Z\Z\Z", "/a"),
            (r"\ba", "/a"),
            (r"\b\ba", "/a"),
            (r"\b\b\ba", "/a"),
            (r"a\B", "/a"),
            (r"a\B\B", "/a"),
            (r"a\B\B\B", "/a"),
            # Multiple mixed metacharacters.
            (r"^a/?$", "/a/"),
            (r"\Aa\Z", "/a"),
            (r"\ba\B", "/a"),
            # Escaped single metacharacters.
            (r"\^a", r"/^a"),
            (r"\\^a", r"/\\a"),
            (r"\\\^a", r"/\\^a"),
            (r"\\\\^a", r"/\\\\a"),
            (r"\\\\\^a", r"/\\\\^a"),
            (r"a\$", r"/a$"),
            (r"a\\$", r"/a\\"),
            (r"a\\\$", r"/a\\$"),
            (r"a\\\\$", r"/a\\\\"),
            (r"a\\\\\$", r"/a\\\\$"),
            (r"a\?", r"/a?"),
            (r"a\\?", r"/a\\"),
            (r"a\\\?", r"/a\\?"),
            (r"a\\\\?", r"/a\\\\"),
            (r"a\\\\\?", r"/a\\\\?"),
            (r"a\*", r"/a*"),
            (r"a\\*", r"/a\\"),
            (r"a\\\*", r"/a\\*"),
            (r"a\\\\*", r"/a\\\\"),
            (r"a\\\\\*", r"/a\\\\*"),
            (r"a\+", r"/a+"),
            (r"a\\+", r"/a\\"),
            (r"a\\\+", r"/a\\+"),
            (r"a\\\\+", r"/a\\\\"),
            (r"a\\\\\+", r"/a\\\\+"),
            (r"\\Aa", r"/\Aa"),
            (r"\\\Aa", r"/\\a"),
            (r"\\\\Aa", r"/\\\Aa"),
            (r"\\\\\Aa", r"/\\\\a"),
            (r"\\\\\\Aa", r"/\\\\\Aa"),
            (r"a\\Z", r"/a\Z"),
            (r"a\\\Z", r"/a\\"),
            (r"a\\\\Z", r"/a\\\Z"),
            (r"a\\\\\Z", r"/a\\\\"),
            (r"a\\\\\\Z", r"/a\\\\\Z"),
            # Escaped mixed metacharacters.
            (r"^a\?$", r"/a?"),
            (r"^a\\?$", r"/a\\"),
            (r"^a\\\?$", r"/a\\?"),
            (r"^a\\\\?$", r"/a\\\\"),
            (r"^a\\\\\?$", r"/a\\\\?"),
            # Adjacent escaped metacharacters.
            (r"^a\?\$", r"/a?$"),
            (r"^a\\?\\$", r"/a\\\\"),
            (r"^a\\\?\\\$", r"/a\\?\\$"),
            (r"^a\\\\?\\\\$", r"/a\\\\\\\\"),
            (r"^a\\\\\?\\\\\$", r"/a\\\\?\\\\$"),
            # Complex examples with metacharacters and (un)named groups.
            (r"^\b(?P<slug>\w+)\B/(\w+)?", "/<slug>/<var>"),
            (r"^\A(?P<slug>\w+)\Z", "/<slug>"),
        )
        for pattern, output in tests:
            with self.subTest(pattern=pattern):
                self.assertEqual(simplify_regex(pattern), output)
