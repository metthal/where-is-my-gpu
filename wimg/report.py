import discord

from typing import Optional

from wimg.product import Product


POSITIVE_COLOR = 0x00d759
NEGATIVE_COLOR = 0xd10024


class Report:
    def __init__(self, product: Product):
        self.product = product
        self.old_product = None

    def create_message(self):
        result = discord.Embed(title=self.product.name, url=self.product.link, description=" | ".join(f"[{name}]({link})" for name, link in self.product.additional_urls))
        result.set_thumbnail(url=self.product.image_url)
        if self.old_product and self.product.price != self.old_product.price:
            result.insert_field_at(0, name=f"New price: {self.product.price} CZK", value=f"Previous price: {self.old_product.price} CZK" if self.old_product is not None else "", inline=False)
            result.color = POSITIVE_COLOR if self.old_product.price is None or self.product.price < self.old_product.price else NEGATIVE_COLOR
        if self.old_product and self.product.stock != self.old_product.stock:
            out_of_stock = self.product.stock is None
            result.insert_field_at(0, name="Out of stock" if out_of_stock else "In stock", value="Out of stock" if out_of_stock else f"Pieces: {self.product.stock}", inline=False)
            result.color = POSITIVE_COLOR if not out_of_stock else NEGATIVE_COLOR
        return result if len(result.fields) > 0 else None
