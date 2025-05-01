import sqlite3
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def create_database():
    """Create SQLite database and table for storing book data"""
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    
    # Drop table if it exists
    cursor.execute('DROP TABLE IF EXISTS books')
    
    # Create table
    cursor.execute('''
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price REAL,
        rating INTEGER,
        availability INTEGER,
        product_url TEXT
    )
    ''')
    
    conn.commit()
    return conn

def setup_driver():
    """Set up and return a Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def convert_rating_to_number(rating_class):
    """Convert rating class to numeric value"""
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    # Extract the rating part from the class name (e.g., 'star-rating Three' -> 'Three')
    rating_text = rating_class.split()[-1] if rating_class else ''
    return rating_map.get(rating_text, 0)

def extract_availability_count(availability_text):
    """Extract availability number from text"""
    if availability_text:
        match = re.search(r'In stock \((\d+) available\)', availability_text)
        if match:
            return int(match.group(1))
    return 0

def wait_random():
    """Wait for a random amount of time to avoid overwhelming the server"""
    time.sleep(random.uniform(1, 3))

def scrape_books():
    """Scrape books from books.toscrape.com"""
    base_url = "http://books.toscrape.com/"
    driver = setup_driver()
    conn = create_database()
    cursor = conn.cursor()
    
    try:
        # Start with the first page
        current_page_url = base_url + "catalogue/page-1.html"
        page_num = 1
        total_books = 0
        
        while current_page_url:
            print(f"Scraping page {page_num}...")
            driver.get(current_page_url)
            
            # Wait for the page to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
                )
            except TimeoutException:
                print(f"Timeout waiting for page {page_num} to load")
                break
            
            # Find all book containers
            book_elements = driver.find_elements(By.CLASS_NAME, "product_pod")
            
            # Process each book on this page
            for book in book_elements:
                try:
                    # Extract book URL
                    link_element = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
                    book_url = link_element.get_attribute("href")
                    
                    # Navigate to the book's detailed page
                    wait_random()
                    driver.get(book_url)
                    
                    # Wait for detail page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product_main"))
                    )
                    
                    # Extract book details
                    title = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text
                    price_text = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
                    price = float(price_text.replace('£', ''))
                    
                    rating_element = driver.find_element(By.CSS_SELECTOR, "p.star-rating")
                    rating_class = rating_element.get_attribute("class")
                    rating = convert_rating_to_number(rating_class)
                    
                    availability_text = driver.find_element(By.CSS_SELECTOR, "p.availability").text
                    availability = extract_availability_count(availability_text)
                    
                    # Store in database
                    cursor.execute(
                        "INSERT INTO books (title, price, rating, availability, product_url) VALUES (?, ?, ?, ?, ?)",
                        (title, price, rating, availability, book_url)
                    )
                    conn.commit()
                    
                    total_books += 1
                    print(f"Added book: {title} - £{price} - Rating: {rating}")
                    
                    # Go back to the catalog page
                    driver.back()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
                    )
                
                except Exception as e:
                    print(f"Error processing book: {e}")
                    driver.get(current_page_url)  # Get back to catalog page
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
                    )
            
            # Check if there's a next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
                next_page_relative_url = next_button.get_attribute("href")
                current_page_url = next_page_relative_url
                page_num += 1
            except NoSuchElementException:
                # No more pages
                current_page_url = None
        
        print(f"Scraping complete! Total books collected: {total_books}")
    
    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    scrape_books()