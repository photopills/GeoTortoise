from itertools import chain
from typing import Optional, Union

from pypika import Field as PyPikaField
from shapely.geometry.base import BaseGeometry
from tortoise.fields import Field

from ._base_functions import Function

# ====================
# PostGIS transformation operations
# ====================

# TODO: Add GeoJSON support


class GeomFromText(Function):
    """Generates geometry from well known text."""

    def __init__(self, wkt: str, srid: Optional[int] = None, alias=None):
        """
        Generate geometry from the given well-known text.
        :param wkt: The well-known text to insert.
        :param srid: The (optional) SRID to interpret it as..
        :param alias: The alias for the function.
        """
        args = filter(lambda x: x is not None, (wkt, srid))
        super().__init__("ST_GeomFromText", *args, alias=alias)


class AsText(Function):
    """PostGIS function to extract geometry as WKT"""

    def __init__(self, field: Field, alias):
        super().__init__("ST_AsText", field, alias)


# ====================
# Comparative geospatial functions
# ====================

GeometryLike = Union[BaseGeometry, "GeomFromText", Field, str]


def convert_to_db_value(target: GeometryLike, srid=None):
    if isinstance(target, BaseGeometry):
        return GeomFromText(target.wkt, srid)
    if isinstance(target, str):
        return GeomFromText(target, srid)
        # todo validate wkb
    if isinstance(target, Field):
        return PyPikaField(target.model_field_name)
    return target


class ComparesGeometryLike(Function):
    """
    The set of functions that compare two geometry-like objects.
    """

    name = None

    def __init__(
        self,
        g1: Optional[GeometryLike] = None,
        g2: Optional[GeometryLike] = None,
        g1_srid=None,
        g2_srid=None,
        **kwargs
    ):
        """
        Accepts either two geometry-like objects, or a single key-value
        where the key is a field to look up, and the value is the geometry-like
        to compare against.

        :param g1: The object to check.
        :param g2: The object you want to check contains the first.
        :param g1_srid: The optional srid of the object.
        :param g2_srid: The optional srid of the container.
        :param kwargs: An optional single key and value to filter against a field.
        """

        if g1 and g2 and not kwargs:
            g1 = convert_to_db_value(g1, g1_srid)
            g2 = convert_to_db_value(g2, g2_srid)
        elif len(kwargs) == 1:
            field, target = chain.from_iterable(kwargs.items())
            g1 = PyPikaField(field)
            g2 = convert_to_db_value(target, g2_srid)
        else:
            raise TypeError(
                "This function accepts exactly 2 GeometryLikes or a single key-value."
            )

        super().__init__(self.name, g1, g2)


class ST_Equals(ComparesGeometryLike):
    """Calculates whether the supplied GeometryLikes are the same."""

    name = "ST_Equals"


class ST_Disjoint(ComparesGeometryLike):
    """Calculates whether the supplied GeometryLikes are disjoint."""

    name = "ST_Disjoint"


class ST_Touches(ComparesGeometryLike):
    """Calculates whether one GeometryLike touches another."""

    name = "ST_Touches"


class ST_Within(ComparesGeometryLike):
    """Calculates whether the first GeometryLike is completely contained in the 2nd."""

    name = "ST_Within"


class ST_Overlaps(ComparesGeometryLike):
    """Calculates whether the first GeometryLike overlaps with the 2nd."""

    name = "ST_Overlaps"


class ST_Contains(ComparesGeometryLike):
    """Calculates whether the first GeometryLike completely contains the 2nd."""

    name = "ST_Contains"


class ST_Distance(ComparesGeometryLike):
    """Calculates the minimum 2D Cartesian (planar) distance between two GeometryLikes,
    in projected units (spatial ref units)."""

    name = "ST_Distance"


class ST_DistanceSphere(ComparesGeometryLike):
    """Calculates minimum distance in meters between two lon/lat GeometryLikes."""

    name = "ST_DistanceSphere"


class ST_Intersection(ComparesGeometryLike):
    """Calculates the intersecting geometry from the two GeometryLikes."""

    name = "ST_Intersection"


class ST_Difference(ComparesGeometryLike):
    """Calculates the differing geometry from the two GeometryLikes."""

    name = "ST_Difference"


class ST_Union(ComparesGeometryLike):
    """Calculates the union of the two GeometryLikes."""

    name = "ST_Union"


class ST_ClosestPoint(ComparesGeometryLike):
    """Calculates the point on the first GeometryLike that is closes to the 2nd."""

    name = "ST_ClosestPoint"
