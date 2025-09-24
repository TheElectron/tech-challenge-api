import os
import csv
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DIR = 'data'
BASE_URL = 'https://books.toscrape.com/'
DB_NAME = 'tech_challenge_api.db'
CSV_NAME = 'scraped_books.csv'

def setup_database():
    """
    Function responsible for creating the SQLite database and the 'books' table if they do not exist.
    """
    print("*************************************************************************************************")
    print("Setting up the database...")
    os.makedirs(DIR, exist_ok=True)
    output_filepath = os.path.join(DIR, DB_NAME)
    conn = sqlite3.connect(output_filepath)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            rating INTEGER,
            availability TEXT,
            category TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def scrape_books():
    """
    Function responsible for extracting data from the website 'books.toscrape.com'.
    """
    all_books_data = []
    url_to_scrape = urljoin(BASE_URL, 'catalogue/page-1.html')
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
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
                try:
                    price = float(price.replace('Â£', ''))
                except ValueError:
                    price = 0.0
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
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'availability': availability,
                    'category': category,
                    'image_url': image_full_url
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
        except requests.exceptions.RequestException as e:
            print(f"\tAn error occurred accessing the page \n{url_to_scrape}: {e}")
            break
    if not all_books_data:
        print("\tWeb scraping execution failed..")
        return None
    print(f"\tTotal books scraped: {len(all_books_data)}")
    print("Ending the Web Scraping...")
    print("*************************************************************************************************")
    return all_books_data

def save_to_csv(books_data):
    """
    Salva a lista de livros em um arquivo CSV. Esta função se adapta
    automaticamente aos novos campos por usar DictWriter.
    """
    print("Saving the data in .csv format...")
    output_filepath = os.path.join(DIR, CSV_NAME)
    headers = books_data[0].keys()    
    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(books_data)
        print(f"\tData stored successfully. The file can be found at: {output_filepath}")
    except IOError as e:
        print(f"\tAn error occurred while writing the CSV file: {e}")

def save_to_sqlite(books_data):
    """
    Salva a lista de livros no banco de dados SQLite com os novos campos.
    """
    print("Saving the data in the SQLite database...")
    output_filepath = os.path.join(DIR, DB_NAME)
    conn = sqlite3.connect(output_filepath)
    cursor = conn.cursor()
    sql_insert = '''
        INSERT OR IGNORE INTO books 
        (title, price, rating, availability, category, image_url) 
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    for book in books_data:
        cursor.execute(sql_insert,
                        (
                            book['title'], 
                            book['price'], 
                            book['rating'], 
                            book['availability'], 
                            book['category'], 
                            book['image_url']
                        ))
    conn.commit()
    conn.close()
    print(f"\tData stored successfully. The database can be found at: {output_filepath}")
    print("*************************************************************************************************")

if __name__ == '__main__':
    setup_database()
    books = scrape_books()
    if books:
        save_to_csv(books)
        save_to_sqlite(books)
