"""
Data utility functions for handling CSV files, phone numbers, and data processing
"""
import csv
import os
import re
import logging
from typing import List, Dict, Set, Optional

def clean_phone_number(phone: str) -> str:
    """
    Clean and standardize phone number format
    
    Args:
        phone (str): Raw phone number string
    
    Returns:
        str: Cleaned phone number in 234XXXXXXXXX format
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Handle Nigerian numbers
    if cleaned.startswith('0'):
        cleaned = '234' + cleaned[1:]
    elif cleaned.startswith('+234'):
        cleaned = cleaned[1:]  # Remove the +
    elif not cleaned.startswith('234'):
        cleaned = '234' + cleaned
    
    return cleaned

def load_existing_verified_numbers(verified_file: str, not_verified_file: str) -> Set[str]:
    """
    Load phone numbers that have already been verified from existing CSV files
    
    Args:
        verified_file (str): Path to verified WhatsApp data CSV
        not_verified_file (str): Path to not verified WhatsApp data CSV
    
    Returns:
        Set[str]: Set of already verified phone numbers
    """
    verified_numbers = set()
    
    for file_path in [verified_file, not_verified_file]:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('phone'):
                            clean_phone = clean_phone_number(row['phone'])
                            if clean_phone:
                                verified_numbers.add(clean_phone)
            except Exception as e:
                logging.error(f"Error reading {file_path}: {e}")
    
    return verified_numbers

def append_to_csv(filename: str, data: Dict, fieldnames: List[str]) -> bool:
    """
    Append data to CSV file, creating it with headers if it doesn't exist
    
    Args:
        filename (str): Path to CSV file
        data (Dict): Data to append
        fieldnames (List[str]): Column names for CSV
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
        
        return True
    except Exception as e:
        logging.error(f"Error appending to {filename}: {e}")
        return False

def save_csv(data: List[Dict], filename: str, fieldnames: Optional[List[str]] = None) -> bool:
    """
    Save data to CSV file
    
    Args:
        data (List[Dict]): List of dictionaries to save
        filename (str): Path to CSV file
        fieldnames (List[str], optional): Column names. If None, uses keys from first dict
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not data:
        logging.warning(f"No data to save to {filename}")
        return False
    
    try:
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logging.info(f"Saved {len(data)} records to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving to {filename}: {e}")
        return False

def read_csv(filename: str) -> List[Dict]:
    """
    Read data from CSV file
    
    Args:
        filename (str): Path to CSV file
    
    Returns:
        List[Dict]: List of dictionaries from CSV
    """
    if not os.path.exists(filename):
        logging.warning(f"File {filename} does not exist")
        return []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
        return []

def get_data_file_path(business_type: str, area: str, file_type: str, filename: str | None = None) -> str:
    """
    Get the full path for a data file based on business type and area
    
    Args:
        business_type (str): Type of business ('hotels', 'restaurants', 'banks', etc.)
        area (str): Area name (e.g., 'ikeja', 'alimosho')
        file_type (str): Type of file ('list', 'data')
        filename (str, optional): Custom filename. If None, generates: {area}_{business_type}_{file_type}.csv
    
    Returns:
        str: Full path to the data file
    """
    # Clean area name for folder/file naming
    clean_area = area.replace(" ", "_").replace(",", "").lower()
    clean_business_type = business_type.lower()
    
    # Generate filename if not provided
    if filename is None:
        filename = f"{clean_area}_{clean_business_type}_{file_type}.csv"
    
    # Create path: data/{business_type}/{area}/{filename}
    return os.path.join('data', clean_business_type, clean_area, filename)

def ensure_data_directory(business_type: str, area: str | None = None) -> bool:
    """
    Ensure data directory exists for business type and area
    
    Args:
        business_type (str): Type of business ('hotels', 'restaurants', 'banks', etc.)
        area (str, optional): Area name. If provided, creates area subdirectory
    
    Returns:
        bool: True if directory exists or was created successfully
    """
    clean_business_type = business_type.lower()
    
    if area:
        clean_area = area.replace(" ", "_").replace(",", "").lower()
        dir_path = os.path.join('data', clean_business_type, clean_area)
    else:
        dir_path = os.path.join('data', clean_business_type)
    
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {dir_path}: {e}")
        return False

def get_log_file_path(log_name: str) -> str:
    """
    Get the full path for a log file
    
    Args:
        log_name (str): Name of the log file
    
    Returns:
        str: Full path to the log file
    """
    return os.path.join('logs', log_name)

def setup_logging(log_name: str, level=logging.INFO) -> None:
    """
    Setup logging configuration
    
    Args:
        log_name (str): Name of the log file
        level: Logging level
    """
    log_file = get_log_file_path(log_name)
    
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        filename=log_file,
        level=level,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler) 