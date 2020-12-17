import discord
import logging

from typing import Optional, Union

from wimg.product import Product, NoProduct


POSITIVE_COLOR = 0x00d759
NEGATIVE_COLOR = 0xd10024


class Report:
    def __init__(self, channel_id: int, product: Product, old_product: Union[Product, NoProduct] = None, force_change: bool = False):
        self.channel_id = channel_id
        self.product = product
        self.old_product = old_product or NoProduct()
        self.changes = []
        self.positive = True

        if self.product.price != self.old_product.price:
            if not self.old_product.price:
                self.positive = True
            elif not self.product.price:
                self.positive = False
            else:
                self.positive = self.product.price < self.old_product.price
            self.changes.append("price")

        if (self.product.out_of_stock and self.old_product.stock) or (self.product.stock and self.old_product.out_of_stock):
            self.positive = not self.product.out_of_stock
            self.changes.append("stock")

        if force_change:
            self.changes.append("forced")

    @property
    def any_changes(self):
        return len(self.changes) > 0

    def create_message(self):
        logging.debug(f"Creating message for product \'{self.product.name}\'...")
        logging.debug(f"  new -> {self.product}")
        logging.debug(f"  old -> {self.old_product}")

        result = discord.Embed(title=self.product.name, url=self.product.links[0].url, description=self.product.readable_links)
        result.color = POSITIVE_COLOR if self.positive else NEGATIVE_COLOR
        result.set_thumbnail(url=self.product.image_url)
        result.add_field(name=self.product.readable_stock, value=f"Previous: {self.old_product.readable_stock}", inline=False)
        result.add_field(name=self.product.readable_price, value=f"Previous: {self.old_product.readable_price}", inline=False)
        result.set_footer(text="Changed: {}".format(", ".join(self.changes)))
        return result
