# Turns product keys in redis from just "ID" into "product:ID"

import aioredis
import asyncio
import re

from pyhocon import ConfigFactory


config = ConfigFactory.parse_file("config.conf")

VALID_KEY_RE = re.compile("[0-9]+")

async def main():
    try:
        redis = await aioredis.create_redis_pool(
            "redis://{}:{}".format(
                config["redis"]["hostname"],
                config["redis"]["port"]
            ),
            db=config["redis"]["db"]
        )

        all_keys = []
        cursor = b"0"
        while cursor:
            cursor, keys = await redis.scan(cursor, match="*")
            all_keys.extend([key.decode("utf-8") for key in keys if VALID_KEY_RE.fullmatch(key.decode("utf-8"))])

        for key in all_keys:
            print(f"migrate_produt_keys: Migrating key '{key}'...")
            await redis.set(f"product:{key}", await redis.get(key))
            await redis.delete(key)
    except Exception as err:
        print(repr(err))
    finally:
        redis.close()
        await redis.wait_closed()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
