import pytest
from shapely.geometry import Point

from geotortoise.utils import (
    longitude_is_valid,
    latitude_is_valid,
    validate_coordinates,
)
from geotortoise.exceptions import InvalidCoordinateError


@pytest.mark.parametrize(
    "geom, expected_result",
    [
        (Point(1000, 0), False),
        (Point(180.01, 0), False),
        (Point(-180.01, 0), False),
        (Point(180, 0), True),
        (Point(0, 0), True),
    ],
)
def test_longitude_is_valid(geom, expected_result):
    assert longitude_is_valid(geom.x) is expected_result


@pytest.mark.parametrize(
    "geom, expected_result",
    [
        (Point(0, 91.01), False),
        (Point(0, -90.01), False),
        (Point(0, 42), True),
        (Point(0, -42), True),
    ],
)
def test_latitude_is_valid(geom, expected_result):
    assert latitude_is_valid(geom.y) is expected_result


@pytest.mark.parametrize(
    "geom, expected_error",
    [
        (
            Point(1000, 0),
            "The longitude value 1000.0 is not valid. The value must be between -180 and 180, both bounds included.",
        ),
        (
            Point(0, -90.01),
            "The latitude value -90.01 is not valid. The value must be between -90 and 90, both bounds included.",
        ),
    ],
)
def test_invalid_coordinates_raises_proper_error(geom, expected_error):
    with pytest.raises(InvalidCoordinateError) as exc:
        validate_coordinates(geom)

    assert str(exc.value) == expected_error


@pytest.mark.parametrize(
    "geom",
    [Point(4, 89.0), Point(178, -8.01)],
)
def test_coordinates_validator_returns_same_geometry_when_coordinates_are_valid(geom):
    same_original_geometry = validate_coordinates(geom)

    assert same_original_geometry == geom
