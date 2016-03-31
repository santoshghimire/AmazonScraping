import scrapy
from amazonscraping.items import AmazonProduct
from scrapy.selector import Selector
# from scrapy.http import Request
# import json
# import requests


class AmazonDataCollector(scrapy.Spider):
    """
    This is the spider that crawls the given start_urls.
    """
    name = "adc"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/Performix-Suspension-Super' +
        '-Thermogenic-Licaps/dp/B00JHIOZQ6/'
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        item = AmazonProduct()
        name = response.xpath(
            "//span[@id='productTitle']/text()"
        ).extract()[0].encode('utf-8')
        price = response.xpath(
            "//span[@id='priceblock_ourprice']/text()"
        ).extract()[0].encode('utf-8')
        rank_details = response.xpath(
            "//li[@id='SalesRank']"
        ).extract()[0]
        print(rank_details, type(rank_details))
        print(name, price)
        item['name'] = name
        item['price'] = price.replace('$', '')
        item['rank'] = '1841'
        item['category'] = 'Health & Personal Care'

        body = """
        <li id="itemId">
            <b>Something in bold</b>
            #Required data (
            <a href="some_link">some link</a>
            )
            <ul>
                <li>other data</li>
                <li>other data</li>
                <li>other data</li>
            </ul>
        </li>
        """
        data = Selector(text=body).xpath('//b/text()').extract()
        print(data)
        return item
