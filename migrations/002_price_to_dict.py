# Migrate prices to dicts

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
        product = pickle.loads(data)
        if isinstance(product.price.values, list):
            print(f"Changing prices from list to dict for '{product.name}'...")
            product.price.values = { price.currency: price for price in product.price.values }
            await product.save(redis)
        elif isinstance(product.price, str):
            print(f"Changing prices from str to dict for '{product.name}'...")
            product.price = Price()
            await produce.save(redis)
