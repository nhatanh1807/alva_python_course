import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

chromedriver_path = 'C:\\Users\\ADMIN\\Downloads\\chromedriver-win64\\chromedriver.exe'
# Initialize the WebDriver using the specified path
service = Service(executable_path=chromedriver_path)
chrome_options = webdriver.ChromeOptions()
wd = webdriver.Chrome(service=service, options=chrome_options)

def add_data(names, prices, links, delivery_dates, last_month_boughts, ratings, rate_turns, num_lefts, ships):
    elements = wd.find_elements(By.CSS_SELECTOR, ".s-main-slot .s-result-item")
    for element in elements:
        try:
            name = element.find_element(By.CSS_SELECTOR, "h2 a span").text
            price = element.find_element(By.CSS_SELECTOR, ".a-price-whole").text
            link = element.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
            delivery_date_elements = element.find_elements(By.CSS_SELECTOR, '[aria-label^="Delivery"]')
            delivery_date = delivery_date_elements[0].get_attribute("aria-label") if delivery_date_elements else "N/A"
            # Extract last month bought
            last_month_bought_elements = element.find_elements(By.CSS_SELECTOR, ".a-size-base.a-color-secondary")
            last_month_bought = last_month_bought_elements[0].text if last_month_bought_elements else "N/A"
            # Extract rating
            rating_elements = element.find_elements(By.CSS_SELECTOR, '[aria-label*="out of 5 stars"]')
            rating = rating_elements[0].get_attribute("aria-label") if rating_elements else "N/A"
             # Extract number of reviews
            review_elements = element.find_elements(By.CSS_SELECTOR, ".a-size-base.s-underline-text")
            rate_turn = review_elements[0].text if review_elements else "N/A"
            # Extract num_lefts
            num_left_elements = element.find_elements(By.CSS_SELECTOR, ".a-truncate-full.a-offscreen")
            num_left = num_left_elements[0].text if num_left_elements else "N/A"
            # Extract shipping information
            ship_elements = element.find_elements(By.CSS_SELECTOR, ".a-size-small.a-color-base")
            ship = ship_elements[0].text if ship_elements else "N/A"
            names.append(name)
            prices.append(price)
            links.append(link)
            delivery_dates.append(delivery_date)
            last_month_boughts.append(last_month_bought)
            ratings.append(rating)
            rate_turns.append(rate_turn)
            num_lefts.append(num_left)
            ships.append(ship)
        except Exception as e:
            print(f"Error occurred while extracting data: {e}")
    return names, prices, links, delivery_dates, last_month_boughts, ratings, rate_turns, num_lefts, ships

try:
    # Open the URL
    url = "https://www.amazon.vn/"
    wd.get(url)

    # Find the search box element
    element = WebDriverWait(wd, 10).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )

    # Type "Laptop" into the search box and hit enter
    element.send_keys("Laptop")
    element.send_keys(Keys.ENTER)

    # Wait for the results to load
    WebDriverWait(wd, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".s-main-slot .s-result-item"))
    )

    # Initialize lists to store data
    names, prices, links, delivery_dates, last_month_boughts, ratings, rate_turns, num_lefts, ships = [], [], [], [], [], [], [], [], []

    # Set the number of pages to scrape
    max_pages = 500
    current_page = 1

    # Loop through pagination
    while current_page <= max_pages:
        try:
            # Collect data from the current page
            names, prices, links, delivery_dates, last_month_boughts, ratings, rate_turns, num_lefts, ships = add_data(names, prices, links, delivery_dates, last_month_boughts, ratings, rate_turns, num_lefts, ships)

            # Check if the "Next" button is available
            next_button = WebDriverWait(wd, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".s-pagination-next"))
            )
            next_button.click()
            # Wait for a few seconds to ensure the next page loads properly
            time.sleep(2)

            # Wait for the next page to load
            WebDriverWait(wd, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".s-main-slot .s-result-item"))
            )

            # Increment the page counter
            current_page += 1
        except Exception as e:
            print(f"No more pages or error occurred: {e}")
            break

    # Convert to DataFrame
    df = pd.DataFrame({
        'Name': names,
        'Price': prices,
        'Link': links,
        'ngay_giao_hang' : delivery_dates,
        'luot_mua_thang_truoc' : last_month_boughts,
        'diem_danh_gia' : ratings,
        'luot_danh_gia' : rate_turns,
        'so_option_khac' : num_lefts,
        'ship' : ships
    })

    # Print DataFrame
    print(df)

    # Check if DataFrame is empty
    if df.empty:
        print("No data was scraped.")
    else:
    # Use the current working directory if __file__ is not defined
        script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        file_path = os.path.join(script_dir, 'ama_laptop.csv')
        print(f"Saving CSV to: {file_path}")
        df.to_csv(file_path, index=False)
        print("CSV file saved successfully.")

finally:
    # Ensure the WebDriver is closed properly
    wd.quit()