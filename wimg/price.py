from dataclasses import dataclass


@dataclass
class PriceInCurrency:
    value: float
    currency: str

    def __str__(self):
        with_decimals = "{:.2f}".format(self.value)
        return "{} {}".format(with_decimals.rstrip("0").rstrip(".") if with_decimals.endswith(".00") else with_decimals, self.currency)


class Price:
    def __init__(self, value: float = None, currency: str = None):
        self.values = []
        if value is not None and currency is not None:
            self.values.append(PriceInCurrency(value, currency))

    def add_value(self, value: float, currency: str):
        self.values.append(PriceInCurrency(value, currency))

    def merge(self, rhs: "Price"):
        self.values.extend(rhs.values)

    def __bool__(self):
        return len(self.values) > 0

    def __str__(self):
        return "No Price" if not self.values else " / ".join([str(value) for value in self.values])

    def __eq__(self, rhs: "Price") -> bool:
        return len(self.values) == len(rhs.values) and all(map(lambda x: x[0].value == x[1].value, zip(self.values, rhs.values)))

    def __lt__(self, rhs: "Price") -> bool:
        return len(self.values) == len(rhs.values) and all(map(lambda x: x[0].value < x[1].value, zip(self.values, rhs.values)))
