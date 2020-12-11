#!/usr/bin/env python3

import aioredis
import asyncio
import discord
import logging
import os
import sys

from pyhocon import ConfigFactory

from wimg.product import Product
from wimg.report import Report
from wimg.scraper import Scraper
from wimg.sites import Alza


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)-8s] -- %(message)s",
    stream=sys.stdout
)


config = ConfigFactory.parse_file("config.conf")


async def main():
    discord_client = discord.Client(loop=asyncio.get_event_loop())
    scraper = Scraper()
    for scraper_conf in config["scraper"]["targets"]:
        if scraper_conf["type"] == "alza":
            scraper.add(Alza(scraper_conf["url"]))

    #@discord_client.event
    #async def on_ready():
    #    p1 = Product(6160836, "EVGA GeForce RTX 3090 FTW3 ULTRA", "https://www.alza.cz/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm", None, None, "https://cdn.alza.cz/Foto/f11/EV/EVr3090h4.jpg")
    #    p2 = Product(6160836, "EVGA GeForce RTX 3090 FTW3 ULTRA", "https://www.alza.cz/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm", 15000, "> 5", "https://cdn.alza.cz/Foto/f11/EV/EVr3090h4.jpg", [("🇸🇰 Alza", "https://www.alza.sk/gaming/evga-geforce-rtx-3090-ftw3-ultra-d6160836.htm")])
    #    r = Report(p2)
    #    r.old_product = p1
    #    await discord_client.get_channel(config["discord"]["channel_id"]).send(embed=r.create_message())

    try:
        redis = await aioredis.create_redis_pool("redis://{}:{}".format(config["redis"]["hostname"], config["redis"]["port"]), db=config["redis"]["db"])
        discord_task = asyncio.create_task(discord_client.start(config["discord"]["token"]))
        while True:
            reports = await scraper.scrape(redis)

            send_tasks = []
            for report in reports:
                msg = report.create_message()
                if msg is not None:
                    logging.info(f"Product '{report.product.name}' has changed. Reporting...")
                    send_tasks.append(discord_client.get_channel(config["discord"]["channel_id"]).send(embed=msg))

            if send_tasks:
                await asyncio.gather(*send_tasks)

            await asyncio.sleep(config["scraper"]["interval"])
    except Exception as err:
        logging.error(str(err), exc_info=True)
    finally:
        await discord_client.logout()
        redis.close()
        await redis.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
