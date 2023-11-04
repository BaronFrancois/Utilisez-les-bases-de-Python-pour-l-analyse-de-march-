import requests
from bs4 import BeautifulSoup
# join Url from website image relative path
from urllib.parse import urljoin
import json
import csv

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

# 
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find_all('tr')

# URL PageProduct
product_page_url = url

# Title
title = soup.find('h1').text

# Description product
description_element = soup.find(id='product_description')
# If there is no escription
if description_element:
    product_description = description_element.find_next_sibling('p').text
else:
    product_description = "No description available"

# image URL
image_element = soup.find('img')
# Relative Path for image URL
image_url = urljoin(url, image_element['src'])


product_data = {
    "Product Page URL": product_page_url,
    "Title": title,
    "Product Description": product_description,
    "Image URL": image_url
}

data = product_data

csv_file = "output.csv"

for row in table:
    td = row.find_all('td')
    th = row.find_all('th')
    print(row.text.strip())
    product_data[th[0].text.strip()] = td[0].text.strip()



# Utilisation d'une boucle pour afficher les données
# for key, value in product_data.items():
#     print(f"{key}: {value}")

# with open('product_data.json', 'w') as json_file:
#     json.dump(product_data, json_file, indent=4)

with open(csv_file, mode="w", newline='', encoding ='utf8') as file:
    writer = csv.writer(file) #what does writer do
    writer.writerow(data.keys())
    print(f"{data.values()} DATAAAAAAAAAAA")

    writer.writerow(data.values())




# my_dict = {'key1': 'value1', 'key2': 'value2'}, you can access 'value1' by using my_dict['key1'].


my_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

# Iterating over keys
# for key in my_dict:
#     print(key)


# Iterating over values
# for value in my_dict.values():
#     print(value)


# Iterating over key-value pairs
# for key, value in my_dict.items():
#     print(f"Key: {key}, Value: {value}")


# Nest step is to add category function + create a function to use it in category "filter"