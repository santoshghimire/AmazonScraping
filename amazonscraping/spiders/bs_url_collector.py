import scrapy
from scrapy.http import Request

from amazonscraping.items import BestSellerCategoryLink
from amazonscraping.pipelines import BestSellerCategoryPipeline


class BestSellerCategoryURLCollector(scrapy.Spider):
    """
    This is the spider that crawls the given start_urls.
    """
    name = "bestseller"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/Best-Sellers/zgbs/'
    ]
    noparse_category = [
        "Appstore for Android", "MP3 Downloads",
        "Kindle Store"
    ]

    pipeline = set([
        BestSellerCategoryPipeline
    ])

    def parse(self, response):
        item = BestSellerCategoryLink()
        main_categories = response.xpath(
            "//ul[@id='zg_browseRoot']/ul/li/a"
        )
        # main_categories = [main_categories[0]]
        for main_category in main_categories:
            category_name = main_category.xpath(
                "text()"
            ).extract()[0]
            if category_name not in self.noparse_category:
                category_url = main_category.xpath(
                    "@href"
                ).extract()[0]

                item['name'] = category_name
                item['url'] = category_url
                item['parent_category'] = category_name
                item['main_category'] = category_name
                yield item

                yield Request(
                    category_url, callback=self.parse_sub_category
                )

    def parse_sub_category(self, response):
        sub_categories = response.xpath(
            "//span[@class='zg_selected']/../following-sibling::ul/li/a"
        )
        if sub_categories:
            for sub_cat in sub_categories:
                item = BestSellerCategoryLink()
                name = sub_cat.xpath("text()").extract()[0]
                url = sub_cat.xpath("@href").extract()[0]

                # get parent category name
                # parent = response.xpath(
                #     "//span[@class='zg_selected']/parent::li/"
                #     "parent::ul/preceding-sibling::li"
                # )
                # parent_category = parent.xpath("a/text()").extract()[0]

                parent = response.xpath(
                    "//span[@class='zg_selected']/parent::li"
                )
                parent_category = parent.xpath("span/text()").extract()[0]

                # get main category name
                while True:
                    main_parent = parent.xpath(
                        "parent::ul/preceding-sibling::li"
                    )
                    try:
                        actual_main_parent = parent.xpath(
                            "a/text()"
                        ).extract()[0]
                    except:
                        # if main parent is selected
                        actual_main_parent = parent.xpath(
                            "span/text()"
                        ).extract()[0]
                    main_parent_name = main_parent.xpath(
                        "a/text()"
                    ).extract()[0]
                    if main_parent_name == 'Any Department':
                        break
                    else:
                        parent = main_parent

                # set current item details
                item['name'] = name
                item['url'] = url
                item['parent_category'] = parent_category
                item['main_category'] = actual_main_parent
                yield item

                yield Request(
                    url, callback=self.parse_sub_category
                )
