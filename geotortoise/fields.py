from typing import Any, Type, Union

import shapely.wkb
import shapely.wkt
from shapely.errors import WKBReadingError, WKTReadingError
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry
from tortoise import ConfigurationError, Model
from tortoise.exceptions import FieldError, OperationalError
from tortoise.fields import Field

from .functions import AsText


class GeometryField(Field):
    """
    Base Geometry Field.

    To save a data to the database, it **MUST** be either a string containing
    its Well-Known Text (WKT) value or a Shapely Geometry instance.

    Columns defined with restrictions, such as :class:`PointField`, will **ONLY** accept
    data that conform to the restricted geometry. For example, if a Polygon
    is provided as data to a :class:`PointField`, it **WILL** raise an error
    on the database.

    If there is the need to store different types of geometries in the same column,
    consider using this class directly instead of any of its children.

    :param srid: Defines the projection system of the geometry.
        Most applications dealing with coordinates in the form *(longitude, latitude)*
        will want to use **EPSG:4326** (aka **WSG84**) as the *SRID*.

        There are cases where the application is dealing
        with absolute distances in meters.
        In those cases, it is **SUGGESTED** to use a **UTM** coordinate system,
        such as **EPSG:32723**.

        If no value is provided, the database will set the *SRID*
        of the column as unknown. In this case, the sole responsibility of casting
        the values belong to the application.
    :type srid: int

    :param spatial_index: Defines whether the column will have a Spatial Index.
        This index is created by defining an index using *GIST* on the column.
        The default is True.
    :type spatial_index: bool
    """

    SQL_TYPE: str = "GEOMETRY"

    def __init__(
        self,
        srid: int = None,
        spatial_index: bool = True,
        **kwargs: Any,
    ) -> None:
        self.srid = srid
        self.spatial_index = spatial_index
        super().__init__(**kwargs)

    def to_db_value(
        self,
        value: BaseGeometry,
        instance: Union[Type[Model], Model],
    ) -> str:
        if value is None:
            return value

        if not isinstance(value, BaseGeometry):
            try:
                value = shapely.wkt.loads(value)
            except WKTReadingError:    
                raise FieldError("The value to be saved must be a Shapely geometry or a WKT geometry.")

        return shapely.wkb.dumps(value, hex=True, srid=self.srid)

    def to_python_value(self, value: Any) -> BaseGeometry:
        if value is None or isinstance(value, BaseGeometry):
            return value

        if not isinstance(value, (bytes, str)):
            raise FieldError(f'Invalid type: "{type(value)}", expected "bytes or str".')

        if isinstance(value, bytes):
            try:
                return shapely.wkb.loads(value)
            except WKBReadingError as exc:
                raise OperationalError("Could not parse the provided data.") from exc

        try:
            int(value, 16)  # Prevents "ParseException: Invalid HEX char."
            return shapely.wkb.loads(value, hex=True)
        except (ValueError, WKBReadingError):
            pass

        try:
            return shapely.wkt.loads(value)
        except WKTReadingError:
            pass

        raise OperationalError("Could not parse the provided data.")

    def get_sql(self, quote_char="", *args, **kwargs):
        return quote_char + self.model_field_name + quote_char

    def get_select(self, capabilities, table):
        try:
            return AsText(super().get_select(capabilities, table)).as_(
                self.model_field_name
            )
        except KeyError:
            raise ConfigurationError("Dialect does not support geospatial data!")


class PointField(GeometryField):
    """
    Point field.

    This field is used to save points in the format (longitude, latitude).
    """

    field_type = Point

    @property
    def SQL_TYPE(self) -> str:
        return f"GEOMETRY(POINT,{self.srid})" if self.srid else "GEOMETRY(POINT)"


class PolygonField(GeometryField):
    """
    Polygon field.

    This field is used to save a polygon. It takes at least three points to create
    a polygon. The polygon can have one shell and one or more holes inside the shell.
    """

    field_type = Polygon

    @property
    def SQL_TYPE(self) -> str:
        return f"GEOMETRY(POLYGON,{self.srid})" if self.srid else "GEOMETRY(POLYGON)"
