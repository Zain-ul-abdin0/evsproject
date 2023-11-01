import scrapy

class GoogleSpider(scrapy.Spider):
    name = 'google'
    start_urls = ['https://www.google.com']

    def parse(self, response):
        # Your scraping logic here
        pass

# Run the spider
process = scrapy.crawler.CrawlerProcess()
process.crawl(GoogleSpider)
process.start()
