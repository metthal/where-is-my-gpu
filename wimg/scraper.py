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
                report = Report(product, await Product.load(redis, product.id))
                logging.debug(f"Saving \'{product.name}\' to the database...")
                await product.save(redis)
                reports.append(report)

        return reports
