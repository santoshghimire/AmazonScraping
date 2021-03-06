# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import yaml
from scrapy import signals
from .decorator import check_spider_pipeline, check_spider_connection


class AmazonscrapingPipeline(object):

    cnx = {
        'host': "",
        'username': "",
        'password': "",
        'db': ""
    }
    db = None
    cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    @check_spider_connection
    def spider_opened(self, spider):
        """ Connect to RDS MySQL database when spider is opened """
        print('** Spider opened, connecting to MySQLdb **')

        # open config file for database credentials
        with open(".config.yaml", 'r') as stream:
            config = yaml.load(stream)
            self.cnx['host'] = config['mysql']['host']
            self.cnx['username'] = config['mysql']['username']
            self.cnx['password'] = config['mysql']['password']
            self.cnx['db'] = config['mysql']['db']
        try:
            # connect mysql
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
                price varchar(100), rank integer, category varchar(500),
                url varchar(1000), shipping_weight varchar(100),
                item_model_number varchar(200), badge_count integer,
                amazon_seller varchar(10), asin varchar(100));
                """
            )
            self.cursor.execute("SET sql_notes = 1; ")
            print('Connection successful...')
        except:
            print('Connection failed !!!')

    @check_spider_connection
    def spider_closed(self, spider):
        # disconnect from server
        try:
            self.db.close()
            print('** Spider closed, MySQL disconnected. **')
        except:
            print('** Spider closed. **')

    @check_spider_pipeline
    def process_item(self, item, spider):
        """ Process the scraped item """
        try:
            # save the item to mysql
            print('** Saving item to MySQL **')
            self.cursor.execute(
                """
                insert into amzn_products (name, price, rank, category,
                url, shipping_weight, item_model_number, badge_count,
                amazon_seller, asin) values
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    item['name'], item['price'], item['rank'],
                    item['category'],
                    item['url'], item['shipping_weight'],
                    item['item_model_number'],
                    item['badge_count'], item['amazon_seller'],
                    item['asin']
                )
            )
            # Commit your changes in the database
            self.db.commit()
            print('Save successful...')
        except:
            print('Save failed !!!')
        return item


class BestSellerCategoryPipeline(object):

    cnx = {
        'host': "",
        'username': "",
        'password': "",
        'db': ""
    }
    db = None
    cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    @check_spider_connection
    def spider_opened(self, spider):
        """ Connect to RDS MySQL database when spider is opened """
        print('** Spider opened, connecting to MySQLdb **')

        # open config file for database credentials
        with open(".config.yaml", 'r') as stream:
            config = yaml.load(stream)
            self.cnx['host'] = config['mysql']['host']
            self.cnx['username'] = config['mysql']['username']
            self.cnx['password'] = config['mysql']['password']
            self.cnx['db'] = config['mysql']['db']
        try:
            # connect mysql
            self.db = MySQLdb.connect(
                self.cnx['host'], self.cnx['username'],
                self.cnx['password'], self.cnx['db']
            )

            # prepare a cursor object using cursor() method
            self.cursor = self.db.cursor()

            self.cursor.execute("SET sql_notes = 0; ")
            self.cursor.execute(
                """
                create table IF NOT EXISTS bestseller_categories
                (
                    name varchar(200),
                    url varchar(500), parent_category varchar(200),
                    main_category varchar(200),
                    scraped varchar(10) default 'no'
                );
                """
            )
            self.cursor.execute("SET sql_notes = 1; ")
            print('Connection successful...')
        except:
            print('Connection failed !!!')

    @check_spider_connection
    def spider_closed(self, spider):
        # disconnect from server
        try:
            self.db.close()
            print('** Spider closed, MySQL disconnected. **')
        except:
            print('** Spider closed. **')

    @check_spider_pipeline
    def process_item(self, item, spider):
        """ Process the scraped item """
        try:
            # save the item to mysql
            print('** Saving item to MySQL **')
            self.cursor.execute(
                """
                insert into bestseller_categories (
                    name, url, parent_category,
                    main_category
                ) values(
                    %s, %s, %s, %s
                );
                """,
                (
                    item['name'], item['url'], item['parent_category'],
                    item['main_category']
                )
            )
            # Commit your changes in the database
            self.db.commit()
            print('Save successful...')
        except:
            print('Save failed !!!')
        return item


class BestSellerPipeline(object):

    cnx = {
        'host': "",
        'username': "",
        'password': "",
        'db': ""
    }
    db = None
    cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    @check_spider_connection
    def spider_opened(self, spider):
        """ Connect to RDS MySQL database when spider is opened """
        print('** Spider opened, connecting to MySQLdb **')

        # open config file for database credentials
        with open(".config.yaml", 'r') as stream:
            config = yaml.load(stream)
            self.cnx['host'] = config['mysql']['host']
            self.cnx['username'] = config['mysql']['username']
            self.cnx['password'] = config['mysql']['password']
            self.cnx['db'] = config['mysql']['db']
        try:
            # connect mysql
            self.db = MySQLdb.connect(
                self.cnx['host'], self.cnx['username'],
                self.cnx['password'], self.cnx['db']
            )

            # prepare a cursor object using cursor() method
            self.cursor = self.db.cursor()

            self.cursor.execute("SET sql_notes = 0; ")
            self.cursor.execute(
                """
                create table IF NOT EXISTS product_urls
                (
                    product_url varchar(500),
                    category_url varchar(500),
                    scraped varchar(10) default 'no'
                );
                """
            )
            self.cursor.execute("SET sql_notes = 1; ")
            print('Connection successful...')
        except:
            print('Connection failed !!!')

    @check_spider_connection
    def spider_closed(self, spider):
        # disconnect from server
        try:
            self.db.close()
            print('** Spider closed, MySQL disconnected. **')
        except:
            print('** Spider closed. **')

    @check_spider_pipeline
    def process_item(self, item, spider):
        """ Process the scraped item """
        try:
            # save the item to mysql
            print('** Saving item to MySQL **')
            self.cursor.execute(
                """
                insert into product_urls (
                    product_url, category_url
                ) values(
                    %s, %s
                );
                """,
                (
                    item['product_url'], item['category_url']
                )
            )
            # Commit your changes in the database
            self.db.commit()
            print('Save successful...')
        except:
            print('Save failed !!!')
        return item
