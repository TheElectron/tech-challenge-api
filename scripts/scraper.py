import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_books():
    """
        Function responsible for extracting data from the website 'books.toscrape.com' and storing it in CSV format.
    """
    all_books_data = []
    base_url = "https://books.toscrape.com/"
    url_to_scrape = urljoin(base_url, 'catalogue/page-1.html')
    rating_map = {
        'One': '1',
        'Two': '2',
        'Three': '3',
        'Four': '4',
        'Five': '5'
        }
    print("*************************************************************************************************")
    print("Starting the Web Scraping...")
    while url_to_scrape:
        print(f"\tPage: {url_to_scrape}")
        try:
            response = requests.get(url_to_scrape)
            response.raise_for_status() # Raise an exception for bad HTTP status (4xx or 5xx).
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get all books on the listing page.
            # Each book is inside an <article class="product_pod"> tag.
            books_on_page = soup.find_all('article', class_='product_pod')
            for book in books_on_page:
                # Get url to the book detail page.
                book_relative_url = book.find('h3').find('a')['href']
                book_full_url = urljoin(url_to_scrape, book_relative_url)
                
                # Book detail
                book_response = requests.get(book_full_url)
                book_response.raise_for_status()
                book_soup = BeautifulSoup(book_response.text, 'html.parser')
                
                title = book_soup.find('h1').text
                price = book_soup.find('p', class_='price_color').text
                
                # Rating => class="star-rating"
                rating_class = book_soup.find('p', class_='star-rating')['class']
                rating = rating_map.get(rating_class[1], '0')
                
                availability_text = book_soup.find('p', class_='instock availability').text.strip()
                availability = ''.join(filter(str.isdigit, availability_text))
                
                # category => class="breadcrumb"
                category = book_soup.find('ul', class_='breadcrumb').find_all('li')[2].find('a').text
                
                image_relative_url = book_soup.find('div', id='product_gallery').find('img')['src']
                image_full_url = urljoin(book_full_url, image_relative_url)
                
                # print(f"\t{title} | {price} | {rating} | {availability} | {category}")
                book_data = {
                    'Title': title,
                    'Price': price,
                    'Rating': rating,
                    'Availability': availability,
                    'Category': category,
                    'Image': image_full_url
                }
                all_books_data.append(book_data)
                time.sleep(0.1)
            # Netx page
            next_button = soup.find('li', class_='next')
            if next_button:
                next_page_relative_url = next_button.find('a')['href']
                url_to_scrape = urljoin(url_to_scrape, next_page_relative_url)
            else:
                url_to_scrape = None
                print("\n\tEnding the Web Scraping...")
        except requests.exceptions.RequestException as e:
            print(f"\tAn error occurred accessing the page \n{url_to_scrape}: {e}")
            break
    if not all_books_data:
        print("\tNo data was found.\n\tThe CSV file will not be generated..")
        return
    # Saving the data in .csv format
    output_dir = 'data'
    output_filename  = 'scraped_books.csv'
    output_filepath = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)
    headers = all_books_data[0].keys()    
    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_books_data)
        print(f"\tData stored successfully. The file can be found at: {output_filepath}")
    except IOError as e:
        print(f"\tAn error occurred while writing the CSV file: {e}")

if __name__ == '__main__':
    scrape_books()