import warnings

from django.db import NotSupportedError
from django.db.models.expressions import Func, Value
from django.db.models.fields import CharField, IntegerField, TextField
from django.db.models.functions import Cast, Coalesce
from django.db.models.lookups import Transform
from django.utils.deprecation import RemovedInDjango60Warning


class MySQLSHA2Mixin:
    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="SHA2(%%(expressions)s, %s)" % self.function[3:],
            **extra_context,
        )


class OracleHashMixin:
    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template=(
                "LOWER(RAWTOHEX(STANDARD_HASH(UTL_I18N.STRING_TO_RAW("
                "%(expressions)s, 'AL32UTF8'), '%(function)s')))"
            ),
            **extra_context,
        )


class PostgreSQLSHAMixin:
    def as_postgresql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="ENCODE(DIGEST(%(expressions)s, '%(function)s'), 'hex')",
            function=self.function.lower(),
            **extra_context,
        )


class Chr(Transform):
    function = "CHR"
    lookup_name = "chr"
    output_field = CharField()

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            function="CHAR",
            template="%(function)s(%(expressions)s USING utf16)",
            **extra_context,
        )

    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template="%(function)s(%(expressions)s USING NCHAR_CS)",
            **extra_context,
        )

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="CHAR", **extra_context)


class Concat(Func):
    """
    Concatenate expressions together into a string.

    Handle nulls and non-textual expressions gracefully.
    """

    function = None
    template = "%(expressions)s"
    arg_joiner = " || "

    def __init__(self, *expressions, **extra):
        if len(expressions) < 2:
            raise ValueError("Concat must take at least two expressions")
        super().__init__(*expressions, **extra)

    def as_mysql(self, compiler, connection):
        # MySQL || operator is an alias for OR unless PIPES_AS_CONCAT is enabled.
        return Func(Value(""), *self.source_expressions, function="CONCAT_WS").as_sql(
            compiler, connection
        )

    def as_sql(self, compiler, connection, **extra_context):
        copy = self.copy()
        source_expressions = copy.get_source_expressions()
        if connection.features.requires_casted_text_in_pipes_concat:
            source_expressions = [
                expr
                if isinstance(expr.output_field, (CharField, TextField))
                else Cast(expr, TextField())
                for expr in source_expressions
            ]
        # Systematically coalesce source expression to empty strings because
        # their nullability cannot be accurately inferred.
        if not connection.features.interprets_empty_strings_as_nulls:
            source_expressions = [
                Coalesce(expr, Value("")) for expr in source_expressions
            ]
        copy.set_source_expressions(source_expressions)
        return super(Concat, copy).as_sql(compiler, connection, **extra_context)


class ConcatPair(Concat):
    def __init__(self, *expressions, **extra):
        # RemovedInDjango60Warning.
        warnings.warn(
            "ConcatPair is deprecated, use Concat instead.",
            category=RemovedInDjango60Warning,
            stacklevel=2,
        )
        super().__init__(*expressions, **extra)


class Left(Func):
    function = "LEFT"
    arity = 2
    output_field = CharField()

    def __init__(self, expression, length, **extra):
        """
        expression: the name of a field, or an expression returning a string
        length: the number of characters to return from the start of the string
        """
        if not hasattr(length, "resolve_expression"):
            if length < 1:
                raise ValueError("'length' must be greater than 0.")
        super().__init__(expression, length, **extra)

    def get_substr(self):
        return Substr(self.source_expressions[0], Value(1), self.source_expressions[1])

    def as_oracle(self, compiler, connection, **extra_context):
        return self.get_substr().as_oracle(compiler, connection, **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        return self.get_substr().as_sqlite(compiler, connection, **extra_context)


class Length(Transform):
    """Return the number of characters in the expression."""

    function = "LENGTH"
    lookup_name = "length"
    output_field = IntegerField()

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection, function="CHAR_LENGTH", **extra_context
        )


class Lower(Transform):
    function = "LOWER"
    lookup_name = "lower"


