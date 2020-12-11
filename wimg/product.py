import pickle

from datetime import datetime
from typing import List, Tuple


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
        return "{} [{}] [{}] [{}]".format(self.id, self.name, "Out of Stock" if self.stock is None else f"In Stock ({self.stock})", f"{self.price} CZK" if self.price is not None else "No Price")

    async def save(self, redis):
        await redis.set(self.id, pickle.dumps(self))

    @classmethod
    async def load(cls, redis, id):
        result = await redis.get(id)
        if result is None:
            return None
        return pickle.loads(result)

    @classmethod
    async def load_multiple(cls, redis, ids):
        return [pickle.loads(result) for result in await redis.mget(*ids)]

    def to_tuple(self):
        return (
            self.id,
            self.name,
            self.link,
            self.price,
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
