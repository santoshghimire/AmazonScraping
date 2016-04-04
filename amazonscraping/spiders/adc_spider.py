import scrapy
import urlparse

from amazonscraping.items import AmazonProduct
from scrapy.http import Request


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
            price = float(price.replace('$', ''))
        except:
            try:
                # sale price
                price = response.xpath(
                    "//span[@id='priceblock_saleprice']/text()"
                ).extract()[0].encode('utf-8')
                price = float(price.replace('$', ''))
            except:
                print('Error in processing price')
                price = -1.0
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
                print('Error in processing rank and category')
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
            item_model_number = ''
            pass

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
                other_sellers_link, callback=self.parse_other_sellers_page
            )
            request.meta['item'] = item
            return request
        except:
            item['badge_count'] = 0
            item['amazon_seller'] = 'No'
            if not product_id:
                item['asin'] = product_id
            return item

    def parse_other_sellers_page(self, response):
        try:
            badge_elements = response.xpath(
                "//div[@class='olpBadgeContainer']/div/span/"
                "a[contains(text(), 'Fulfillment by Amazon')]/text()"
            ).extract()
            badge_count = len(badge_elements)
        except:
            print(
                'Error in processing seller Fullfillment by Amazon badge count'
            )
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
            print('Error in processing amazon seller')

        item = response.meta['item']
        item['badge_count'] = badge_count
        item['amazon_seller'] = amazon_seller
        return item
