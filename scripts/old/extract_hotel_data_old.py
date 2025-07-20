import csv
import sys
import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

logging.basicConfig(filename='extract_hotel_data.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def extract_details(driver, link):
    driver.get(link)
    wait = WebDriverWait(driver, 15)
    try:
        detail_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
    except TimeoutException:
        logging.warning(f"Detail pane did not load for {link}, skipping...")
        return None
    time.sleep(1)
    # Extract name
    try:
        name = detail_pane.find_element(By.CSS_SELECTOR, 'h1.DUwDvf, span.iD2gKb, div.qBF1Pd span, div.qBF1Pd, h3, div[role="heading"]').text.strip()
    except Exception:
        name = ''
    # Extract address
    try:
        address = detail_pane.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"] div.Io6YTe, div.Io6YTe').text.strip()
    except Exception:
        address = ''
    # Extract phone
    try:
        phone = ''
        phone_btn = detail_pane.find_element(By.CSS_SELECTOR, 'button[aria-label^="Phone:"]')
        if phone_btn is not None:
            phone_label = phone_btn.get_attribute('aria-label')
            if phone_label:
                phone = phone_label.replace('Phone:', '').strip()
    except Exception:
        phone = ''
    # Extract website
    try:
        website_btn = detail_pane.find_element(By.CSS_SELECTOR, 'a[aria-label^="Website:"]')
        website = website_btn.get_attribute('href')
    except Exception:
        website = ''
    # Extract email (rare, best effort)
    try:
        email = ''
        all_text = detail_pane.text
        for word in all_text.split():
            if '@' in word and '.' in word:
                email = word
                break
    except Exception:
        email = ''
    # Extract image
    try:
        img_elem = detail_pane.find_element(By.CSS_SELECTOR, 'img')
        img_url = img_elem.get_attribute('src')
    except Exception:
        img_url = ''
    return {
        'name': name,
        'address': address,
        'phone': phone,
        'email': email,
        'website': website,
        'image_url': img_url,
        'link': link
    }

def main():
    area = sys.argv[1] if len(sys.argv) > 1 else 'Lagos'
    input_file = f'{area}_hotel_list.csv'
    output_file = f'{area}_hotel_data.csv'
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        return
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            hotels = list(reader)
        hotel_data = []
        for i, hotel in enumerate(hotels):
            link = hotel['link']
            logging.info(f"Processing {i+1}/{len(hotels)}: {link}")
            details = extract_details(driver, link)
            if details:
                hotel_data.append(details)
                logging.info(f"Extracted: {details}")
            time.sleep(2)
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'address', 'phone', 'email', 'website', 'image_url', 'link'])
            writer.writeheader()
            for row in hotel_data:
                writer.writerow(row)
        print(f"Saved hotel data to {output_file}")
    finally:
        driver.quit()

if __name__ == '__main__':
    main() 