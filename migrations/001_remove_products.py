# Remove products which are no longer loadable

import pickle

from wimg.price import Price


async def apply(redis):
    all_keys = []
    cursor = b"0"
    while cursor:
        cursor, keys = await redis.scan(cursor, match="product:*")
        all_keys.extend(keys)

    for key in all_keys:
        data = await redis.get(key)
        try:
            product = pickle.loads(data)
            if not isinstance(product.price, Price):
                raise ValueError
        except Exception:
            print(f"Removing {key.decode('utf-8')}...")
            await redis.delete(key)
