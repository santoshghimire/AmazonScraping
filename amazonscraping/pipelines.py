# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from scrapy import signals


class AmazonscrapingPipeline(object):

    cnx = {
        'host': "localhost",
        'username': "root",
        'password': "root",
        'db': "amazonscraping"
    }
    db = None
    cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        """ Connect to RDS MySQL database when spider is opened """
        print('** Spider opened, connecting to MySQLdb **')
        self.db = MySQLdb.connect(
            self.cnx['host'], self.cnx['username'],
            self.cnx['password'], self.cnx['db']
        )

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()

        self.cursor.execute("SET sql_notes = 0; ")
        self.cursor.execute(
            """
            create table IF NOT EXISTS amzn_products (name varchar(1000),
            price float, rank integer, category varchar(500));
            """
        )
        self.cursor.execute("SET sql_notes = 1; ")
        print('Connection successful...')

    def spider_closed(self, spider):
        # disconnect from server
        self.db.close()
        print('** Spider closed **')

    def process_item(self, item, spider):
        # save the item to mysql
        print('** Saving item to MySQL **')
        self.cursor.execute(
            """
            insert into amzn_products (name,price, rank, category) values
            (%s, %s, %s, %s);
            """,
            (item['name'], item['price'], item['rank'], item['category'])
        )
        # Commit your changes in the database
        self.db.commit()
        print('Save successful...')
        return item
