import aiohttp
import asyncio
import functools
import lxml.etree
import io

from typing import List


class Site:
    def __init__(self, base_url: str, resource: str, channel_id: int):
        self.base_url = base_url if base_url and base_url.endswith("/") else f"{base_url}/"
        self.resource = resource[1:] if resource.startswith("/") else resource
        self.channel_id = channel_id
        self.tree = None

    @property
    def urls(self):
        return [f"{self.base_url}{self.resource}"]

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


class MultiSite(Site):
    def __init__(self, resource: str, channel_id: int, sites: List[Site]):
        super(MultiSite, self).__init__(None, resource, channel_id)
        self.sites = sites

    @property
    def urls(self):
        return functools.reduce(lambda urls, site: urls + site.urls, self.sites, [])

    async def get(self):
        results = await asyncio.gather(*[
            site.get() for site in self.sites
        ])

        products = {p.name: p for p in results[0]}
        for add_products in results[1:]:
            for p in add_products:
                if p.name in products:
                    products[p.name].merge(p)
                else:
                    products[p.name] = p

        return results[0]
