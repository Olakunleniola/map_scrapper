#!/usr/bin/env python3
"""
WhatsApp Number Verifier
Verifies phone numbers from hotel data against WhatsApp
"""
import sys
import os
import logging

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.selenium_utils import setup_driver
from lib.data_utils import (
    read_csv, append_to_csv, get_data_file_path, ensure_data_directory, 
    setup_logging, clean_phone_number, load_existing_verified_numbers
)
from lib.network_utils import check_network_connectivity, check_whatsapp_number

def verify_hotel_whatsapp_numbers(area: str) -> tuple:
    """
    Verify WhatsApp numbers for hotels in a given area
    
    Args:
        area (str): Area to process (e.g., 'Ikeja, Lagos')
    
    Returns:
        tuple: (verified_count, not_verified_count)
    """
    # Setup file paths - try different possible file names
    possible_filenames = [
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_hotels_data.csv'),
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_hotel_data.csv'),
        get_data_file_path('hotel_data', f'{area.replace(" ", "_")}_data.csv')
    ]
    
    input_filename = None
    for filename in possible_filenames:
        if os.path.exists(filename):
            input_filename = filename
            break
    verified_filename = get_data_file_path('whatsapp_data', 'verified_whatsapp_data.csv')
    not_verified_filename = get_data_file_path('whatsapp_data', 'not_verified_whatsapp_data.csv')
    
    # Check if input file exists
    if not input_filename or not os.path.exists(input_filename):
        logging.error(f"Input file not found. Tried:")
        for filename in possible_filenames:
            logging.error(f"  - {filename}")
        return 0, 0
    
    # Load existing verified numbers to avoid duplicates
    existing_verified = load_existing_verified_numbers(verified_filename, not_verified_filename)
    logging.info(f"Found {len(existing_verified)} already verified phone numbers. Skipping these...")
    
    # Read business data
    hotels = read_csv(input_filename)
    if not hotels:
        logging.error("No hotel data found")
        return 0, 0
    
    # Setup WebDriver
    driver = setup_driver()
    verified_count = 0
    not_verified_count = 0
    
    try:
        for i, hotel in enumerate(hotels):
            raw_phone = hotel.get('phone', '').strip()
            if not raw_phone:
                logging.warning(f"No phone number for hotel: {hotel.get('name', 'Unknown')}")
                continue
            
            # Clean phone number
            phone = clean_phone_number(raw_phone)
            if not phone:
                logging.warning(f"Invalid phone number format: {raw_phone}")
                continue
            
            # Skip if already verified
            if phone in existing_verified:
                logging.info(f"Skipping {phone} - already verified")
                continue
            
            logging.info(f"Checking {phone} ({hotel.get('name', 'Unknown')}) [{i+1}/{len(hotels)}]")
            
            # Check WhatsApp
            is_whatsapp = check_whatsapp_number(driver, phone)
            
            # Prepare data for CSV
            data = {
                'area': area,
                'name': hotel.get('name', ''),
                'address': hotel.get('address', ''),
                'phone': phone,
                'website': hotel.get('website', ''),
                'email': hotel.get('email', ''),
                'image': hotel.get('image', '')
            }
            
            # Save to appropriate CSV
            fieldnames = ['area', 'name', 'address', 'phone', 'website', 'email', 'image']
            
            if is_whatsapp:
                if append_to_csv(verified_filename, data, fieldnames):
                    verified_count += 1
                    logging.info(f"✓ {phone} is on WhatsApp")
            else:
                if append_to_csv(not_verified_filename, data, fieldnames):
                    not_verified_count += 1
                    logging.info(f"✗ {phone} is not on WhatsApp")
    
    except Exception as e:
        logging.error(f"Error during verification: {e}")
    finally:
        driver.quit()
    
    return verified_count, not_verified_count

def main():
    """Main function to run the WhatsApp verification"""
    if len(sys.argv) < 2:
        print("Usage: python verify_whatsapp_numbers.py <area>")
        print("Example: python verify_whatsapp_numbers.py 'Ikeja, Lagos'")
        sys.exit(1)
    
    area = sys.argv[1]
    
    # Setup logging
    setup_logging(f'verify_whatsapp_{area.replace(" ", "_").replace(",", "")}.log')
    
    # Ensure data directories exist
    ensure_data_directory('whatsapp_data')
    
    logging.info(f"Starting WhatsApp verification for area: {area}")
    
    # Check network connectivity
    if not check_network_connectivity():
        print("Network connectivity to wa.me failed. Please check your internet connection and DNS settings.")
        sys.exit(1)
    
    # Verify WhatsApp numbers
    verified_count, not_verified_count = verify_hotel_whatsapp_numbers(area)
    
    print(f"\nVerification complete!")
    print(f"New verified numbers: {verified_count}")
    print(f"New non-verified numbers: {not_verified_count}")
    print(f"Data appended to data/whatsapp_data/")

if __name__ == "__main__":
    main() 