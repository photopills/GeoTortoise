import uuid
from itertools import count
from typing import Any, List, Optional, Sequence

import asyncpg
from pypika import Parameter, Table
from pypika.terms import Term
from tortoise import Model
from tortoise.contrib.postgres.search import SearchCriterion
from tortoise.filters import search

from .base import BaseExecutor
from .._base_functions import Function


def postgres_search(field: Term, value: Term):
    return SearchCriterion(field, expr=value)


class AsyncpgExecutor(BaseExecutor):
    EXPLAIN_PREFIX = "EXPLAIN (FORMAT JSON, VERBOSE)"
    DB_NATIVE = BaseExecutor.DB_NATIVE | {bool, uuid.UUID}
    FILTER_FUNC_OVERRIDE = {search: postgres_search}

    def parameter(self, pos: int) -> Parameter:
        return Parameter("$%d" % (pos + 1,))

    def _prepare_insert_statement(
        self, columns: Sequence[str], has_generated: bool = True
    ) -> str:
        query = (
            self.db.query_class.into(self.model._meta.basetable)
            .columns(*columns)
            .insert(*[self.parameter(i) for i in range(len(columns))])
        )
        if has_generated:
            generated_fields = self.model._meta.generated_db_fields
            if generated_fields:
                query = query.returning(*generated_fields)
        return str(query)

    async def _process_insert_result(
        self, instance: Model, results: Optional[asyncpg.Record]
    ) -> None:
        if results:
            generated_fields = self.model._meta.generated_db_fields
            db_projection = instance._meta.fields_db_projection_reverse
            for key, val in zip(generated_fields, results):
                setattr(instance, db_projection[key], val)


# class PostGISExecutor(AsyncpgExecutor):
#     def _prepare_insert_statement(self, columns: List[str], values: List[Any]) -> str:
#         counter = count(1)

#         values = [
#             value.parameterize(lambda: f"${next(counter)}")
#             if isinstance(value, Function)
#             else Parameter(f"${next(counter)}")
#             for value in values
#         ]

#         return str(
#             self.db.query_class.into(Table(self.model._meta.table))
#             .columns(*columns)
#             .insert(*values)
#             .returning("id")
#         )
