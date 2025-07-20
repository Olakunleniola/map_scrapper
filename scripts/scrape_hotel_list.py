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
        
        # Wait for results to load
        results_container = wait_for_element(driver, By.CSS_SELECTOR, '[role="feed"]', timeout=15)
        if not results_container:
            logging.error("Results container not found")
            return hotels
        
        # Scroll to load more results
        logging.info("Scrolling to load more results...")
        scroll_count = scroll_container(driver, '[role="feed"]', scroll_pause=3)
        logging.info(f"Scrolled {scroll_count} times")
        
        # Extract hotel data
        hotel_elements = driver.find_elements(By.CSS_SELECTOR, '[role="article"]')
        logging.info(f"Found {len(hotel_elements)} hotel elements")
        
        for i, element in enumerate(hotel_elements):
            try:
                # Extract hotel name
                name_element = element.find_element(By.CSS_SELECTOR, 'h3, [role="heading"]')
                name = name_element.text.strip()
                
                # Extract hotel link
                link_element = element.find_element(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
                link = link_element.get_attribute('href')
                
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
                
            except Exception as e:
                logging.warning(f"Error extracting hotel {i+1}: {e}")
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
    ensure_data_directory('hotel_data')
    
    logging.info(f"Starting {search_type} list scraping for {area}, {city}, {country}")
    
    # Scrape business list
    businesses = scrape_hotel_list(search_type, area, city, country)
    
    if businesses:
        # Save to CSV
        filename = get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_{search_type}_list.csv')
        if save_csv(businesses, filename):
            print(f"Successfully scraped {len(businesses)} {search_type}")
            print(f"Data saved to: {filename}")
        else:
            print("Error saving data to CSV")
    else:
        print(f"No {search_type} found or error occurred during scraping")

if __name__ == "__main__":
    main() 