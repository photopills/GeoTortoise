from typing import TYPE_CHECKING, Any, List

from pypika.queries import Query
from tortoise.backends.base.schema_generator import BaseSchemaGenerator
from tortoise.converters import encoders

from .._base_functions import func
from ..fields import GeometryField

if TYPE_CHECKING:  # pragma: nocoverage
    from .client import AsyncpgDBClient

    # from tortoise.backends.asyncpg.client import AsyncpgDBClient


class AsyncpgSchemaGenerator(BaseSchemaGenerator):
    DIALECT = "postgres"
    TABLE_COMMENT_TEMPLATE = "COMMENT ON TABLE \"{table}\" IS '{comment}';"
    COLUMN_COMMENT_TEMPLATE = 'COMMENT ON COLUMN "{table}"."{column}" IS \'{comment}\';'
    GENERATED_PK_TEMPLATE = '"{field_name}" {generated_sql}'

    def __init__(self, client: "AsyncpgDBClient") -> None:
        super().__init__(client)
        self.comments_array: List[str] = []

    @classmethod
    def _get_escape_translation_table(cls) -> List[str]:
        table = super()._get_escape_translation_table()
        table[ord("'")] = "''"
        return table

    def _table_comment_generator(self, table: str, comment: str) -> str:
        comment = self.TABLE_COMMENT_TEMPLATE.format(
            table=table, comment=self._escape_comment(comment)
        )
        self.comments_array.append(comment)
        return ""

    def _column_comment_generator(self, table: str, column: str, comment: str) -> str:
        comment = self.COLUMN_COMMENT_TEMPLATE.format(
            table=table, column=column, comment=self._escape_comment(comment)
        )
        if comment not in self.comments_array:
            self.comments_array.append(comment)
        return ""

    def _post_table_hook(self) -> str:
        val = "\n".join(self.comments_array)
        self.comments_array = []
        if val:
            return "\n" + val
        return ""

    def _column_default_generator(
        self,
        table: str,
        column: str,
        default: Any,
        auto_now_add: bool = False,
        auto_now: bool = False,
    ) -> str:
        default_str = " DEFAULT"
        if auto_now_add:
            default_str += " CURRENT_TIMESTAMP"
        else:
            default_str += f" {default}"
        return default_str

    def _escape_default_value(self, default: Any):
        if isinstance(default, bool):
            return default
        return encoders.get(type(default))(default)  # type: ignore


class PostGISSchemaGenerator(AsyncpgSchemaGenerator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _before_generate_sql(self, model):
        new_fields_db_projection = {}
        for k, v in model._meta.fields_db_projection.items():
            field_type = model._meta.fields_map[k]
            if isinstance(field_type, GeometryField):
                self.stripped_fields[model][k] = field_type
            else:
                new_fields_db_projection[k] = v

        model._meta.fields_db_projection = new_fields_db_projection

    def _after_generate_sql(self, table_data):
        if table_data["model"] in self.stripped_fields:
            for field_name, field_type in self.stripped_fields[
                table_data["model"]
            ].items():
                geometry_column_sql = str(
                    Query.select(
                        func.AddGeometryColumn(
                            table_data["table"],
                            field_name,
                            field_type.srid,
                            field_type.geometry_type.value,
                            2,
                        )
                    )
                )
                table_data["table_creation_string"] += f"{geometry_column_sql};"

            for k, v in self.stripped_fields[table_data["model"]].items():
                table_data["model"]._meta.fields_db_projection[k] = v.model_field_name
