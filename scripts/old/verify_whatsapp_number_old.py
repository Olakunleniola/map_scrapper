import csv
import os
import sys
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import socket

logging.basicConfig(filename='verify_whatsapp_number.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def check_network():
    try:
        host = 'wa.me'
        socket.gethostbyname(host)
        s = socket.create_connection((host, 80), 5)
        s.close()
        return True
    except Exception as e:
        print(f"Network connectivity check failed: {e}")
        return False

def check_whatsapp(driver, phone_number):
    url = f"https://wa.me/{phone_number}"
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        if "Phone number shared via url is invalid" in page_source or "Invalid phone number" in page_source:
            return False
        return True
    except Exception as e:
        logging.error(f"Error checking WhatsApp for {phone_number}: {e}")
        return False

def load_existing_verified_numbers():
    """Load phone numbers that have already been verified from existing CSV files"""
    verified_numbers = set()
    
    # Check verified file
    if os.path.exists('verified_whatsapp_data.csv'):
        with open('verified_whatsapp_data.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('phone'):
                    verified_numbers.add(row['phone'].replace(' ', ''))
    
    # Check not verified file
    if os.path.exists('not_verified_whatsapp_data.csv'):
        with open('not_verified_whatsapp_data.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('phone'):
                    verified_numbers.add(row['phone'].replace(' ', ''))
    
    return verified_numbers

def append_to_csv(filename, data, fieldnames):
    """Append data to CSV file, creating it with headers if it doesn't exist"""
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def main():
    area = sys.argv[1] if len(sys.argv) > 1 else 'Lagos'
    input_file = f'{area}_hotel_data.csv'
    verified_file = 'verified_whatsapp_data.csv'
    not_verified_file = 'not_verified_whatsapp_data.csv'
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
        return
    
    if not check_network():
        print("Network connectivity to wa.me failed. Please check your internet connection and DNS settings.")
        return
    
    # Load already verified numbers to avoid duplicates
    existing_verified = load_existing_verified_numbers()
    print(f"Found {len(existing_verified)} already verified phone numbers. Skipping these...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        verified_data = []
        not_verified_data = []
        
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                raw_phone = row.get('phone', '').strip()
                if not raw_phone:
                    continue
                
                # Clean phone number
                phone = re.sub(r'\D', '', raw_phone)
                if not phone.startswith('234'):
                    phone = '234' + phone
                
                # Skip if already verified
                if phone in existing_verified:
                    print(f"Skipping {phone} - already verified")
                    continue
                
                print(f"Checking {phone}...")
                is_whatsapp = check_whatsapp(driver, phone)
                
                data = {
                    'area': area,
                    'name': row.get('name', ''),
                    'address': row.get('address', ''),
                    'phone': phone,
                    'website': row.get('website', ''),
                    'email': row.get('email', ''),
                    'image': row.get('image', '')
                }
                
                if is_whatsapp:
                    verified_data.append(data)
                    print(f"✓ {phone} is on WhatsApp")
                else:
                    not_verified_data.append(data)
                    print(f"✗ {phone} is not on WhatsApp")
        
        # Append data to CSV files
        fieldnames = ['area', 'name', 'address', 'phone', 'website', 'email', 'image']
        
        for data in verified_data:
            append_to_csv(verified_file, data, fieldnames)
        
        for data in not_verified_data:
            append_to_csv(not_verified_file, data, fieldnames)
        
        print(f"\nVerification complete!")
        print(f"New verified numbers: {len(verified_data)}")
        print(f"New non-verified numbers: {len(not_verified_data)}")
        print(f"Data appended to {verified_file} and {not_verified_file}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 