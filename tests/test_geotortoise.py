from shapely.geometry import Point, Polygon

from geotortoise.functions import ST_Contains, ST_Distance, ST_Within
from tests.models import Place, Region

from .conftest import db_handler

# TODO: Create model objects as fixtures
test_region = Polygon(
    [
        [2.6312255859375, 41.86547012230937],
        [3.0157470703125, 41.86547012230937],
        [3.0157470703125, 42.12674735753131],
        [2.6312255859375, 42.12674735753131],
        [2.6312255859375, 41.86547012230937],
    ]
)
other_region = [
    pt[::-1]
    for pt in [
        [2.6312255859375, 41.86547012230937],
        [3.0157470703125, 41.86547012230937],
        [3.0157470703125, 42.12674735753131],
        [2.6312255859375, 42.12674735753131],
        [2.6312255859375, 41.86547012230937],
    ]
]

test_other_region = Polygon(other_region)

test_place = Point(2.828787714242935, 41.98668181757302)
test_obstacle = Point(2.8292490541934967, 41.9864914201914)


@db_handler
async def test_create_place():
    await Place.create(name="Girona", point=Point(23, 10))
    assert await Place.all().count() == 1


@db_handler
async def test_create_region():
    await Region.create(name="Girona", poly=test_region)

    assert await Region.all().count() == 1
    assert (await Region.first()).poly == test_region


@db_handler
async def test_st_contains():
    await Region.create(name="Girona", poly=test_region)
    await Region.create(name="Other region", poly=test_other_region)
    qs = await Region.filter(ST_Contains(Region._meta.fields_map["poly"], test_place))

    assert await Region.all().count() == 2
    # only one region contains the point
    assert len(qs) == 1


@db_handler
async def test_st_within():
    await Place.create(name="Garden", point=test_place)
    await Place.create(
        name="Other Place", point=Point(41.9864914201914, 2.8292490541934967)
    )

    qs = await Place.filter(ST_Within(Place._meta.fields_map["point"], test_region))

    assert await Place.all().count() == 2
    # only one place within the passed region
    assert len(qs) == 1


@db_handler
async def test_st_distance():
    pt = await Place.create(name="Garden", point=test_place)
    distance = await Place.annotate(distance=ST_Distance(pt.point, test_obstacle))
    # TODO: Return value in Km unit
    assert distance[0].distance == 0.0004990848754603494

