import math

from dataclasses import dataclass


@dataclass
class PriceInCurrency:
    value: float
    currency: str

    def __str__(self):
        with_decimals = "{:.2f}".format(self.value)
        return "{} {}".format(with_decimals.rstrip("0").rstrip(".") if with_decimals.endswith(".00") else with_decimals, self.currency)

    def __eq__(self, rhs):
        return self.currency == rhs.currency and math.isclose(self.value, rhs.value, abs_tol=0.0001)

    def __lt__(self, rhs):
        return self.currency == rhs.currency and self.value < rhs.value


class Price:
    def __init__(self, value: float = None, currency: str = None):
        self.values = {}
        if value is not None and currency is not None:
            self.values[currency] = PriceInCurrency(value, currency)

    def add_value(self, value: float, currency: str):
        self.values[currency] = PriceInCurrency(value, currency)

    def merge(self, rhs: "Price"):
        self.values.update(rhs.values)

    def __bool__(self):
        return len(self.values) > 0

    def __str__(self):
        return "No Price" if not self.values else " / ".join([str(value) for _, value in self.values.items()])

    def __eq__(self, rhs: "Price") -> bool:
        if len(self.values) == 0 and len(rhs.values) == 0:
            return True

        for currency, price in self.values.items():
            if currency in rhs.values and price == rhs.values[currency]:
                return True

        return False

    def __lt__(self, rhs: "Price") -> bool:
        for currency, price in self.values.items():
            if currency in rhs.values and price < rhs.values[currency]:
                return True
        return False
