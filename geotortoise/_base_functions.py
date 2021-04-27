"""
Implements arbitrary SQL functions using getattr.

Inspired by the SQLAlchemy function implementation.
"""
from typing import Callable, Union

from pypika.functions import Function as PyPikaFunction
from pypika.terms import Criterion, Field, Parameter
from tortoise.query_utils import Q, QueryModifier


class FunctionCriterion(Criterion):
    def __init__(self, function: "Function", alias=None):
        # TODO: Check how to pass the alias
        super().__init__(alias)
        self.function = function

    def fields(self):
        return [x for x in self.function.args if isinstance(x, Field)]

    def get_sql(self, with_alias=False, **kwargs):
        sql = self.function.get_function_sql()
        if with_alias and self.alias:
            return f'{sql} "{self.alias}"'
        return sql


class Function(PyPikaFunction, Q):
    def __init__(self, name, *args, **kwargs):
        self._parameters = args
        PyPikaFunction.__init__(self, name, *args, **kwargs)
        Q.__init__(self)

    def resolve(self, model, annotations, custom_filters, *args):
        # TODO: Get more information about *args param
        return QueryModifier(where_criterion=FunctionCriterion(self))

    def parameterize(self, placeholder: Union[str, Callable]):
        """
        Parametrizes a function so that the SQL engine may insert the values later.

        :param placeholder: The placeholder, or a function to derive the placeholder.
        """
        return Function(
            self.name,
            *[
                Parameter(placeholder() if callable(placeholder) else placeholder)
                for _ in self.args
            ],
        )

    @property
    def parameters(self):
        return self._parameters


class _FunctionBuilder:
    def __init__(self, name=None):
        self.name = name

    def __call__(self, *args, **kwargs):
        return Function(self.name, *args, **kwargs)

    def __getattr__(self, name):
        return _FunctionBuilder(name)


func = _FunctionBuilder()
