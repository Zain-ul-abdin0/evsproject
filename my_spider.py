import scrapy
from bs4 import BeautifulSoup
from pymongo import MongoClient

class EVDatabaseSpider(scrapy.Spider):
    name = 'ev_database'
    start_urls = ['https://ev-database.org/']

    def parse(self, response):
        # Open a connection to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["evs"]
        collection = db["mostrecent"]

        # Find the "View all" link and follow it
        view_all_link = response.css('div.jplist-dd-panel a::attr(href)').get()
        yield response.follow(view_all_link, self.parse_view_all)

    def parse_view_all(self, response):
        # Find and click the "Show 100" button
        show_100_button = response.xpath('/html/body/main/div[2]/div[6]/div[2]/div/ul/li[5]/span/a/@href').get()
        yield response.follow(show_100_button, self.parse_show_100)

    def parse_show_100(self, response):
        # Find all data-wrapper elements
        data_wrappers = response.css('.data-wrapper')

        # Initialize a dictionary to store the data
        data_dict = {}

        # Function to remove empty lines from a string
        def remove_empty_lines(text):
            lines = text.splitlines()
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            return '\n'.join(non_empty_lines)

        # Loop through the data-wrapper elements
        for data_wrapper in data_wrappers:
            # Extract the inner HTML of each data-wrapper element
            data_html = data_wrapper.extract()

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(data_html, 'html.parser')

            # Get the name (assuming it's in a specific element, adjust as needed)
            name_element = soup.find('h2')
            name = name_element.get_text() if name_element else "No Name Found"

            # Get the text content (remove HTML tags)
            text_content = soup.get_text()

            # Remove empty lines from the text content
            cleaned_text_content = remove_empty_lines(text_content)

            # Store the data in the dictionary with the name as the key
            data_dict[name] = cleaned_text_content

        # Insert the data into MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["evs"]
        collection = db["mostrecent"]
        collection.insert_one(data_dict)

        # Print the data
        for name, content in data_dict.items():
            self.log(f"Name: {name}")
            self.log(f"Data:\n{content}")
            self.log("------")

        # Close the MongoDB connection
        client.close()