class LPad(Func):
    function = "LPAD"
    output_field = CharField()

    def __init__(self, expression, length, fill_text=Value(" "), **extra):
        if (
            not hasattr(length, "resolve_expression")
            and length is not None
            and length < 0
        ):
            raise ValueError("'length' must be greater or equal to 0.")
        super().__init__(expression, length, fill_text, **extra)


class LTrim(Transform):
    function = "LTRIM"
    lookup_name = "ltrim"


class MD5(OracleHashMixin, Transform):
    function = "MD5"
    lookup_name = "md5"


class Ord(Transform):
    function = "ASCII"
    lookup_name = "ord"
    output_field = IntegerField()

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="ORD", **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="UNICODE", **extra_context)


class Repeat(Func):
    function = "REPEAT"
    output_field = CharField()

    def __init__(self, expression, number, **extra):
        if (
            not hasattr(number, "resolve_expression")
            and number is not None
            and number < 0
        ):
            raise ValueError("'number' must be greater or equal to 0.")
        super().__init__(expression, number, **extra)

    def as_oracle(self, compiler, connection, **extra_context):
        expression, number = self.source_expressions
        length = None if number is None else Length(expression) * number
        rpad = RPad(expression, length, expression)
        return rpad.as_sql(compiler, connection, **extra_context)


class Replace(Func):
    function = "REPLACE"

    def __init__(self, expression, text, replacement=Value(""), **extra):
        super().__init__(expression, text, replacement, **extra)


class Reverse(Transform):
    function = "REVERSE"
    lookup_name = "reverse"

    def as_oracle(self, compiler, connection, **extra_context):
        # REVERSE in Oracle is undocumented and doesn't support multi-byte
        # strings. Use a special subquery instead.
        sql, params = super().as_sql(
            compiler,
            connection,
            template=(
                "(SELECT LISTAGG(s) WITHIN GROUP (ORDER BY n DESC) FROM "
                "(SELECT LEVEL n, SUBSTR(%(expressions)s, LEVEL, 1) s "
                "FROM DUAL CONNECT BY LEVEL <= LENGTH(%(expressions)s)) "
                "GROUP BY %(expressions)s)"
            ),
            **extra_context,
        )
        return sql, params * 3


class Right(Left):
    function = "RIGHT"

    def get_substr(self):
        return Substr(
            self.source_expressions[0],
            self.source_expressions[1] * Value(-1),
            self.source_expressions[1],
        )


class RPad(LPad):
    function = "RPAD"


class RTrim(Transform):
    function = "RTRIM"
    lookup_name = "rtrim"


class SHA1(OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = "SHA1"
    lookup_name = "sha1"


class SHA224(MySQLSHA2Mixin, PostgreSQLSHAMixin, Transform):
    function = "SHA224"
    lookup_name = "sha224"

    def as_oracle(self, compiler, connection, **extra_context):
        raise NotSupportedError("SHA224 is not supported on Oracle.")


class SHA256(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = "SHA256"
    lookup_name = "sha256"


class SHA384(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = "SHA384"
    lookup_name = "sha384"


class SHA512(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = "SHA512"
    lookup_name = "sha512"


class StrIndex(Func):
    """
    Return a positive integer corresponding to the 1-indexed position of the
    first occurrence of a substring inside another string, or 0 if the
    substring is not found.
    """

    function = "INSTR"
    arity = 2
    output_field = IntegerField()

    def as_postgresql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="STRPOS", **extra_context)


class Substr(Func):
    function = "SUBSTRING"
    output_field = CharField()

    def __init__(self, expression, pos, length=None, **extra):
        """
        expression: the name of a field, or an expression returning a string
        pos: an integer > 0, or an expression returning an integer
        length: an optional number of characters to return
        """
        if not hasattr(pos, "resolve_expression"):
            if pos < 1:
                raise ValueError("'pos' must be greater than 0")
        expressions = [expression, pos]
        if length is not None:
            expressions.append(length)
        super().__init__(*expressions, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="SUBSTR", **extra_context)

    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function="SUBSTR", **extra_context)


class Trim(Transform):
    function = "TRIM"
    lookup_name = "trim"


class Upper(Transform):
    function = "UPPER"
    lookup_name = "upper"
