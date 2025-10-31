import scrapy

class RawHtmlSpider(scrapy.Spider):
    name = "raw_html"
    custom_settings = {
        "LOG_ENABLED": False
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("Pass start URL via -a url=https://...")
        self.start_urls = [url]

    def parse(self, response):
        yield {
            "url": response.url,
            "status": response.status,
            "html": response.text
        }
