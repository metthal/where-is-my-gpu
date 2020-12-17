#!/usr/bin/env python3

import asyncio
import aioredis
import importlib
import os
import sys

from pyhocon import ConfigFactory


config = ConfigFactory.parse_file("config.conf")
sys.path.append("migrations")


async def main():
    migrations = []
    for root, dirs, files in os.walk("migrations"):
        for f in files:
            migration_id = int(f.split("_")[0])
            migrations.append((migration_id, f[:-3], os.path.join(root, f)))

    migrations = sorted(migrations)

    try:
        redis = await aioredis.create_redis_pool(
            "redis://{}:{}".format(
                config["redis"]["hostname"],
                config["redis"]["port"]
            ),
            db=config["redis"]["db"]
        )


        start_with_migration = 0
        schema = await redis.get("schema")
        if schema is not None:
            start_with_migration = int(schema) + 1
        else:
            # Hack to enforce the schema version
            await redis.set("schema", 0)

        if start_with_migration <= max([id for id, _, _ in migrations]):
            for index, (id, name, script) in enumerate(migrations):
                if id == start_with_migration:
                    migrations = migrations[index:]
                    break
        else:
            migrations.clear()

        for id, name, script in migrations:
            migration = importlib.import_module(name)
            print(f"Applying migration '{name}'...")
            await migration.apply(redis)
            await redis.set("schema", id)
    except Exception as err:
        print(repr(err))
    finally:
        redis.close()
        await redis.wait_closed()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
