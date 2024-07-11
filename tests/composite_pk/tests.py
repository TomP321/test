import json
import unittest

import yaml

from django.core import serializers
from django.db import IntegrityError, connection
from django.db.models import CompositePrimaryKey
from django.test import TestCase

from .models import Comment, Tenant, User


class CompositePKTests(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create()
        cls.user = User.objects.create(tenant=cls.tenant, id=1)
        cls.comment = Comment.objects.create(tenant=cls.tenant, id=1, user=cls.user)

    @staticmethod
    def get_constraints(table):
        with connection.cursor() as cursor:
            return connection.introspection.get_constraints(cursor, table)

    def test_pk_updated_if_field_updated(self):
        meta = User._meta
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.pk, (self.tenant.id, self.user.id))
        self.assertTrue(meta.pk.is_set(user.pk))
        user.tenant_id = 9831
        self.assertEqual(user.pk, (9831, self.user.id))
        self.assertTrue(meta.pk.is_set(user.pk))
        user.id = 4321
        self.assertEqual(user.pk, (9831, 4321))
        self.assertTrue(meta.pk.is_set(user.pk))
        user.pk = (9132, 3521)
        self.assertEqual(user.tenant_id, 9132)
        self.assertEqual(user.id, 3521)
        self.assertTrue(meta.pk.is_set(user.pk))
        user.id = None
        self.assertFalse(meta.pk.is_set(user.pk))

    def test_composite_pk_in_fields(self):
        user_fields = {f.name for f in User._meta.get_fields()}
        self.assertEqual(user_fields, {"pk", "tenant", "id", "email", "comments"})

        comment_fields = {f.name for f in Comment._meta.get_fields()}
        self.assertEqual(
            comment_fields,
            {"pk", "tenant", "id", "user_id", "user", "text"},
        )

    def test_pk_field(self):
        pk = User._meta.get_field("pk")
        self.assertIsInstance(pk, CompositePrimaryKey)
        self.assertIs(User._meta.pk, pk)

    def test_error_on_user_pk_conflict(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(tenant=self.tenant, id=self.user.id)

    def test_error_on_comment_pk_conflict(self):
        with self.assertRaises(IntegrityError):
            Comment.objects.create(tenant=self.tenant, id=self.comment.id)

    @unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL specific test")
    def test_get_constraints_postgresql(self):
        user_constraints = self.get_constraints(User._meta.db_table)
        user_pk = user_constraints["composite_pk_user_pkey"]
        self.assertEqual(user_pk["columns"], ["tenant_id", "id"])
        self.assertTrue(user_pk["primary_key"])

        comment_constraints = self.get_constraints(Comment._meta.db_table)
        comment_pk = comment_constraints["composite_pk_comment_pkey"]
        self.assertEqual(comment_pk["columns"], ["tenant_id", "comment_id"])
        self.assertTrue(comment_pk["primary_key"])

    @unittest.skipUnless(connection.vendor == "sqlite", "SQLite specific test")
    def test_get_constraints_sqlite(self):
        user_constraints = self.get_constraints(User._meta.db_table)
        user_pk = user_constraints["__primary__"]
        self.assertEqual(user_pk["columns"], ["tenant_id", "id"])
        self.assertTrue(user_pk["primary_key"])

        comment_constraints = self.get_constraints(Comment._meta.db_table)
        comment_pk = comment_constraints["__primary__"]
        self.assertEqual(comment_pk["columns"], ["tenant_id", "comment_id"])
        self.assertTrue(comment_pk["primary_key"])

    @unittest.skipUnless(connection.vendor == "mysql", "MySQL specific test")
    def test_get_constraints_mysql(self):
        user_constraints = self.get_constraints(User._meta.db_table)
        user_pk = user_constraints["PRIMARY"]
        self.assertEqual(user_pk["columns"], ["tenant_id", "id"])
        self.assertTrue(user_pk["primary_key"])

        comment_constraints = self.get_constraints(Comment._meta.db_table)
        comment_pk = comment_constraints["PRIMARY"]
        self.assertEqual(comment_pk["columns"], ["tenant_id", "comment_id"])
        self.assertTrue(comment_pk["primary_key"])

    @unittest.skipUnless(connection.vendor == "oracle", "Oracle specific test")
    def test_get_constraints_oracle(self):
        user_constraints = self.get_constraints(User._meta.db_table)
        user_pk = next(c for c in user_constraints.values() if c["primary_key"])
        self.assertEqual(user_pk["columns"], ["tenant_id", "id"])
        self.assertEqual(user_pk["primary_key"], 1)

        comment_constraints = self.get_constraints(Comment._meta.db_table)
        comment_pk = next(c for c in comment_constraints.values() if c["primary_key"])
        self.assertEqual(comment_pk["columns"], ["tenant_id", "comment_id"])
        self.assertEqual(comment_pk["primary_key"], 1)

    def test_in_bulk(self):
        """
        Test the .in_bulk() method of composite_pk models.
        """
        result = Comment.objects.in_bulk()
        self.assertEqual(result, {self.comment.pk: self.comment})

        result = Comment.objects.in_bulk([self.comment.pk])
        self.assertEqual(result, {self.comment.pk: self.comment})

    def test_iterator(self):
        """
        Test the .iterator() method of composite_pk models.
        """
        result = list(Comment.objects.iterator())
        self.assertEqual(result, [self.comment])


class CompositePKFixturesTests(TestCase):
    fixtures = ["tenant"]

    def test_objects(self):
        tenant_1, tenant_2, tenant_3 = Tenant.objects.order_by("pk")
        self.assertEqual(tenant_1.id, 1)
        self.assertEqual(tenant_1.name, "Tenant 1")
        self.assertEqual(tenant_2.id, 2)
        self.assertEqual(tenant_2.name, "Tenant 2")
        self.assertEqual(tenant_3.id, 3)
        self.assertEqual(tenant_3.name, "Tenant 3")

        user_1, user_2, user_3, user_4 = User.objects.order_by("pk")
        self.assertEqual(user_1.id, 1)
        self.assertEqual(user_1.tenant_id, 1)
        self.assertEqual(user_1.pk, (1, 1))
        self.assertEqual(user_1.email, "user0001@example.com")
        self.assertEqual(user_2.id, 2)
        self.assertEqual(user_2.tenant_id, 1)
        self.assertEqual(user_2.pk, (1, 2))
        self.assertEqual(user_2.email, "user0002@example.com")
        self.assertEqual(user_3.id, 3)
        self.assertEqual(user_3.tenant_id, 2)
        self.assertEqual(user_3.pk, (2, 3))
        self.assertEqual(user_3.email, "user0003@example.com")
        self.assertEqual(user_4.id, 4)
        self.assertEqual(user_4.tenant_id, 2)
        self.assertEqual(user_4.pk, (2, 4))
        self.assertEqual(user_4.email, "user0004@example.com")

    def test_serialize_json(self):
        users = User.objects.filter(pk=(1, 1))
        result = serializers.serialize("json", users)
        self.assertEqual(
            json.loads(result),
            [
                {
                    "model": "composite_pk.user",
                    "pk": [1, 1],
                    "fields": {
                        "email": "user0001@example.com",
                        "id": 1,
                        "tenant": 1,
                    },
                }
            ],
        )

    def test_serialize_jsonl(self):
        users = User.objects.filter(pk=(1, 2))
        result = serializers.serialize("jsonl", users)
        self.assertEqual(
            json.loads(result),
            {
                "model": "composite_pk.user",
                "pk": [1, 2],
                "fields": {
                    "email": "user0002@example.com",
                    "id": 2,
                    "tenant": 1,
                },
            },
        )

    def test_serialize_yaml(self):
        users = User.objects.filter(pk=(2, 3))
        result = serializers.serialize("yaml", users)
        self.assertEqual(
            yaml.safe_load(result),
            [
                {
                    "model": "composite_pk.user",
                    "pk": [2, 3],
                    "fields": {
                        "email": "user0003@example.com",
                        "id": 3,
                        "tenant": 2,
                    },
                },
            ],
        )
