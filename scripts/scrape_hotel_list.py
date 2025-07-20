#!/usr/bin/env python3
"""
Hotel List Scraper - Phase 1
Scrapes hotel names and links from Google Maps for a given area
"""
import sys
import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.selenium_utils import setup_driver, wait_for_element, safe_click, safe_send_keys, scroll_container, handle_cookie_consent
from lib.data_utils import save_csv, get_data_file_path, ensure_data_directory, setup_logging

def scrape_hotel_list(search_type: str = "hotels", area: str = "Lagos", city: str = "Lagos", country: str = "Nigeria") -> list:
    """
    Scrape business list from Google Maps for a given area
    
    Args:
        search_type (str): Type of business to search (e.g., 'hotels', 'restaurants')
        area (str): Specific area to search in (e.g., 'Ikeja')
        city (str): City name (e.g., 'Lagos')
        country (str): Country name (e.g., 'Nigeria')
    
    Returns:
        list: List of dictionaries containing business data
    """
    driver = setup_driver()
    hotels = []
    
    try:
        # Navigate to Google Maps
        driver.get("https://www.google.com/maps")
        logging.info(f"Opened Google Maps for search: {search_type} near {area}, {city}, {country}")
        
        # Handle cookie consent
        handle_cookie_consent(driver)
        
        # Find and fill search box
        search_query = f"{search_type} near {area}, {city}, {country}"
        logging.info(f"Searching for: {search_query}")
        
        # Wait for search box and enter query
        search_box = wait_for_element(driver, By.ID, "searchboxinput", timeout=15)
        if not search_box:
            logging.error("Search box not found")
            return hotels
        
        safe_send_keys(driver, By.ID, "searchboxinput", search_query)
        time.sleep(2)
        
        # Press Enter to search
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)
        
        # Wait for results to load - try multiple container selectors
        results_container = None
        container_selectors = [
            '[role="feed"]',
            '//div[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "results for hotels")]',
            '//div[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "results for")]'
        ]
        
        for selector in container_selectors:
            try:
                if selector.startswith('//'):
                    # XPath selector
                    results_container = wait_for_element(driver, By.XPATH, selector, timeout=10)
                else:
                    # CSS selector
                    results_container = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=10)
                if results_container:
                    logging.info(f"Found results container using selector: {selector}")
                    break
            except:
                continue
        
        if not results_container:
            logging.error("Results container not found with any selector")
            return hotels
        
        # Scroll to load more results
        logging.info("Scrolling to load more results...")
        last_count = 0
        max_scrolls = 50
        scroll_count = 0
        
        for i in range(max_scrolls):
            hotel_elements = results_container.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_container)
            logging.info(f"Scroll {i+1}: Found {len(hotel_elements)} {search_type} so far")
            time.sleep(2.5)
            if len(hotel_elements) == last_count:
                logging.info("No new results loaded after scrolling. Stopping scroll loop.")
                break
            last_count = len(hotel_elements)
            scroll_count = i + 1
        
        logging.info(f"Scrolled {scroll_count} times")
        
        # Extract hotel data using the working selector from main_old.py
        hotel_elements = results_container.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
        logging.info(f"Found {len(hotel_elements)} {search_type} elements")
        
        logging.info(f"Found {len(hotel_elements)} hotel elements")
        
        for i, element in enumerate(hotel_elements):
            try:
                # Find the anchor tag with the hotel link (from main_old.py)
                link_elem = element.find_element(By.CSS_SELECTOR, 'a.hfpxzc')
                link = link_elem.get_attribute('href')
                
                # Find the hotel name (from main_old.py)
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, 'div.qBF1Pd span, div.qBF1Pd, h3, div[role="heading"]')
                    name = name_elem.text.strip()
                except Exception:
                    name = ''
                
                if name and link:
                    hotel_data = {
                        'name': name,
                        'link': link,
                        'search_type': search_type,
                        'area': area,
                        'city': city,
                        'country': country
                    }
                    hotels.append(hotel_data)
                    logging.info(f"Extracted {search_type} {i+1}: {name}")
                else:
                    logging.warning(f"Could not extract name or link for element {i+1}")
                
            except Exception as e:
                logging.warning(f"Error extracting {search_type} {i+1}: {e}")
                continue
        
        logging.info(f"Successfully extracted {len(hotels)} {search_type}")
        
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    return hotels

def main():
    """Main function to run the business list scraper"""
    if len(sys.argv) < 2:
        print("Usage: python scrape_hotel_list.py <area> [search_type] [city] [country]")
        print("Examples:")
        print("  python scrape_hotel_list.py 'Ikeja'")
        print("  python scrape_hotel_list.py 'Ikeja' 'hotels' 'Lagos' 'Nigeria'")
        print("  python scrape_hotel_list.py 'Victoria Island' 'restaurants' 'Lagos' 'Nigeria'")
        sys.exit(1)
    
    area = sys.argv[1]
    search_type = sys.argv[2] if len(sys.argv) > 2 else "hotels"
    city = sys.argv[3] if len(sys.argv) > 3 else "Lagos"
    country = sys.argv[4] if len(sys.argv) > 4 else "Nigeria"
    
    # Setup logging
    setup_logging(f'scrape_{search_type}_list_{area.replace(" ", "_")}.log')
    
    # Ensure data directory exists
    ensure_data_directory(search_type, area)
    
    logging.info(f"Starting {search_type} list scraping for {area}, {city}, {country}")
    
    # Scrape business list
    businesses = scrape_hotel_list(search_type, area, city, country)
    
    if businesses:
        # Save to CSV
        filename = get_data_file_path(search_type, area, 'list')
        if save_csv(businesses, filename):
            print(f"Successfully scraped {len(businesses)} {search_type}")
            print(f"Data saved to: {filename}")
        else:
            print("Error saving data to CSV")
    else:
        print(f"No {search_type} found or error occurred during scraping")

if __name__ == "__main__":
    main() 