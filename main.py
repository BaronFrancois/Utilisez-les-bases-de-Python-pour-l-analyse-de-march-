import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find_all('tr')

for row in table:
    print(row.text.strip())