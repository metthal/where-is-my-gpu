import re

from wimg.product import Product
from wimg.site import Site
from wimg.utils import parse_price


IN_STOCK_RE = re.compile(r"skladem\s+((>\s+)?[0-9]+).*")


class Alza(Site):
    def __init__(self, resource: str, channel_id: int):
        super(Alza, self).__init__("https://alza.cz/", resource, channel_id)
        self.sk_base_url = "https://alza.sk/"

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
            if "rozbaleno" in stock_text:
                continue
            matches = IN_STOCK_RE.fullmatch(stock_text)
            stock = matches.group(1) if matches else None
            image_url = product.xpath("div[contains(@class, 'top')]/div[contains(@class, 'bi')]/a/em/img")[0].attrib.get("data-src", None)
            result.append(Product(id, name, link, price, stock, image_url, [("🇸🇰 Alza", f"{self.sk_base_url}{name_link.attrib['href'][1:]}")]))
        return result
