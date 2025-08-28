#!/usr/bin/env python3
"""
Business Data Extractor - Phase 2
Extracts detailed business information from Google Maps links

Usage:
  python scripts/extract_business_data.py <area> [business_type]

Examples:
  python scripts/extract_business_data.py "Ikeja"                # defaults to hotels
  python scripts/extract_business_data.py "Ikeja" restaurants
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
from lib.data_utils import clean_phone_number, format_message, read_csv, save_csv, get_data_file_path, ensure_data_directory, setup_logging

def extract_details(driver, link: str, business_name: str, area: str, business_type:str, state: str, country: str ) -> dict | None:
    """
    Extract detailed information from a hotel's Google Maps page using robust selectors and minimal warnings.
    Matches the logic and output fields of the old script.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 15)
        try:
            detail_pane = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
        except TimeoutException:
            logging.warning(f"Detail pane did not load for {link}, skipping...")
            return None
        time.sleep(2)
        # Extract address
        try:
            address = detail_pane.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"] div.Io6YTe, div.Io6YTe').text.strip()
            print(address)
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
            'name': business_name,
            'address': address,
            'phone': clean_phone_number(phone),
            'message': format_message(business_name), 
            'email': email,
            'website': website,
            'image_url': img_url,
            'link': link,
            'business_type': business_type,
            'location': area,
            'state': state,
            'country': country
        }
    except Exception as e:
        logging.error(f"Error extracting details for {business_name}: {e}")
        return None

def main():
    """Main function to run the business data extractor"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_business_data.py <area> [business_type]")
        print("Examples:")
        print("  python scripts/extract_business_data.py 'Ikeja'")
        print("  python scripts/extract_business_data.py 'Ikeja' restaurants")
        sys.exit(1)
    
    area = sys.argv[1]
    # Optional business type (default: hotels)
    cli_business_type = sys.argv[2].lower() if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    #Optional State (default: Lagos)
    state = sys.argv[3].lower() if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else "Lagos"
    #Optional Country (default: Country)
    country = sys.argv[4].lower() if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else "Nigeria"


    # Setup logging
    log_suffix_area = area.replace(" ", "_").replace(",", "")
    log_prefix_bt = (cli_business_type or 'hotels').replace(" ", "_")
    setup_logging(f'extract_{log_prefix_bt}_data_{log_suffix_area}.log')
    
    # Determine list file to read
    list_filename = None
    search_type = cli_business_type or 'hotels'
    
    if cli_business_type:
        # Use the explicitly requested business type
        candidate = get_data_file_path(cli_business_type, area, 'list')
        if os.path.exists(candidate):
            list_filename = candidate
        else:
            print(f"No list file found for requested business type '{cli_business_type}' in area '{area}'.")
            print("Please run: python scripts/scrape_business_list.py '<area>' '<business_type>'")
            sys.exit(1)
    else:
        # Auto-detect existing list file among known business types
        possible_business_types = ['hotels', 'restaurants', 'banks', 'pharmacies', 'schools']
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
        print("Business list file not found.")
        print("Please run scrape_business_list.py first, e.g.:")
        print("  python scripts/scrape_business_list.py 'Ikeja' 'hotels'")
        sys.exit(1)
    
    business_data = read_csv(list_filename)
    
    if not business_data:
        print("No businesses found in the list file")
        sys.exit(1)
    
    # Ensure data directory exists for the detected/requested business type
    ensure_data_directory(search_type, area)
    
    logging.info(f"Starting {search_type} data extraction for {len(business_data)} businesses in {area}")
    
    # Setup WebDriver
    driver = setup_driver()
    detailed_business_data = []
    
    try:
        for i, data in enumerate(business_data):              
            business_name = data.get('name', '')
            link = data.get('link', '')
            
            if not link:
                logging.warning(f"No link found for {search_type[:-1] if search_type.endswith('s') else search_type}: {business_name}")
                continue
            
            logging.info(f"Processing {search_type[:-1] if search_type.endswith('s') else search_type} {i+1}/{len(business_data)}: {business_name}")
            
            # Extract detailed information
            business_details = extract_details(driver, link, business_name, area, cli_business_type or 'hotel', state, country)
            if business_details:
                detailed_business_data.append(business_details)
                logging.info(f"Extracted: {business_details.get('name', "")}")
            else:
                logging.warning(f"Could not extract details for {business_name} due to loading issue.")
            
            # Small delay between requests
            time.sleep(2)
        
        # Save detailed data
        if detailed_business_data:
            output_filename = get_data_file_path(search_type, area, 'data', excel=True)
            if save_csv(detailed_business_data, output_filename, excel=True):
                print(f"Successfully extracted data for {len(detailed_business_data)} {search_type}")
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