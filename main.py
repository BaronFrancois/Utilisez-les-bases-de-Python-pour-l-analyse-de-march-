# Importing modules needed for various functionalities of our script.
import re  # Used for regular expressions, helpful in string manipulation.
import requests  # Enables us to make HTTP requests to web pages.
from bs4 import BeautifulSoup  # A library for parsing HTML and XML documents.
from urllib.parse import urljoin  # For constructing full URLs by combining base URL with a partial URL.
import csv  # To read from and write to CSV files, a common file format for data.
from pathlib import Path  # For file system path manipulation, making file handling easier and more readable.


# --- Section: Independent Functions ---

#6/ Called by extract_book_details(-4-) to download and save book images.
def download_book_image(image_url, category, file_name=None):
    # Creates a path object combining the 'images' folder and the book's category. It ensures neat organization.
    folder = Path("images") / category  
    # Creates the folder if it doesn't exist, avoiding errors when trying to save files.
    folder.mkdir(parents=True, exist_ok=True)  

    # If no specific file name is provided, it takes the last part of the URL as the file name.
    if not file_name:
        file_name = image_url.split('/')[-1]  

    # Cleans the file name by replacing characters that are not allowed in file names with underscores.
    file_name = re.sub(r'[\/:*?"<>|]', '_', file_name)  
    # Joins the folder path and the cleaned file name to create a full path to save the image.
    path_to_save = folder / file_name  

    # Makes an HTTP request to get the image from the provided URL.
    response = requests.get(image_url)  
    if response.status_code == 200:  # Checks if the request was successful (status code 200).
        with open(path_to_save, 'wb') as file:  # Opens the file path in write-binary mode.
            file.write(response.content)  # Writes the content of the response (image data) to the file.



#5/ Helper functions called by extract_book_details(-4-) to extract the category and review rating of a book.
# {

# 5.1/
def get_book_category(soup):
    # Searches the parsed HTML ('soup') for the breadcrumb trail, which usually contains the category information.
    breadcrumb = soup.find('ul', class_='breadcrumb')  
    if breadcrumb:  # Checks if the breadcrumb trail is found in the HTML.
        # Extracts all list items from the breadcrumb trail.
        categories = breadcrumb.find_all('li')  
        # The category is usually the second to last item; gets its text and strips any leading/trailing whitespace.
        category = categories[-2].get_text().strip() if len(categories) > 2 else 'No category'  
        return category  # Returns the extracted category.
    else:
        return 'No category'  # Returns 'No category' if the breadcrumb trail is not found.


#5.2/ Function to extract the review rating from the HTML soup
def get_book_review_rating(soup):
    # Finds the paragraph with the class 'star-rating', which contains the book's review rating.
    rating_element = soup.find('p', class_='star-rating')  
    if rating_element:  # Checks if the rating element is found.
        # Extracts the class attribute, which contains the textual rating (like 'Three').
        rating_text = rating_element.get('class')[1] if len(rating_element.get('class')) > 1 else "No rating"  
        # Maps textual ratings to numerical values.
        rating_conversion = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}  
        return rating_conversion.get(rating_text, "No rating")  # Returns the numerical rating.
    else:
        return "No rating"  # Returns 'No rating' if the rating element is not found.
# }


# --- Section: Scraping Specific Functions ---


# Main scraping function for each book. Calls get_book_category(soup)(-5.1-) and get_book_review_rating(soup)(-5.2-) to extract specific information. Can call download_book_image(6) to download the book image.
# {

#4/ Function to scrape individual book details from its page
def extract_book_details(url):
    # Sends an HTTP request to the provided book page URL and gets the response.
    response = requests.get(url)  
    # Parses the HTML content of the response.
    soup = BeautifulSoup(response.text, 'html.parser')  

    # Initializes a dictionary to store various pieces of information about the book.
    product_data = {
        "Product Page URL": url,  # Stores the URL of the book's product page.
        "Title": soup.find('h1').text.strip(),  # Finds and stores the book's title.
        "Product Description": "No description available",  # Default value for the description.
        "Image URL": urljoin(url, soup.find('img')['src']) if soup.find('img') else "",  # Constructs the full image URL.
        "Category": get_book_category(soup),  # Extracts and stores the book's category.
        "Review Rating": get_book_review_rating(soup)  # Extracts and stores the book's review rating.
    }

    # Tries to find the product description and updates it in the dictionary if found.
    description_element = soup.find(id='product_description')
    if description_element:
        product_data["Product Description"] = description_element.find_next_sibling('p').text.strip()

    # Extracts additional product information from the product page table.
    table = soup.find_all('tr')
    for row in table:
        th = row.find('th')  # Finds the table header, which contains the key (like 'UPC', 'Price').
        td = row.find('td')  # Finds the table data, which contains the value.
        if th and td:  # Checks if both key and value elements are found.
            key = th.text.strip()  # Strips whitespace from the key text.
            value = td.text.strip()  # Strips whitespace from the value text.
            # Checks for specific keys and stores their values in the dictionary, with some string manipulation if needed.
            if key == 'UPC':
                product_data["Universal Product Code (UPC)"] = value
            elif key == 'Price (excl. tax)':
                product_data["Price Excluding Tax"] = value.replace('Â£', '£')
            elif key == 'Price (incl. tax)':
                product_data["Price Including Tax"] = value.replace('Â£', '£')
            elif key == 'Availability':
                match = re.search(r'(\d+) available', value)
                product_data["Number Available"] = match.group(1) if match else "0"

    return product_data  # Returns the dictionary containing all the scraped data.
