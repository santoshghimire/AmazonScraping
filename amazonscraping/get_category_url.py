import MySQLdb
import yaml


class GetBestSellerCategoryURL:
    """Get Best Seller Category URL from mysql table"""
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
        print("Fetching bestseller categories urls...")
        # SELECT URL FROM bestseller_categories;
        self.cursor.execute(
            """
            SELECT URL FROM bestseller_categories WHERE scraped='no';
            """
        )
        print("ok")

    def next_url(self):
        """
        Generate a list of URLs to crawl by querying mysql database
        """
        next_url = self.cursor.fetchone()
        self.update_cursor.execute(
            """
            UPDATE bestseller_categories SET scraped=%s WHERE
            url=%s
            """,
            ('yes', next_url[0])
        )
        # Commit your changes in the database
        self.db.commit()
        yield next_url[0]
