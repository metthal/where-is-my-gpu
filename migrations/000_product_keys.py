# Turns product keys in redis from just "ID" into "product:ID"

import re


async def apply(redis):
    VALID_KEY_RE = re.compile("[0-9]+")

    all_keys = []
    cursor = b"0"
    while cursor:
        cursor, keys = await redis.scan(cursor, match="*")
        all_keys.extend([key.decode("utf-8") for key in keys if VALID_KEY_RE.fullmatch(key.decode("utf-8"))])

    for key in all_keys:
        print(f"migrate_produt_keys: Migrating key '{key}'...")
        await redis.set(f"product:{key}", await redis.get(key))
        await redis.delete(key)
