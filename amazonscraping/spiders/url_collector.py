import scrapy
from scrapy.http import Request

from amazonscraping.items import BestSellerItemLink
from amazonscraping.get_category_url import GetBestSellerCategoryURL
from amazonscraping.pipelines import BestSellerPipeline


class URLCollector(scrapy.Spider):
    """
    This is the spider that crawls the given start_urls.
    """
    name = "url_collector"
    allowed_domains = ["amazon.com"]

    url = GetBestSellerCategoryURL()

    start_urls = []

    pipeline = set([
        BestSellerPipeline
    ])

    def start_requests(self):
        """
        NOTE: This method is ONLY CALLED ONCE by Scrapy (to kick things off).
        Get the first url to crawl and return a Request object
        This will be parsed to self.parse which will continue
        the process of parsing all the other generated URLs
        """
        # connect to mysql database
        self.url.connect()

        # grab the first URL to begin crawling
        start_url = self.url.next_url().next()

        request = Request(start_url, dont_filter=True)

        # important to yield, not return
        yield request

    def parse(self, response):
        """
        Parse the current response object, and return any Item and/or Request
        objects
        """
        links = response.xpath(
            "//div[@class='zg_itemImmersion']/"
            "div[@class='zg_itemWrapper']/div[@class='zg_image']/"
            "div/a/@href"
        ).extract()
        for link in links:
            item = BestSellerItemLink()
            item['product_url'] = link.strip()
            item['category_url'] = response.url
            yield item

        for page in range(2, 6):
            for j in ["1", "0"]:
                # get paginated links
                pagination_url = response.url + \
                    '/?_encoding=UTF8&pg=' + str(page) +\
                    '&ajax=1&isAboveTheFold=' + j
                request = Request(
                    pagination_url, callback=self.parse_paginated_items
                )
                request.meta['category_url'] = response.url
                yield request

        # get the next URL to crawl
        next_url = self.url.next_url().next()
        yield Request(next_url)

    def parse_paginated_items(self, response):
        links = response.xpath("//div[@class='zg_title']/a/@href").extract()
        for link in links:
            item = BestSellerItemLink()
            item['product_url'] = link.strip()
            item['category_url'] = response.meta['category_url']
            yield item
