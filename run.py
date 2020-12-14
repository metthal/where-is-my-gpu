#!/usr/bin/env python3

import asyncio
import logging
import sys

from pyhocon import ConfigFactory
from typing import Optional

from wimg.bot import Bot


def log_level_from_string(log_level_str: Optional[str]):
    if log_level_str == "debug":
        return logging.DEBUG
    elif log_level_str == "info":
        return logging.INFO
    elif log_level_str == "warning":
        return logging.WARNING
    elif log_level_str == "error":
        return logging.ERROR
    else:
        return logging.INFO


def setup_logging(config: dict):
    logging.basicConfig(
        level=log_level_from_string(config.get("log_level", None)),
        format="[%(asctime)s] [%(levelname)-8s] -- %(message)s",
        stream=sys.stdout
    )

    if config.get("log_level", None) == "debug":
        for name in ["discord"]:
            logging.getLogger(name).setLevel(logging.INFO)


config = ConfigFactory.parse_file("config.conf")
setup_logging(config)


async def main():
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
