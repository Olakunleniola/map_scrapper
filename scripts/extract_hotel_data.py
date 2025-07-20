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

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.selenium_utils import setup_driver, wait_for_element, safe_click
from lib.data_utils import read_csv, save_csv, get_data_file_path, ensure_data_directory, setup_logging

def extract_hotel_details(driver, hotel_link: str, hotel_name: str, area: str) -> dict:
    """
    Extract detailed information from a hotel's Google Maps page
    
    Args:
        driver: WebDriver instance
        hotel_link (str): Google Maps link for the hotel
        hotel_name (str): Name of the hotel
        area (str): Area where hotel is located
    
    Returns:
        dict: Dictionary containing hotel details
    """
    try:
        driver.get(hotel_link)
        time.sleep(3)
        
        # Initialize hotel data
        hotel_data = {
            'name': hotel_name,
            'area': area,
            'link': hotel_link,
            'address': '',
            'phone': '',
            'website': '',
            'email': '',
            'image': ''
        }
        
        # Extract address
        try:
            address_element = wait_for_element(driver, By.CSS_SELECTOR, 'button[data-item-id*="address"]', timeout=5)
            if address_element:
                hotel_data['address'] = address_element.text.strip()
        except:
            pass
        
        # Extract phone number
        try:
            phone_element = wait_for_element(driver, By.CSS_SELECTOR, 'button[data-item-id*="phone"]', timeout=5)
            if phone_element:
                hotel_data['phone'] = phone_element.text.strip()
        except:
            pass
        
        # Extract website
        try:
            website_element = wait_for_element(driver, By.CSS_SELECTOR, 'a[data-item-id*="authority"]', timeout=5)
            if website_element:
                website_url = website_element.get_attribute('href')
                if website_url:
                    hotel_data['website'] = website_url
        except:
            pass
        
        # Extract email (if available)
        try:
            # Look for email in various formats
            email_selectors = [
                'a[href^="mailto:"]',
                'button[data-item-id*="email"]',
                '[data-item-id*="email"]'
            ]
            
            for selector in email_selectors:
                email_element = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=3)
                if email_element:
                    email_text = email_element.text.strip() or (email_element.get_attribute('href') or '').replace('mailto:', '')
                    if '@' in email_text:
                        hotel_data['email'] = email_text
                        break
        except:
            pass
        
        # Extract image (if available)
        try:
            image_element = wait_for_element(driver, By.CSS_SELECTOR, 'img[alt*="photo"], img[alt*="image"]', timeout=5)
            if image_element:
                image_url = image_element.get_attribute('src')
                if image_url:
                    hotel_data['image'] = image_url
        except:
            pass
        
        logging.info(f"Extracted details for: {hotel_name}")
        return hotel_data
        
    except Exception as e:
        logging.error(f"Error extracting details for {hotel_name}: {e}")
        return hotel_data

def main():
    """Main function to run the hotel data extractor"""
    if len(sys.argv) < 2:
        print("Usage: python extract_hotel_data.py <area>")
        print("Example: python extract_hotel_data.py 'Ikeja, Lagos'")
        sys.exit(1)
    
    area = sys.argv[1]
    
    # Setup logging
    setup_logging(f'extract_hotel_data_{area.replace(" ", "_").replace(",", "")}.log')
    
    # Ensure data directory exists
    ensure_data_directory('hotel_data')
    
    # Read business list - try different possible file names
    possible_filenames = [
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_hotels_list.csv'),
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_hotel_list.csv'),
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_list.csv')
    ]
    
    list_filename = None
    for filename in possible_filenames:
        if os.path.exists(filename):
            list_filename = filename
            break
    
    if not list_filename:
        print(f"Business list file not found. Tried:")
        for filename in possible_filenames:
            print(f"  - {filename}")
        print("Please run scrape_hotel_list.py first")
        sys.exit(1)
    
    hotels = read_csv(list_filename)
    
    if not hotels:
        print("No businesses found in the list file")
        sys.exit(1)
    
    # Determine search type from the data
    search_type = hotels[0].get('search_type', 'hotels') if hotels else 'hotels'
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
            detailed_hotels.append(hotel_details)
            
            # Small delay between requests
            time.sleep(2)
        
        # Save detailed data
        if detailed_hotels:
            output_filename = get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_{search_type}_data.csv')
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