# }


# --- Section: Higher Level Functions ---


#3/ For each category, retrieve the URLs of all books. Each book URL is passed to extract_book_details(-4-).
# {

# Function to get product URLs for a category
def retrieve_books_in_category(category_url):
    urls = []  # Initializes an empty list to store book URLs.
    while True:  # Starts an infinite loop, which will break when no 'next' button is found.
        # Sends a request to the category page and parses the HTML.
        response = requests.get(category_url)  
        soup = BeautifulSoup(response.text, 'html.parser')  
        # Finds all book articles on the category page.
        books = soup.find_all('article', class_='product_pod')  
        # Loops through each book and extracts its product page URL, adding it to the 'urls' list.
        urls.extend(urljoin(category_url, book.find('h3').find('a')['href']) for book in books)

        # Looks for a 'next' button to move to the next page of the category.
        next_button = soup.find('li', class_='next')  
        if not next_button:  # If no 'next' button is found, breaks out of the loop.
            break
        # Updates the category URL to point to the next page.
        category_url = urljoin(category_url, next_button.find('a')['href'])  
    return urls  # Returns the list of all product URLs found in the category.

# }

#2/ Retrieves category links from the home page.Each category link is then processed by retrieve_books_in_category(-3-).

# {
# Function to get category URLs from the homepage
def retrieve_category_links(homepage_url):
    # Sends an HTTP request to the homepage and parses the HTML response.
    response = requests.get(homepage_url)  
    soup = BeautifulSoup(response.text, 'html.parser')  
    # Selects category links from the sidebar of the webpage.
    category_links = soup.select('.side_categories ul li ul li a')  
    # Creates a dictionary mapping category names to their URLs.
    return {link.get_text().strip(): urljoin(homepage_url, link['href']) for link in category_links}
# }


# --- Section: Point d'Entrée Principal ---


# 1/ Starts the scraping process. Call retrieve_category_links(-2-) directly and iterate through each category.
# {

# Main script
if __name__ == "__main__":
    # This conditional checks if the script is being run as the main program and not being imported as a module.
    homepage_url = "https://books.toscrape.com/index.html"
    # Sets the homepage URL of the website from which we are scraping data.

    # Retrieve category links from the homepage
    categories = retrieve_category_links(homepage_url)
    # Calls the function 'retrieve_category_links' to get a dictionary of category names and their corresponding URLs.

    for category_name, category_url in categories.items():
        # Iterates over each category name and URL in the 'categories' dictionary.
        print(f"Processing category: {category_name}")
        # Prints the name of the current category being processed.

        # Get product URLs for the current category
        product_urls = retrieve_books_in_category(category_url)
        # Calls the function 'retrieve_books_in_category' to get a list of all book URLs in the current category.

        all_book_data = []
        # Initializes an empty list to store details of all books in the current category.

        for url in product_urls:
            # Iterates over each book URL in the current category.
            try:
                # Tries to execute the following block of code.
                book_data = extract_book_details(url)
                # Calls 'extract_book_details' function to scrape details of the book from its URL.

                if book_data:
                    # Checks if book_data is not empty.
                    all_book_data.append(book_data)
                    # Adds the scraped book data to the 'all_book_data' list.

                    image_file_name = f"{book_data['Title'].replace(' ', '_')}.jpg"
                    # Formats the file name for the book's image using the book's title.

                    download_book_image(book_data['Image URL'], book_data['Category'], file_name=image_file_name)
                    # Calls 'download_book_image' to download the book image and save it in the respective category folder.

                    print(f"Scraped data for {book_data['Title']}")
                    # Prints a message indicating successful data scraping for the current book.

            except Exception as e:
                # Catches any exception that might occur during the try block.
                print(f"Failed to scrape data for url {url}: {e}")
                # Prints a message indicating failure in data scraping along with the error.

        if all_book_data:
            # create folder for csv data if it doesn't exists.
            Path("csv_data").mkdir(parents=True, exist_ok=True)
            # Checks if there is any book data collected for the current category.
            csv_file = f"csv_data/{category_name.replace(' ', '_')}_data.csv"
            # Sets the file path for the CSV file where the data will be saved, named after the category.

            with open(csv_file, mode="w", newline='', encoding='utf-8') as file:
                # Opens a CSV file in write mode and ensures proper encoding.
                writer = csv.DictWriter(file, fieldnames=all_book_data[0].keys())
                # Creates a CSV writer object with fieldnames set to the keys of the first book's data.

                writer.writeheader()
                # Writes the header row in the CSV file.

                for book_data in all_book_data:
                    # Iterates over each book's data in the current category.
                    writer.writerow(book_data)
                    # Writes the book's data as a row in the CSV file.

            print(f"Data for category {category_name} has been written to {csv_file}")
            # Prints a message indicating successful writing of data to the CSV file for the current category.

        else:
            # Executes if no book data was collected for the current category.
            print(f"No data to write for category {category_name}")
            # Prints a message indicating that there is no data to write for the current category.
# }
