import pickle

from wimg.product import Product
from wimg.utils import remove_prefix


class User:
    def __init__(self, id: int):
        self.id = id
        self.subscribed = set()

    def is_subscribed_for(self, product: Product):
        return product.id in self.subscribed

    async def save(self, redis):
        await redis.set(f"user:{self.id}", pickle.dumps(self))

    @classmethod
    async def load(cls, redis, id: int):
        result = await redis.get(f"user:{id}")
        if result is None:
            return None
        return pickle.loads(result)

    @classmethod
    async def load_multiple(cls, redis, ids):
        if len(ids) == 0:
            return []
        return [pickle.loads(result) for result in await redis.mget(*[f"user:{id}" for id in ids]) if result is not None]

    @classmethod
    async def load_all(cls, redis):
        all_keys = []
        cursor = b"0"
        while cursor:
            cursor, keys = await redis.scan(cursor, match="user:*")
            all_keys.extend([remove_prefix("user:", key.decode("utf-8")) for key in keys])
        return await cls.load_multiple(redis, all_keys)
