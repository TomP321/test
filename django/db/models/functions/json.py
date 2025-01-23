from django.db import NotSupportedError
from django.db.models.expressions import Case, Func, Value, When
from django.db.models.fields import TextField
from django.db.models.fields.json import JSONField
from django.db.models.functions import Cast
from django.db.models.lookups import IsNull


class JSONArray(Func):
    function = "JSON_ARRAY"
    output_field = JSONField()

    def __init__(self, *expressions, absent_on_null=False):
        self.absent_on_null = absent_on_null
        super().__init__(*expressions)

    def _absent_on_null_workaround(self, *, compiler, connection, **kwargs):
        # On backends that do not support ABSENT ON NULL, we can implement the behavior
        # so long as the backend has a way to concatenate JSON arrays.
        unit_arrays = [
            Case(
                When(IsNull(expression, True), then=JSONArray()),
                default=JSONArray(expression),
            )
            for expression in self.get_source_expressions()
        ]

        if len(unit_arrays) == 0:
            return super().as_sql(
                compiler,
                connection,
            )

        if len(unit_arrays) == 1:
            return unit_arrays[0].as_sql(
                compiler,
                connection,
            )

        return Func(
            *unit_arrays,
        ).as_sql(
            compiler,
            connection,
            **kwargs,
        )

    def as_sql(self, compiler, connection, **extra_context):
        if not connection.features.supports_json_field:
            raise NotSupportedError(
                "JSONFields are not supported on this database backend."
            )
        if self.absent_on_null and not connection.features.supports_json_absent_on_null:
            raise NotSupportedError(
                "ABSENT ON NULL is not supported by this database backend."
            )
        return super().as_sql(compiler, connection, **extra_context)

    def as_mysql(self, compiler, connection, **extra_context):
        if self.absent_on_null:
            return self._absent_on_null_workaround(
                compiler=compiler,
                connection=connection,
                function="JSON_MERGE_PRESERVE",
            )

        return super().as_sql(compiler, connection, **extra_context)

    def as_native(self, compiler, connection, *, returning, **extra_context):
        # Providing the ON NULL clause when no source expressions are provided is a
        # syntax error on some backends.
        if len(self.get_source_expressions()) == 0:
            on_null_clause = ""
        elif self.absent_on_null:
            on_null_clause = "ABSENT ON NULL"
        else:
            on_null_clause = "NULL ON NULL"

        return self.as_sql(
            compiler,
            connection,
            template=(
                f"%(function)s(%(expressions)s {on_null_clause} RETURNING {returning})"
            ),
            **extra_context,
        )

    def as_postgresql(self, compiler, connection, **extra_context):
        # Casting source expressions is only required using JSONB_BUILD_ARRAY
        # or when using JSON_ARRAY on PostgreSQL 16+ with server-side bindings.
        # This is done in all cases for consistency.
        casted_obj = self.copy()
        casted_obj.set_source_expressions(
            [
                (
                    # Conditional Cast to avoid unnecessary wrapping.
                    expression
                    if isinstance(expression, Cast)
                    else Cast(expression, expression.output_field)
                )
                for expression in casted_obj.get_source_expressions()
            ]
        )

        if connection.features.is_postgresql_16:
            return casted_obj.as_native(
                compiler, connection, returning="JSONB", **extra_context
            )

        if self.absent_on_null:
            return casted_obj._absent_on_null_workaround(
                compiler=compiler,
                connection=connection,
                template="(%(expressions)s)",
                arg_joiner=" || ",
            )

        return casted_obj.as_sql(
            compiler,
            connection,
            function="JSONB_BUILD_ARRAY",
            **extra_context,
        )

    def as_oracle(self, compiler, connection, **extra_context):
        return self.as_native(compiler, connection, returning="CLOB", **extra_context)


class JSONObject(Func):
    function = "JSON_OBJECT"
    output_field = JSONField()

    def __init__(self, **fields):
        expressions = []
        for key, value in fields.items():
            expressions.extend((Value(key), value))
        super().__init__(*expressions)

    def as_sql(self, compiler, connection, **extra_context):
        if not connection.features.has_json_object_function:
            raise NotSupportedError(
                "JSONObject() is not supported on this database backend."
            )
        return super().as_sql(compiler, connection, **extra_context)

    def join(self, args):
        pairs = zip(args[::2], args[1::2], strict=True)
        # Wrap 'key' in parentheses in case of postgres cast :: syntax.
        return ", ".join([f"({key}) VALUE {value}" for key, value in pairs])

    def as_native(self, compiler, connection, *, returning, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            arg_joiner=self,
            template=f"%(function)s(%(expressions)s RETURNING {returning})",
            **extra_context,
        )

    def as_postgresql(self, compiler, connection, **extra_context):
        # Casting keys to text is only required when using JSONB_BUILD_OBJECT
        # or when using JSON_OBJECT on PostgreSQL 16+ with server-side bindings.
        # This is done in all cases for consistency.
        copy = self.copy()
        copy.set_source_expressions(
            [
                Cast(expression, TextField()) if index % 2 == 0 else expression
                for index, expression in enumerate(copy.get_source_expressions())
            ]
        )

        if connection.features.is_postgresql_16:
            return copy.as_native(
                compiler, connection, returning="JSONB", **extra_context
            )

        return super(JSONObject, copy).as_sql(
            compiler,
            connection,
            function="JSONB_BUILD_OBJECT",
            **extra_context,
        )

    def as_oracle(self, compiler, connection, **extra_context):
        return self.as_native(compiler, connection, returning="CLOB", **extra_context)
