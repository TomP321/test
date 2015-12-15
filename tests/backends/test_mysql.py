# -*- coding: utf-8 -*-
# Unit and doctests for the MySQL backend.
from __future__ import unicode_literals

import unittest

from django.db import connection
from django.test import TestCase, override_settings


@override_settings(DEBUG=True)
@unittest.skipUnless(connection.vendor == 'mysql', 'MySQL specific test.')
class MySQLTests(TestCase):

    def test_auto_is_null_auto_config(self):
        query = "set sql_auto_is_null = 0"
        connection.init_connection_state()
        last_query = connection.queries[-1]['sql'].lower()
        if connection.features.can_return_last_inserted_id_with_auto_is_null:
            self.assertIn(query, last_query)
        else:
            self.assertNotIn(query, last_query)
