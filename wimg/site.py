import aiohttp
import lxml.etree
import io


class Site:
    def __init__(self, base_url: str, resource: str, channel_id: int):
        self.base_url = base_url if base_url.endswith("/") else f"{base_url}/"
        self.resource = resource[1:] if resource.startswith("/") else resource
        self.channel_id = channel_id
        self.tree = None

    @property
    def url(self):
        return f"{self.base_url}{self.resource}"

    def url_for_page(self, page: int):
        raise NotImplementedError

    def has_next_page(self):
        raise NotImplementedError

    def parse_products(self):
        raise NotImplementedError

    async def get(self):
        result = []
        html_parser = lxml.etree.HTMLParser()

        page = 1
        has_next_page = True
        async with aiohttp.ClientSession() as session:
            while has_next_page:
                async with session.get(self.url_for_page(page), headers={"User-Agent": "Googlebot"}) as response:
                    response_text = await response.text()
                    self.tree = lxml.etree.parse(io.StringIO(response_text), lxml.etree.HTMLParser())

                result.extend(self.parse_products())
                has_next_page = self.has_next_page()
                page = page + 1

        return result
