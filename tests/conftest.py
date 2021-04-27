import logging
import sys

from tortoise import Tortoise

from .models import DB_URL, TEST_MODELS

LOGGING = False


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
            for model in Tortoise.apps["models"].values():
                await model.all().delete()
            await Tortoise.close_connections()

    return _setup_db


if LOGGING:
    fmt = logging.Formatter(
        fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt)

    # will print debug sql
    logger_db_client = logging.getLogger("db_client")
    logger_db_client.setLevel(logging.DEBUG)
    logger_db_client.addHandler(sh)

    logger_tortoise = logging.getLogger("tortoise")
    logger_tortoise.setLevel(logging.DEBUG)
    logger_tortoise.addHandler(sh)
