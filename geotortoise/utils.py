from shapely.geometry import Point
from .exceptions import InvalidCoordinateError


def validate_coordinates(geom: Point) -> bool:
    if not longitude_is_valid(geom.x):
        raise InvalidCoordinateError(
            f"The longitude value {geom.x} is not valid. The value must be between -180 and 180, both bounds included."
        )
    if not latitude_is_valid(geom.y):
        raise InvalidCoordinateError(
            f"The latitude value {geom.y} is not valid. The value must be between -90 and 90, both bounds included."
        )
    return geom


def longitude_is_valid(x: float) -> bool:
    return bool(-180 <= x <= 180)


def latitude_is_valid(y: float) -> bool:
    return bool(-90 <= y <= 90)
