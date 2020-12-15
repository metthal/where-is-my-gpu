import aioredis
import asyncio
import discord
import io
import logging
import re
import textwrap

from datetime import datetime
from tabulate import tabulate
from typing import List

from wimg.product import Product
from wimg.report import Report
from wimg.scraper import Scraper
from wimg.sites import Alza
from wimg.user import User


MENTION_RE = re.compile(r"<@(!)?[0-9]+>")


class Bot(discord.Client):
    def __init__(self, config: dict, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.config = config
        self.scraper = Scraper()
        for scraper_conf in self.config["scraper"]["targets"]:
            if scraper_conf["type"] == "alza":
                self.scraper.add(Alza(scraper_conf["url"], scraper_conf["channel_id"]))
        self.redis = None

    async def start(self):
        self.redis = await aioredis.create_redis_pool(
            "redis://{}:{}".format(
                self.config["redis"]["hostname"],
                self.config["redis"]["port"]
            ),
            db=self.config["redis"]["db"]
        )
        asyncio.create_task(super(Bot, self).start(self.config["discord"]["token"]))

        while True:
            users = await User.load_all(self.redis)
            reports = await self.scraper.scrape(self.redis)

            send_tasks = []
            for report in filter(lambda r: r.any_changes, reports):
                send_tasks.append(self.send_report(report, users))

            if send_tasks:
                await asyncio.gather(*send_tasks)

            await asyncio.sleep(self.config["scraper"]["interval"])

    async def send_report(self, report: Report, users: List[User]):
        logging.info(f"Product '{report.product.name}' has changed. Reporting...")

        mentions = []
        for user in users:
            if user.is_subscribed_for(report.product):
                mentions.append(user.id)
                continue

        content = None
        if mentions:
            content = " ".join([f"<@{user_id}>" for user_id in mentions])

        return await self.send(report.channel_id, content=content, embed=report.create_message())

    async def stop(self):
        await self.logout()
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def on_message(self, message):
        if not any(map(lambda user: user.id == self.user.id, message.mentions)):
            return

        try:
            cmd_parts = MENTION_RE.sub("", message.content).strip().split(" ", 1)
            cmd = cmd_parts[0].lower()
            if cmd == "help":
                logging.info(f"Command: HELP ({message.author.name})")
                await self.send(
                    message.channel.id,
                    textwrap.dedent("""
                    Yo. Just tag me and type a command which you'd like to execute. I have these commands available:

                    `help` - You are reading this.
                    `ping` - Test whether I am responsive.
                    `targets` - List of URLs I am watching.
                    `list` - List of products I have in the database.
                    `trigger <PRODUCT_NAME>` - Test notification for product by its name.
                    `subscriptions` - List of products you are subscribed for. When there's something new about this product, you are explicitly tagged.
                    `subscribe <PRODUCT_NAME>` - Subscribe for a product by its name.
                    `unsubscribe <PRODUCT_NAME>` - Unsubscribe from a product by its name. If you put `all` in place of product name then all your subscriptions are removed.
                    """)
                )
            elif cmd == "ping":
                logging.info(f"Command: PING ({message.author.name})")
                await message.add_reaction("✅")
            elif cmd == "targets":
                logging.info(f"Command: TARGETS ({message.author.name})")
                longest_url = max([len(site.url) for site in self.scraper.sites])
                await self.send(message.channel.id,
                    "```" +
                    "\n".join([
                        "{}{} -> #{}".format(
                            site.url,
                            " " * (longest_url - len(site.url)),
                            self.get_channel(site.channel_id).name
                        ) for site in self.scraper.sites
                    ]) +
                    "```"
                )
            elif cmd == "list":
                logging.info(f"Command: LIST ({message.author.name})")
                products_table = sorted([product.to_tuple() for product in sorted(await Product.load_all(self.redis), key=lambda p: p.name)])
                await self.send(
                    message.channel.id,
                    file=discord.File(
                        io.StringIO(tabulate(products_table, headers=Product.tuple_headers())),
                        filename="products-{:%Y-%m-%d-%H-%M-%S}.txt".format(datetime.now())
                    )
                )
            elif cmd == "trigger":
                product_name = cmd_parts[1]
                logging.info(f"Command: TRIGGER ({message.author.name}) ({product_name})")
                product = await Product.find(self.redis, product_name)
                if product is None:
                    await message.add_reaction("❌")
                else:
                    users = await User.load_all(self.redis)
                    report = Report(message.channel.id, product, product, force_change=True)
                    await self.send_report(report, users)
                    await message.add_reaction("✅")
            elif cmd == "subscriptions":
                logging.info(f"Command: SUBSCRIPTIONS ({message.author.name})")
                user = await User.load(self.redis, message.author.id)
                if user is None:
                    await message.add_reaction("\u0030\ufe0f\u20e3") # emoji :zero:
                    return

                products = await Product.load_multiple(self.redis, user.subscribed)
                if len(products) == 0:
                    await message.add_reaction("\u0030\ufe0f\u20e3") # emoji :zero:
                else:
                    await self.send(message.channel.id, f"<@{user.id}>, here are you subscriptions:\n```" + "\n".join([p.name for p in products]) + "```")
            elif cmd == "subscribe":
                product_name = cmd_parts[1]
                logging.info(f"Command: SUBSCRIBE ({message.author.name}) ({product_name})")
                product = await Product.find(self.redis, product_name)
                if product is None:
                    await message.add_reaction("❌")
                    return

                user = await User.load(self.redis, message.author.id)
                if user is None:
                    user = User(message.author.id)

                user.subscribed.add(product.id)
                await user.save(self.redis)
                await message.add_reaction("✅")
            elif cmd == "unsubscribe":
                product_name = cmd_parts[1]
                logging.info(f"Command: UNSUBSCRIBE ({message.author.name}) ({product_name})")
                user = await User.load(self.redis, message.author.id)
                if user is None:
                    return

                if product_name == "all":
                    product_ids = list(user.subscribed)
                else:
                    product = await Product.find(self.redis, product_name)
                    if product is None:
                        await message.add_reaction("❌")
                        return
                    product_ids = [product.id]

                for product_id in product_ids:
                    if product_id in user.subscribed:
                        user.subscribed.remove(product_id)
                await user.save(self.redis)
                await message.add_reaction("✅")
            else:
                logging.error(f"Command: Got unknown command '{cmd}' from '{message.author.name}'")
                await message.add_reaction("❓")
        except Exception as err:
            logging.error(repr(err), exc_info=True)
            await message.add_reaction("💀")

    async def send(self, channel_id, *args, **kwargs):
        return await self.get_channel(channel_id).send(*args, **kwargs)
