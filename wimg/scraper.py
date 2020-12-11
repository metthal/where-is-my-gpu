import asyncio
import logging

from wimg.product import Product
from wimg.report import Report
from wimg.site import Site


class Scraper:
    def __init__(self):
        self.sites = []

    def add(self, site: Site):
        self.sites.append(site)

    async def scrape(self, redis):
        logging.info("Starting scraping...")

        results = await asyncio.gather(*[
            site.get() for site in self.sites
        ])

        reports = []
        for result in results:
            for product in result:
                logging.info(f"  Detected product: {product}")
                report = Report(product)
                report.old_product = await Product.load(redis, product.id)
                await product.save(redis)

        return reports
