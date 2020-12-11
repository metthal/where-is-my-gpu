#!/usr/bin/env python3

import asyncio
import logging
import sys

from pyhocon import ConfigFactory

from wimg.bot import Bot


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)-8s] -- %(message)s",
    stream=sys.stdout
)


async def main():
    config = ConfigFactory.parse_file("config.conf")
    bot = Bot(config, loop=asyncio.get_event_loop())

    try:
        await bot.start()
    except Exception as err:
        logging.error(str(err), exc_info=True)
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
