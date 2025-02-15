from unittest import mock

from thibaud.core.checks import Error
from thibaud.db import connections, models
from thibaud.test import SimpleTestCase
from thibaud.test.utils import isolate_apps


def dummy_allow_migrate(db, app_label, **hints):
    # Prevent checks from being run on the 'other' database, which doesn't have
    # its check_field() method mocked in the test.
    return db == "default"


@isolate_apps("invalid_models_tests")
class BackendSpecificChecksTests(SimpleTestCase):
    @mock.patch("thibaud.db.models.fields.router.allow_migrate", new=dummy_allow_migrate)
    def test_check_field(self):
        """Test if backend specific checks are performed."""
        error = Error("an error")

        class Model(models.Model):
            field = models.IntegerField()

        field = Model._meta.get_field("field")
        with mock.patch.object(
            connections["default"].validation, "check_field", return_value=[error]
        ):
            self.assertEqual(field.check(databases={"default"}), [error])
