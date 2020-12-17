import re

from wimg.link import Link
from wimg.product import Product
from wimg.site import MultiSite, Site
from wimg.utils import parse_price


IN_STOCK_RE = re.compile(r"skladem\s+((>\s+)?[0-9]+).*")


class AlzaForCountry(Site):
    COUNTRY_TO_EMOJI = {
        "cz": "🇨🇿",
        "sk": "🇸🇰"
    }

    def __init__(self, country: int, resource: str, channel_id: int):
        super(AlzaForCountry, self).__init__(f"https://alza.{country}/", resource, channel_id)
        self.country = country

    def url_for_page(self, page: int) -> str:
        return "{}{}{}-p{}.htm".format(self.base_url, self.resource, self.resource[:-4], page)

    def has_next_page(self) -> bool:
        return len(self.tree.xpath("//div[@id='pagerbottom']/a[@id='pgby2']")) != 0

    def parse_products(self):
        result = []
        products = self.tree.xpath("//div[@id='boxes']/div[contains(@class, 'box')]")
        for product in products:
            id = int(product.attrib["data-id"])
            name_link = product.xpath("div[contains(@class, 'top')]/div[contains(@class, 'fb')]/a[contains(@class, 'name')]")[0]
            name = name_link.text
            link = f"{self.base_url}{name_link.attrib['href'][1:]}"
            price = parse_price(product.xpath("div[contains(@class, 'bottom')]//div[contains(@class, 'priceInner')]/span")[0].text)
            stock_text = product.xpath("div[contains(@class, 'bottom')]/div[contains(@class, 'avl')]/span")[0].text.lower()
            if "rozbalen" in stock_text:
                continue
            matches = IN_STOCK_RE.fullmatch(stock_text)
            stock = matches.group(1) if matches else None
            image_url = product.xpath("div[contains(@class, 'top')]/div[contains(@class, 'bi')]/a/em/img")[0].attrib.get("data-src", None)

            link = Link(f"{self.COUNTRY_TO_EMOJI[self.country]} Alza", link)
            result.append(Product(id, name, link, price, stock, image_url))
        return result


class Alza(MultiSite):
    def __init__(self, resource: str, channel_id: int):
        super(Alza, self).__init__(resource, channel_id, [
            AlzaForCountry("cz", resource, channel_id),
            AlzaForCountry("sk", resource, channel_id)
        ])
