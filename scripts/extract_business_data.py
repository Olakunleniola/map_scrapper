#!/usr/bin/env python3
"""
Hotel Data Extractor - Phase 2
Extracts detailed hotel information from Google Maps links
"""
import sys
import os
import time
import logging
from selenium.webdriver.common.by import By
from typing import Optional

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.selenium_utils import setup_driver, wait_for_element, safe_click
from lib.data_utils import read_csv, save_csv, get_data_file_path, ensure_data_directory, setup_logging

def extract_hotel_details(driver, hotel_link: str, hotel_name: str, area: str) -> dict | None:
    """
    Extract detailed information from a hotel's Google Maps page using robust selectors and minimal warnings.
    Matches the logic and output fields of the old script.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    try:
        driver.get(hotel_link)
        wait = WebDriverWait(driver, 15)
        try:
            detail_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
        except TimeoutException:
            logging.warning(f"Detail pane did not load for {hotel_link}, skipping...")
            return None
        time.sleep(1)
        # Extract name
        try:
            name = detail_pane.find_element(By.CSS_SELECTOR, 'h1.DUwDvf, span.iD2gKb, div.qBF1Pd span, div.qBF1Pd, h3, div[role="heading"]').text.strip()
        except Exception:
            name = hotel_name or ''
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
        # Extract email (scan all text for email pattern)
        try:
            email = ''
            all_text = detail_pane.text
            for word in all_text.split():
                if '@' in word and '.' in word:
                    email = word
                    break
        except Exception:
            email = ''
        # Extract image (first img in detail pane)
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
            'link': hotel_link
        }
    except Exception as e:
        logging.error(f"Error extracting details for {hotel_name}: {e}")
        return None

def main():
    """Main function to run the hotel data extractor"""
    if len(sys.argv) < 2:
        print("Usage: python extract_business_data.py <area>")
        print("Example: python extract_business_data.py 'Ikeja, Lagos'")
        sys.exit(1)
    
    area = sys.argv[1]
    
    # Setup logging
    setup_logging(f'extract_hotel_data_{area.replace(" ", "_").replace(",", "")}.log')
    
    # Read business list - try different possible business types
    possible_business_types = ['hotels', 'restaurants', 'banks', 'pharmacies', 'schools']
    list_filename = None
    
    for business_type in possible_business_types:
        filename = get_data_file_path(business_type, area, 'list')
        if os.path.exists(filename):
            list_filename = filename
            search_type = business_type
            break
    
    # If no business type found, try the old format for backward compatibility
    if not list_filename:
        old_possible_filenames = [
            get_data_file_path('hotel_data', area, 'list', f'{area.replace(" ", "_")}_hotels_list.csv'),
            get_data_file_path('hotel_data', area, 'list', f'{area.replace(" ", "_")}_hotel_list.csv'),
            get_data_file_path('hotel_data', area, 'list', f'{area.replace(" ", "_")}_list.csv')
        ]
        
        for filename in old_possible_filenames:
            if os.path.exists(filename):
                list_filename = filename
                search_type = 'hotels'  # Default for old format
                break
    
    if not list_filename:
        print(f"Business list file not found. Tried business types: {possible_business_types}")
        print("Please run scrape_business_list.py first")
        sys.exit(1)
    
    hotels = read_csv(list_filename)
    
    if not hotels:
        print("No businesses found in the list file")
        sys.exit(1)
    
    # Ensure data directory exists for the detected business type
    ensure_data_directory(search_type, area)
    
    logging.info(f"Starting {search_type} data extraction for {len(hotels)} businesses in {area}")
    
    # Setup WebDriver
    driver = setup_driver()
    detailed_hotels = []
    
    try:
        for i, hotel in enumerate(hotels):
            hotel_name = hotel.get('name', '')
            hotel_link = hotel.get('link', '')
            
            if not hotel_link:
                logging.warning(f"No link found for hotel: {hotel_name}")
                continue
            
            logging.info(f"Processing hotel {i+1}/{len(hotels)}: {hotel_name}")
            
            # Extract detailed information
            hotel_details = extract_hotel_details(driver, hotel_link, hotel_name, area)
            if hotel_details:
                detailed_hotels.append(hotel_details)
                logging.info(f"Extracted: {hotel_details}")
            else:
                logging.warning(f"Could not extract details for {hotel_name} due to loading issue.")
            
            # Small delay between requests
            time.sleep(2)
        
        # Save detailed data
        if detailed_hotels:
            output_filename = get_data_file_path(search_type, area, 'data')
            if save_csv(detailed_hotels, output_filename):
                print(f"Successfully extracted data for {len(detailed_hotels)} {search_type}")
                print(f"Data saved to: {output_filename}")
            else:
                print("Error saving detailed data to CSV")
        else:
            print("No detailed data extracted")
    
    except Exception as e:
        logging.error(f"Error during extraction: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 