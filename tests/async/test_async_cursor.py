import unittest

from django.db import connection, new_connection
from django.test import SimpleTestCase


@unittest.skipUnless(connection.supports_async is True, "Async DB test")
class AsyncCursorTests(SimpleTestCase):
    async def test_aexecute(self):
        async with new_connection() as conn:
            async with conn.acursor() as cursor:
                await cursor.aexecute("SELECT 1")

    async def test_afetchone(self):
        async with new_connection() as conn:
            async with conn.acursor() as cursor:
                await cursor.aexecute("SELECT 1")
                result = await cursor.afetchone()
            self.assertEqual(result, (1,))

    async def test_afetchmany(self):
        async with new_connection() as conn:
            async with conn.acursor() as cursor:
                await cursor.aexecute(
                    """
                    SELECT *
                    FROM (VALUES
                            ('BANANA'),
                            ('STRAWBERRY'),
                            ('MELON')
                    ) AS v (NAME)"""
                )
                result = await cursor.afetchmany(size=2)
            self.assertEqual(result, [("BANANA",), ("STRAWBERRY",)])

    async def test_afetchall(self):
        async with new_connection() as conn:
            async with conn.acursor() as cursor:
                await cursor.aexecute(
                    """
                    SELECT *
                    FROM (VALUES
                            ('BANANA'),
                            ('STRAWBERRY'),
                            ('MELON')
                    ) AS v (NAME)"""
                )
                result = await cursor.afetchall()
            self.assertEqual(result, [("BANANA",), ("STRAWBERRY",), ("MELON",)])
