# Importing required modules
import re  # For regular expressions
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML
from urllib.parse import urljoin  # For joining URLs
import csv  # For writing to CSV files

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

# Function to scrape the listing page and get all book URLs
def scrape_listing_page(url):
    # Send a request to the listing page and get the response content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all book entries on the page
    books = soup.find_all('article', class_='product_pod')

    # List to store URLs of individual book pages
    book_urls = [urljoin(url, book.find('h3').find('a')['href']) for book in books]

    # Return the list of URLs
    return book_urls

# Main script execution
if __name__ == "__main__":
    # URL of the page with book listings
    listing_url = "https://books.toscrape.com/catalogue/category/books_1/index.html"
    # Scrape the listing page for book URLs
    book_urls = scrape_listing_page(listing_url)

    # List to store data of all books
    all_book_data = []

    # Loop through each book URL to scrape information
    for url in book_urls:
        try:
            # Scrape data for the current book
            book_data = scrape_book(url)
            # Add the scraped data to the list
            all_book_data.append(book_data)
            # Print the title of the book that was just scraped
            print(f"Scraped data for {book_data['Title']}")
        except Exception as e:
            # Print an error message if scraping fails
            print(f"Failed to scrape data for url {url}: {e}")

    # Write the scraped data to a CSV file
    csv_file = "books_data.csv"
    with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=all_book_data[0].keys())
        writer.writeheader()
        for book_data in all_book_data:
            writer.writerow(book_data)

    # Print a message indicating the completion of the CSV writing process
    print(f"Data for all books has been written to {csv_file}")
