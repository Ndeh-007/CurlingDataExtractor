import scrapy


class CurlingSpiderPySpider(scrapy.Spider):
    name = "curling_spider.py"
    allowed_domains = ["results.worldcurling.org"]
    start_urls = ["https://results.worldcurling.org"]

    def parse(self, response):
        pass
