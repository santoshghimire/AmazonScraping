# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonProduct(scrapy.Item):
    """Amazon product item"""
    name = scrapy.Field()
    price = scrapy.Field()
    rank = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    shipping_weight = scrapy.Field()
    item_model_number = scrapy.Field()
    badge_count = scrapy.Field()
    amazon_seller = scrapy.Field()
    asin = scrapy.Field()


class BestSellerCategoryLink(scrapy.Item):
    """Best Seller Category link item"""
    name = scrapy.Field()
    url = scrapy.Field()
    parent_category = scrapy.Field()
    main_category = scrapy.Field()


class BestSellerItemLink(scrapy.Item):
    """Best Seller Item on Amazon"""
    product_url = scrapy.Field()
    category_url = scrapy.Field()
