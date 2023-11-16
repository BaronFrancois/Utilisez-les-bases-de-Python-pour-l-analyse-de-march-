# Importing required modules
import re  # For regular expressions
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML
from urllib.parse import urljoin  # For joining URLs
import csv  # For writing to CSV files
from pathlib import Path


def download_image(image_url, folder="images", file_name=None):
   # If no file name is specified, use the last part of the image URL
    if not file_name:
        file_name = image_url.split('/')[-1]
    # Replace unwanted characters in file name
    file_name = file_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    # Full path to save the image
    path_to_save = Path(folder) / file_name
    # Download and save the image
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(path_to_save, 'wb') as file:
            file.write(response.content)

# Function to extract the category from the HTML soup
def extract_category(soup):
    # Find the breadcrumb trail in the page, which usually contains the category
    breadcrumb = soup.find('ul', class_='breadcrumb')
    # If breadcrumb is found, proceed to find the category
    if breadcrumb:
        # The category is typically the second to last item in the breadcrumb
        categories = breadcrumb.find_all('li')
        category = categories[-2].get_text().strip() if len(categories) > 2 else 'No category'
        return category
    else:
        return 'No category'  # If breadcrumb is not found, return 'No category'

# Function to extract the review rating from the HTML soup
def extract_review_rating(soup):
    # Find the 'star-rating' class to get the review rating
    rating_element = soup.find('p', class_='star-rating')
    if rating_element:
        # The class attribute of the rating element contains the rating as the second class (e.g., 'Three')
        rating_text = rating_element.get('class')[1] if len(rating_element.get('class')) > 1 else "No rating"
        # Map the textual rating to a number
        rating_conversion = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return rating_conversion.get(rating_text, "No rating")
    else:
        return "No rating"  # If no rating element is found, return 'No rating'

# Function to scrape individual book details from its page
def scrape_book(url):
    # Send a request to the book page and get the response content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize a dictionary to store book details
    product_data = {
        "Product Page URL": url,  # URL of the book's product page
        "Title": soup.find('h1').text.strip(),  # Title of the book
        "Product Description": "No description available",  # Default if no description is found
        "Image URL": urljoin(url, soup.find('img')['src']) if soup.find('img') else "",  # Image URL
        "Category": extract_category(soup),  # Category of the book
        "Review Rating": extract_review_rating(soup)  # Review rating
    }

    # Find the product description paragraph following the 'product_description' element
    description_element = soup.find(id='product_description')
    if description_element:
        product_data["Product Description"] = description_element.find_next_sibling('p').text.strip()

    # Extract additional product information from the product page table
    table = soup.find_all('tr')
    for row in table:
        th = row.find('th')
        td = row.find('td')
        if th and td:
            key = th.text.strip()
            value = td.text.strip()
            if key == 'UPC':
                product_data["Universal Product Code (UPC)"] = value
            elif key == 'Price (excl. tax)':
                product_data["Price Excluding Tax"] = value.replace('Â£', '£')
            elif key == 'Price (incl. tax)':
                product_data["Price Including Tax"] = value.replace('Â£', '£')
            elif key == 'Availability':
                match = re.search(r'(\d+) available', value)
                product_data["Number Available"] = match.group(1) if match else "0"

    # Return the dictionary containing all the scraped data
    return product_data

# Function to get category URLs from the homepage
def get_category_urls(homepage_url):
    # Send a request to the homepage and parse the HTML response
    response = requests.get(homepage_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Select and extract category links from the sidebar
    category_links = soup.select('.side_categories ul li ul li a')
    # Create a dictionary to store category names and their corresponding URLs
    return {link.get_text().strip(): urljoin(homepage_url, link['href']) for link in category_links}

# Function to get product URLs for a category
def get_product_urls(category_url):
    urls = []
    while True:
        # Send a request to the category page and parse the HTML response
        response = requests.get(category_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all book articles in the category
        books = soup.find_all('article', class_='product_pod')
        # Extract and append the URLs of the book products to the 'urls' list
        urls.extend(urljoin(category_url, book.find('h3').find('a')['href']) for book in books)

        # Check for the presence of a 'next' button to paginate through pages
        next_button = soup.find('li', class_='next')
        if not next_button:
            break
        # Update the category URL to the URL of the next page
        category_url = urljoin(category_url, next_button.find('a')['href'])
    return urls

# Main script
if __name__ == "__main__":
    homepage_url = "https://books.toscrape.com/index.html"
    # Get category URLs from the homepage
    categories = get_category_urls(homepage_url)

    for category_name, category_url in categories.items():
        print(f"Processing category: {category_name}")
        # Get product URLs for the current category
        product_urls = get_product_urls(category_url)

        all_book_data = []
        for url in product_urls:
            try:
                # Scrape data for each book product
                book_data = scrape_book(url)
                if book_data:
                    all_book_data.append(book_data)
                    # Use the book title as the image file name
                    image_file_name = f"{book_data['Title'].replace(' ', '_')}.jpg"
                    download_image(book_data['Image URL'], file_name=image_file_name)  # Download the image
                    print(f"Scraped data for {book_data['Title']}")
            except Exception as e:
                print(f"Failed to scrape data for url {url}: {e}")

        if all_book_data:
            csv_file = f"csv_data/{category_name.replace(' ', '_')}_data.csv"
            with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=all_book_data[0].keys())
                writer.writeheader()
                for book_data in all_book_data:
                    writer.writerow(book_data)
            print(f"Data for category {category_name} has been written to {csv_file}")
        else:
            print(f"No data to write for category {category_name}")
