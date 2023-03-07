from tortoise import fields
from tortoise.models import Model

from geotortoise import fields as geo_fields


class Region(Model):
    name = fields.CharField(max_length=250)
    poly = geo_fields.PolygonField()


class Place(Model):
    name = fields.CharField(max_length=250)
    point = geo_fields.PointField()


# ====================
# Test Config
# ====================
TEST_MODELS = ["tests.models", "aerich.models"]

DB_HOST = "0.0.0.0"
DB_URL = f"postgres://geo:geo@{DB_HOST}:5432/geo"

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": TEST_MODELS,
            "default_connection": "default",
        },
    },
}
