import pytest
from shapely.geometry import Point

from geotortoise.utils import longitude_is_valid, latitude_is_valid


@pytest.mark.parametrize(
    "geom, expected_result",
    [
        (Point(1000, 0), False),
        (Point(180.01, 0), False),
        (Point(-180.01, 0), False),
        (Point(180, 0), True),
        (Point(0, 0), True),
        
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
