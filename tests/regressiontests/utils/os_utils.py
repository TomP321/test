# No unicode_literals, filesystem paths are native strings.
import os

from django.utils import unittest
from django.utils._os import safe_join


class SafeJoinTests(unittest.TestCase):
    def test_base_path_ends_with_sep(self):
        drive, path = os.path.splitdrive(safe_join("/abc/", "abc"))
        self.assertEqual(
            path,
            "{0}abc{0}abc".format(os.path.sep)
        )

    def test_root_path(self):
        drive, path = os.path.splitdrive(safe_join("/", "path"))
        self.assertEqual(
            path,
            "{0}path".format(os.path.sep),
        )

        drive, path = os.path.splitdrive(safe_join("/", ""))
        self.assertEqual(
            path,
            os.path.sep,
        )

    def test_safe_join_returns_native_string(self):
        # Regression test for #19398
        base = os.path.dirname(__file__)
        self.assertIsInstance(safe_join(base, 'foo'), str)
