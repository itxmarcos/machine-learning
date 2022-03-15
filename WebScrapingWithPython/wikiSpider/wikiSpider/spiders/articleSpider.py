from scrapy.spiders import CrawlSpider, Rule
from wikiSpider.items import Article
from scrapy.linkextractors import LinkExtractor

"""
Command to scrape:
    scrapy crawl article -s LOG_FILE=wiki.log
    scrapy crawl article -o articles.csv -t csv
    scrapy crawl article -o articles.json -t json
    scrapy crawl article -o articles.xml -t xml
"""

class ArticleSpider(CrawlSpider):
    name="article"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["http://en.wikipedia.org/wiki/Python_%28programming_language%29"]
    rules = [Rule(LinkExtractor(allow=('(/wiki/)((?!:).)*$'),), callback="parse_item", follow=True)]

    def parse_item(self, response):
        item = Article()
        title = response.xpath('//h1/text()')[0].extract()
        print(f"Title is: {title}")
        item['title'] = title
        return item
