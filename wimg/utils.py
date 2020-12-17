import re

from wimg.price import Price

from typing import Optional


PRICE_RE = re.compile(r"[^0-9.]+")


def parse_price(price_str: str) -> Optional[Price]:
    if price_str.endswith("-"):
        currency = "CZK"
    elif "€" in price_str:
        currency = "EUR"

    price = PRICE_RE.sub("", price_str.replace(",", "."))
    result = Price()
    if price:
        result.add_value(float(price), currency)
    return result


def remove_prefix(prefix: str, s: str):
    return s[len(prefix):] if s.startswith(prefix) else s
