import pickle

from datetime import datetime
from typing import List, Tuple

from wimg.utils import remove_prefix


CZK_EUR_EXCHANGE_RATE = 25.5


class Product:
    def __init__(self, id: int, name: str, link: str, price: int, stock: str, image_url: str, additional_urls: List[Tuple[str, str]] = None):
        self.id = id
        self.name = name
        self.link = link
        self.price = price
        self.stock = stock
        self.image_url = image_url
        self.additional_urls = additional_urls if additional_urls is not None else []
        self.last_seen = datetime.now()

    def __str__(self):
        return "{} [{}] [{}] [{}] [{}]".format(self.id, self.name, "Out of Stock" if self.stock is None else f"In Stock ({self.stock})", self.price_with_currency, self.last_seen)

    @property
    def price_with_currency(self):
        return "No Price" if self.price is None else "{} CZK ({} EUR)".format(self.price, int(self.price / CZK_EUR_EXCHANGE_RATE))

    @property
    def out_of_stock(self):
        return self.stock is None

    @property
    def readable_stock(self):
        return f"In Stock ({self.stock})" if self.stock is not None else "Out of Stock"

    async def save(self, redis):
        await redis.set(f"product:{self.id}", pickle.dumps(self))
        await redis.set(f"product_name:{self.name.lower()}", self.id)

    @classmethod
    async def load(cls, redis, id):
        result = await redis.get(f"product:{id}")
        if result is None:
            return None
        return pickle.loads(result)

    @classmethod
    async def load_multiple(cls, redis, ids):
        if len(ids) == 0:
            return []
        return [pickle.loads(result) for result in await redis.mget(*[f"product:{id}" for id in ids]) if result is not None]

    @classmethod
    async def load_all(cls, redis):
        all_keys = []
        cursor = b"0"
        while cursor:
            cursor, keys = await redis.scan(cursor, match="product:*")
            all_keys.extend([remove_prefix("product:", key.decode("utf-8")) for key in keys])
        return await cls.load_multiple(redis, all_keys)

    @classmethod
    async def find(cls, redis, name):
        result_id = await redis.get(f"product_name:{name.lower()}")
        if result_id is None:
            return None
        return await cls.load(redis, int(result_id))

    def to_tuple(self):
        return (
            self.id,
            self.name,
            self.link,
            self.price_with_currency,
            self.stock,
            self.last_seen
        )

    @staticmethod
    def tuple_headers():
        return [
            "ID",
            "Name",
            "Link",
            "Price",
            "Stock",
            "Last Seen"
        ]


class NoProduct:
    def __init__(self):
        self.name = "<No Product>"
        self.price = None
        self.stock = None

    def __str__(self):
        return self.name

    @property
    def price_with_currency(self):
        return "No Price"

    @property
    def out_of_stock(self):
        return True

    @property
    def readable_stock(self):
        return "Did Not Exist"
