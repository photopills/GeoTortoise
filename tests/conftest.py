import asyncio

import pytest
from tortoise import Tortoise, run_async
from tortoise.contrib.test import finalizer, initializer

from .models import DB_URL, TEST_MODELS, Place, Region


def db_handler(func_test):
    async def _setup_db(*args, **kwargs):
        try:
            await Tortoise.init(
                db_url=DB_URL,
                modules={"models": TEST_MODELS},
            )
            # call the test function
            await func_test()
        finally:
            await Place.all().delete()
            await Region.all().delete()
            await Tortoise.close_connections()

    return _setup_db
