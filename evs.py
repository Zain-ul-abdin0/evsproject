from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import pymongo

# Configure Firefox options
firefox_options = Options()

# Create a Firefox browser instance
driver = webdriver.Firefox(options=firefox_options)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["evs"]
collection = db["mostrecent"]


# Open the website
website_url = "https://ev-database.org/"
driver.get(website_url)

dropdown_element = driver.find_element(By.CSS_SELECTOR, ".jplist-dd-panel")  # Replace with the actual locator strategy and value

view_all = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[6]/div[2]/div/div')
view_all.click()

button_element = driver.find_element(By.XPATH, "/html/body/main/div[2]/div[6]/div[2]/div/ul/li[5]/span")
driver.execute_script("arguments[0].scrollIntoView();", button_element)
button_element.click()

driver.get(driver.current_url)

# Find all data-wrapper elements
data_wrappers = driver.find_elements(By.CSS_SELECTOR, '.data-wrapper')

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
    data_html = data_wrapper.get_attribute('innerHTML')
    
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


# Print the dictionary
collection.insert_one(data_dict)

for name, content in data_dict.items():
    print(f"Name: {name}")
    print(f"Data:\n{content}")
    print("------")

# Close the browser window when done
time.sleep(100)
client.close()

driver.quit()
