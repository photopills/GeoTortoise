import pytest
from shapely.geometry import Point

from geotortoise.utils import longitude_is_valid


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
