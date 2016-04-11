import scrapy
import urlparse
from scrapy.http import Request
# from scrapy.xlib.pydispatch import dispatcher


from amazonscraping.items import AmazonProduct
from amazonscraping.get_product_url import GetProductURL
from amazonscraping.pipelines import AmazonscrapingPipeline


class AmazonDataCollector(scrapy.Spider):
    """
    This is the spider that crawls the given start_urls.
    """
    name = "adc"
    allowed_domains = ["amazon.com"]
    handle_httpstatus_list = [400, 404, 503]

    url = GetProductURL()

    start_urls = []

    args = False

    # start_urls = [
    #     'http://www.amazon.com/Performix-Suspension-Super' +
    #     '-Thermogenic-Licaps/dp/B00JHIOZQ6/'
    # ]

    pipeline = set([
        AmazonscrapingPipeline
    ])

    def __init__(self, *args, **kwargs):
        super(AmazonDataCollector, self).__init__(*args, **kwargs)
        if kwargs.get('url'):
            self.start_urls = [kwargs.get('url')]
            self.args = True

    def start_requests(self):
        """
        NOTE: This method is ONLY CALLED ONCE by Scrapy (to kick things off).
        Get the first url to crawl and return a Request object
        This will be parsed to self.parse which will continue
        the process of parsing all the other generated URLs
        """
        if not self.args:
            # connect to mysql database
            self.url.connect()

            # grab the first URL to begin crawling
            start_url = self.url.next_url().next()
        else:
            start_url = self.start_urls[0]

        request = Request(start_url, dont_filter=True)

        # important to yield, not return
        yield request

    def parse(self, response):
        # yield Request(url=response.url, dont_filter=True)
        if not response.xpath("//span[@class='nav-logo-base nav-sprite']"):
            print('Not amazon')
            yield Request(url=response.url, dont_filter=True)
        item = AmazonProduct()
        try:
            name = response.xpath(
                "//span[@id='productTitle']/text()"
            ).extract()[0].encode('utf-8')
        except:
            print('Error in processing name', response.url)
            name = ''
        try:
            # price by amazon
            price = response.xpath(
                "//span[@id='priceblock_ourprice']/text()"
            ).extract()[0].encode('utf-8')
            price = float(price.replace('$', ''))
        except:
            try:
                # sale price
                price = response.xpath(
                    "//span[@id='priceblock_saleprice']/text()"
                ).extract()[0].encode('utf-8')
                price = price.replace('$', '')
            except:
                print('Error in processing price', response.url)
                price = ''
        try:
            rank_details = response.xpath(
                "//li[@id='SalesRank']/text()"
            )[1].extract().strip()

            rank = rank_details.split(' ')[0].replace('#', '').replace(',', '')
            rank = int(rank)
            category = rank_details.split('in')[-1].replace('(', '').strip()
        except:
            # For tabular format
            try:
                best_seller_rank = response.xpath(
                    "//table[@id='productDetails_detailBullets_sections1']"
                    "//th[contains(text(), 'Best Sellers Rank')]"
                )
                rank_details = best_seller_rank.xpath(
                    "following-sibling::td/span/span/text()"
                )[0].extract()
                rank = rank_details.split(' ')[0].replace('#', '').replace(
                    ',', ''
                )
                rank = int(rank)
                category = rank_details.split('in')[-1].replace(
                    '(', ''
                ).strip()
            except:
                print('Error in processing rank and category', response.url)
                rank = -1
                category = ''

        # getting request url without querystring
        url = response.request.url
        parsed_url = urlparse.urljoin(url, urlparse.urlparse(url).path)

        # getting shipping weight
        try:
            shipping_wt_details = response.xpath(
                "//li[@id='SalesRank']/../li/b[contains(text(),"
                " 'Shipping Weight')]"
            )
            shipping_wt = shipping_wt_details.xpath('../text()')[0].extract()
            shipping_wt = shipping_wt.replace('(', '').strip()
        except:
            # For tabular format
            try:
                shipping_wt_details = response.xpath(
                    "//table[@id='productDetails_detailBullets_sections1']"
                    "//th[contains(text(), 'Shipping Weight')]"
                )
                shipping_wt_details = shipping_wt_details.xpath(
                    "following-sibling::td/text()"
                )[0].extract()
                shipping_wt = shipping_wt_details.replace('(', '').strip()
            except:
                shipping_wt = ''

        try:
            item_model_details = response.xpath(
                "//table[@id='productDetails_techSpec_section_1']"
                "//th[contains(text(), 'Item model number')]"
            )
            item_model_details = item_model_details.xpath(
                "following-sibling::td/text()"
            )[0].extract()
            item_model_number = item_model_details.strip()
        except:
            try:
                item_model_details = response.xpath(
                    "//li[@id='SalesRank']/../li/b[contains(text(),"
                    " 'Item model number')]"
                )
                item_model_number = item_model_details.xpath(
                    '../text()'
                )[0].extract()
                item_model_number = item_model_number.strip()
            except:
                item_model_number = ''

        item['name'] = name
        item['price'] = price
        item['rank'] = rank
        item['category'] = category
        item['url'] = parsed_url
        item['shipping_weight'] = shipping_wt
        item['item_model_number'] = item_model_number

        try:
            product_id = ''
            other_sellers_link = "http://www.amazon.com/gp/offer-listing/"
            split_url = url.split('/')
            product_id = split_url[split_url.index('dp') + 1]

            item['asin'] = product_id

            other_sellers_link += product_id
            request = Request(
                other_sellers_link, callback=self.parse_other_sellers_page,
                headers={
                    'Host': 'www.amazon.com',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0)'
                            'Gecko/20100101 Firefox/45.0',
                    'Accept': 'text/html,application/xhtml+xml,application/'
                            'xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache'
                }
            )
            request.meta['item'] = item
            yield request
        except:
            item['badge_count'] = 0
            item['amazon_seller'] = 'N/A'
            if not product_id:
                item['asin'] = product_id
            yield item

        # get the next URL to crawl
        if not self.args:
            next_url = self.url.next_url().next()
            yield Request(next_url)

    def parse_other_sellers_page(self, response):
        if response.status in self.handle_httpstatus_list:
            self.crawler.stats.inc_value('failed_url_count')
        try:
            badge_elements = response.xpath(
                "//div[@class='olpBadgeContainer']/div/span/"
                "a[contains(text(), 'Fulfillment by Amazon')]/text()"
            ).extract()
            badge_count = len(badge_elements)
        except:
            print(
                'Error in processing seller Fullfillment by'
                ' Amazon badge count',
                response.url
            )
            badge_count = 0
        try:
            amazon_seller_element = response.xpath(
                "//div[@class='a-column a-span2 olpSellerColumn']"
                "/h3/img[@alt='Amazon.com']"
            )
            if amazon_seller_element:
                amazon_seller = 'Yes'
            else:
                amazon_seller = 'No'
        except:
            print('Error in processing amazon seller', response.url)
            amazon_seller = 'N/A'

        item = response.meta['item']
        item['badge_count'] = badge_count
        item['amazon_seller'] = amazon_seller
        yield item

    def process_exception(self, response, exception, spider):
        ex_class = "%s.%s" % (
            exception.__class__.__module__, exception.__class__.__name__
        )
        self.crawler.stats.inc_value(
            'downloader/exception_count', spider=spider
        )
        self.crawler.stats.inc_value(
            'downloader/exception_type_count/%s' % ex_class, spider=spider
        )
