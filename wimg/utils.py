import re

from typing import Optional


PRICE_RE = re.compile(r"[^0-9]+")


def parse_price(price_str: str) -> Optional[int]:
    result = PRICE_RE.sub("", price_str)
    return int(result) if result else None


def remove_prefix(prefix: str, s: str):
    return s[len(prefix):] if s.startswith(prefix) else s
