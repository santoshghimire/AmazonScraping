# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonProduct(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    price = scrapy.Field()
    rank = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    shipping_weight = scrapy.Field()
    item_model_number = scrapy.Field()
    badge_count = scrapy.Field()
    amazon_seller = scrapy.Field()
