import scrapy
from w3lib.html import remove_tags
import pymongo
import re
from scrapy.utils.project import get_project_settings


class EvDatabaseSpider(scrapy.Spider):
    name = "ev_database"
    allowed_domains = ["ev-database.org"]
    start_urls = ["https://ev-database.org"]

    # MongoDB connection settings
    mongo_uri = "mongodb://localhost:27017/"
    mongo_db = "evs"
    
    def __init__(self, *args, **kwargs):
        super(EvDatabaseSpider, self).__init__(*args, **kwargs)
        settings=get_project_settings()
        self.client = pymongo.MongoClient(settings.get('MONGODB_URI'))
        self.db = self.client[settings.get('MONGODB_DB')]
        collection_name = settings.get('MONGODB_COLLECTION')
        if collection_name in self.db.list_collection_names():
                self.db[collection_name].drop()
    
    def start_requests(self):
        urls = [
            "https://ev-database.org"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def closed(self, reason):
        # Close the MongoDB client when the spider is done
        self.client.close()
        
    def parse(self, response):
        # Use XPath to select all div elements with class 'data-wrapper'
        data_wrapper_divs = response.xpath('//div[@class="data-wrapper"]')

        # Iterate through each 'data-wrapper' div, strip HTML tags, and remove vertical empty spaces
        for div in data_wrapper_divs:
            img_src = div.xpath('.//div[@class="img"]/a/img/@data-src-retina').get()

            html_data = div.extract()
            text_data = remove_tags(html_data)  # Remove HTML tags
            cleaned_data = text_data.strip().replace('\n','')  # Remove vertical empty spaces
            cleaned_data = re.sub(r'\s{2,}', '\n', cleaned_data)  # Replace consecutive spaces with newline

            item = {
                'product_specification': cleaned_data,
                'image_url': img_src  # Store the image URL in the item
            }
            self.save_to_mongodb(item)
            print("Saved to MongoDB")  # Save the item to MongoDB

    def save_to_mongodb(self, item):
        collection = self.db["cars"]
        collection.insert_one(item)
