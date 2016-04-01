# AmazonScraping
Scraping amazon products

# Installation
pip install -r requirements.txt

# Usage
-  Copy file .config_samply.yaml to .config.yaml and update the credentials

-  scrapy crawl adc -a url="AMAZON PRODUCT URL"

# Generating output csv
scrapy crawl adc -a url="AMAZON PRODUCT URL" -o data.csv