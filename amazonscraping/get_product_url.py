import MySQLdb
import yaml


class GetProductURL:
    """Get Best Seller product URLs from mysql table"""
    cnx = {
        'host': "",
        'username': "",
        'password': "",
        'db': ""
    }
    db = None
    cursor = None
    update_cursor = None

    def connect(self):
        print('Connecting MySQLdb...')
        # open config file for database credentials
        with open(".config.yaml", 'r') as stream:
            config = yaml.load(stream)
            self.cnx['host'] = config['mysql']['host']
            self.cnx['username'] = config['mysql']['username']
            self.cnx['password'] = config['mysql']['password']
            self.cnx['db'] = config['mysql']['db']
        # connect mysql
        self.db = MySQLdb.connect(
            self.cnx['host'], self.cnx['username'],
            self.cnx['password'], self.cnx['db']
        )

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()
        self.update_cursor = self.db.cursor()
        print("Connection successful...")
        print("Fetching bestseller product urls...")
        self.cursor.execute(
            """
            SELECT product_url FROM bestseller_urls WHERE scraped='no';
            """
        )
        print("ok")

    def next_url(self):
        """
        Return url to crawl by querying mysql database
        """
        next_url = self.cursor.fetchone()
        self.update_cursor.execute(
            """
            UPDATE bestseller_urls SET scraped=%s WHERE
            product_url=%s
            """,
            ('yes', next_url[0])
        )
        # Commit your changes in the database
        self.db.commit()
        yield next_url[0]
