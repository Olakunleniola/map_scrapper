from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import sys
import logging

# Set up Selenium WebDriver with Chrome
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
# Uncomment the next line to run headless (no browser window)
# options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Set up logging to file
logging.basicConfig(filename='scrape.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

try:
    print("Opening Google Maps...")
    driver.get('https://www.google.com/maps')
    wait = WebDriverWait(driver, 20)

    # Handle Google consent popup if it appears
    try:
        print("Checking for consent popup...")
        consent_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Accept all") or contains(., "I agree") or contains(., "Accept") or contains(., "AGREE")]'))
        )
        consent_button.click()
        print("Consent popup accepted.")
        time.sleep(1)
    except Exception:
        print("No consent popup found.")
        pass  # No consent popup

    # Manual pause for user to accept cookies if needed
    input("If you see a cookie/consent popup, please accept it in the browser, then press Enter here to continue...")

    print(f"Page title: {driver.title}")
    print(f"Page URL: {driver.current_url}")

    print("Waiting for search box...")
    try:
        # Try the original ID selector
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'searchboxinput')))
        print("Search box found by ID.")
    except Exception:
        print("Search box not found by ID. Trying alternate selector...")
        # Try a more flexible selector (input with placeholder 'Search Google Maps')
        try:
            search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search Google Maps"]')))
            print("Search box found by placeholder.")
        except Exception:
            print("Search box not found by alternate selector. Saving page source for debugging.")
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Page source saved to 'page_source.html'. Please check this file to see what the browser is displaying.")
            driver.quit()
            exit(1)

    # Get area from command-line argument
    area = sys.argv[1] if len(sys.argv) > 1 else 'Lagos'
    search_query = f"hotels near {area}, Lagos, Nigeria"
    print(f"Search query: {search_query}")

    print("Submitting search...")
    search_box.clear()
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.ENTER)

    # Take a screenshot after submitting the search
    screenshot_path = os.path.join(os.getcwd(), 'after_search.png')
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot taken after search: {screenshot_path}")

    print("Looking for results containers with aria-label containing 'Results for hotels'...")
    containers = []
    try:
        # Wait for any div with aria-label containing 'Results for hotels' (case-insensitive)
        wait.until(lambda d: len(d.find_elements(By.XPATH, '//div[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "results for hotels")]')) > 0)
        containers = driver.find_elements(By.XPATH, '//div[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "results for hotels")]')
    except TimeoutException:
        print("Timeout: No results containers found. Check the screenshot 'after_search.png' for what the page looks like.")
        driver.quit()
        exit(1)

    print(f"Found {len(containers)} containers with aria-label containing 'Results for hotels':")
    for idx, cont in enumerate(containers):
        print(f"  [{idx}] aria-label: {cont.get_attribute('aria-label')}")

    if not containers:
        print("No suitable results container found.")
        driver.quit()
        exit(1)

    container = containers[0]
    print("Using the first container for scraping.")
    time.sleep(2)  # Small extra wait for more results

    # Improved scrolling: keep scrolling until no new hotels are loaded, or max 50 scrolls
    last_count = 0
    max_scrolls = 50
    for i in range(max_scrolls):
        hotels = container.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        print(f"Scrolled container {i+1} times... Found {len(hotels)} hotels so far.")
        time.sleep(2.5)
        if len(hotels) == last_count:
            print("No new hotels loaded after scrolling. Stopping scroll loop.")
            break
        last_count = len(hotels)

    hotels = container.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
    logging.info(f"Found {len(hotels)} hotels after scrolling.")

    hotel_list = []
    for hotel in hotels:
        try:
            # Find the anchor tag with the hotel link
            link_elem = hotel.find_element(By.CSS_SELECTOR, 'a.hfpxzc')
            link = link_elem.get_attribute('href')
            # Find the hotel name
            try:
                name_elem = hotel.find_element(By.CSS_SELECTOR, 'div.qBF1Pd span, div.qBF1Pd, h3, div[role="heading"]')
                name = name_elem.text.strip()
            except Exception:
                name = ''
            hotel_list.append({'name': name, 'link': link})
            logging.info(f"Extracted hotel: {name} | {link}")
        except Exception as e:
            logging.error(f"Could not extract hotel name/link: {e}")
            continue

    # Write to CSV
    csv_file = f'{area}_hotel_list.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'link'])
        writer.writeheader()
        for row in hotel_list:
            writer.writerow(row)
    print(f"Saved hotel list to {csv_file}")

finally:
    driver.quit()

    