import scrapy
import urlparse

from amazonscraping.items import AmazonProduct
# from scrapy.selector import Selector
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

    def __init__(self, *args, **kwargs):
        super(AmazonDataCollector, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]

    def parse(self, response):
        item = AmazonProduct()
        try:
            name = response.xpath(
                "//span[@id='productTitle']/text()"
            ).extract()[0].encode('utf-8')
        except:
            print('Error in processing name')
            name = ''
        try:
            # price by amazon
            price = response.xpath(
                "//span[@id='priceblock_ourprice']/text()"
            ).extract()[0].encode('utf-8')
        except:
            try:
                # sale price
                price = response.xpath(
                    "//span[@id='priceblock_saleprice']/text()"
                ).extract()[0].encode('utf-8')
            except:
                print('Error in processing price')
                price = ''
        try:
            rank_details = response.xpath(
                "//li[@id='SalesRank']/text()"
            )[1].extract().strip()

            rank = rank_details.split(' ')[0].replace('#', '').replace(',', '')
            category = rank_details.split('in')[-1].replace('(', '').strip()
        except:
            print('Error in processing rank and category')
            rank = ''
            category = ''

        # getting request url without querystring
        url = response.request.url
        parsed_url = urlparse.urljoin(url, urlparse.urlparse(url).path)

        # getting shipping weight
        shipping_wt_details = response.xpath(
            "//li[@id='SalesRank']/../li/b[contains(text(),"
            " 'Shipping Weight')]"
        )
        shipping_wt = shipping_wt_details.xpath('../text()')[0].extract()
        shipping_wt = shipping_wt.replace('(', '').strip()
        # print('Parsed URL:', parsed_url)
        # print('shipping_wt:', shipping_wt)

        item['name'] = name
        item['price'] = price.replace('$', '')
        item['rank'] = rank
        item['category'] = category
        return item
