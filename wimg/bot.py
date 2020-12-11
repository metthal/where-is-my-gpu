import aioredis
import asyncio
import discord
import io
import logging
import re
import textwrap

from datetime import datetime
from tabulate import tabulate

from wimg.product import Product
from wimg.report import Report
from wimg.scraper import Scraper
from wimg.sites import Alza


MENTION_RE = re.compile(r"<@![0-9]+>")


class Bot(discord.Client):
    def __init__(self, config: dict, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.config = config
        self.scraper = Scraper()
        for scraper_conf in self.config["scraper"]["targets"]:
            if scraper_conf["type"] == "alza":
                self.scraper.add(Alza(scraper_conf["url"]))
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
            reports = await self.scraper.scrape(self.redis)

            send_tasks = []
            for report in reports:
                msg = report.create_message()
                if msg is not None:
                    logging.info(f"Product '{report.product.name}' has changed. Reporting...")
                    send_tasks.append(bot.send(self.config["discord"]["channel_id"], embed=msg))

            if send_tasks:
                await asyncio.gather(*send_tasks)

            await asyncio.sleep(self.config["scraper"]["interval"])

    async def stop(self):
        await self.logout()
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def on_message(self, message):
        if not any(map(lambda user: user.id == self.user.id, message.mentions)):
            return

        cmd = MENTION_RE.sub("", message.content).strip().lower()
        if cmd == "help":
            logging.info(f"Command: HELP ({message.author.name})")
            await self.send(
                textwrap.dedent("""
                Yo. Just tag me and type a command which you'd like to execute. I have these commands available:

                `help` - You are reading this.
                `ping` - Test whether I am responsive.
                `test` - Test sending of embedded links.
                `targets` - List of URLs I am watching.
                `list` - List of products I have in the database.
                """)
            )
        elif cmd == "ping":
            logging.info(f"Command: PING ({message.author.name})")
            await message.add_reaction("✅")
        elif cmd == "test":
            logging.info(f"Command: TEST ({message.author.name})")
            p1 = Product(
                6160836,
                "EVGA GeForce RTX 3090 FTW3 ULTRA",
                "https://www.alza.cz/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm",
                None,
                None,
                "https://cdn.alza.cz/Foto/f11/EV/EVr3090h4.jpg",
                [("🇸🇰 Alza", "https://www.alza.sk/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm")]
            )
            p2 = Product(
                6160836,
                "EVGA GeForce RTX 3090 FTW3 ULTRA",
                "https://www.alza.cz/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm",
                45000,
                "> 5",
                "https://cdn.alza.cz/Foto/f11/EV/EVr3090h4.jpg",
                [("🇸🇰 Alza", "https://www.alza.sk/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm")]
            )
            r1 = Report(p2)
            r1.old_product = p1
            r2 = Report(p1)
            r2.old_product = p2
            await self.send(message.channel.id, embed=r1.create_message())
            await self.send(message.channel.id, embed=r2.create_message())
        elif cmd == "targets":
            logging.info(f"Command: TARGETS ({message.author.name})")
            await self.send(message.channel.id, "\n".join([site.url for site in self.scraper.sites]))
        elif cmd == "list":
            logging.info(f"Command: LIST ({message.author.name})")
            all_keys = []
            cursor = b"0"
            while cursor:
                cursor, keys = await self.redis.scan(cursor, match="*")
                all_keys.extend(keys)
            products_table = sorted([product.to_tuple() for product in sorted(await Product.load_multiple(self.redis, all_keys), key=lambda p: p.name)])
            await self.send(
                message.channel.id,
                file=discord.File(
                    io.StringIO(tabulate(products_table, headers=Product.tuple_headers())),
                    filename="products-{:%Y-%m-%d-%H-%M-%S}.txt".format(datetime.now())
                )
            )
        else:
            logging.error(f"Command: Got unknown command '{cmd}' from '{message.author.name}'")
            await message.add_reaction("❓")

    async def send(self, channel_id, *args, **kwargs):
        return await self.get_channel(channel_id).send(*args, **kwargs)
