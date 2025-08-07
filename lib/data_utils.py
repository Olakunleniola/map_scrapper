"""
Data utility functions for handling CSV files, phone numbers, and data processing
"""
import csv
import os
import re
import logging
from typing import List, Dict, Set, Optional
import pandas as pd

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
        cleaned = '+234' + cleaned[1:]
    elif cleaned.startswith('+234'):
        cleaned = cleaned # leave it like that
    elif cleaned.startswith('234'):
        cleaned = '+' + cleaned
    else:
        cleaned = '+234' + cleaned
    return cleaned

def format_message(name: str) -> str:
  
    lines = [
        f"Dear *{name} Team*,",
        "",
        "I’m Engr. Olakunle Adio, founder of Our Work Laundry Solution, Lagos’ trusted partner in industrial laundry excellence. "
        "We’re passionate about keeping your laundry operations seamless, efficient, and downtime-free.",
        "",
        "🚀 *Why Choose Us?*",
        "• We specialize in expert repair, servicing, and setup of industrial laundry equipment—dryers, washers, presses, and ironing tables.",
        "• Our mission? To ensure your hotel delivers impeccable linens and guest experiences, every time.",
        "",
        "🎯 *What We Offer:*",
        "✅ *Rapid Response:* Swift solutions to minimize disruptions.",
        "✅ *Reliable Repairs:* Cost-effective fixes that last.",
        "✅ *Expert Setup & Maintenance:* Tailored services for peak performance.",
        "",
        "🏨 With a proven track record supporting hotels and laundry facilities across Lagos, we’re ready to bring our expertise to you.",
        "",
        "✨ *Let’s Get Started!*",
        "📞 *Call/WhatsApp:* 09124075977",
        "📍 *Proudly based in Lagos—available when you need us!*",
        "🌐 *Learn more:* https://ourworklaundrysolutions.vercel.app",
        "",
        "Give us a chance to earn your trust with a first trial. Let’s keep your operations spotless!",
        "",
        "Warm regards,",
        "Engr. Olakunle Adio",
        "Our Work Laundry Solution",
        "",
        "P.S. We’re also available on WhatsApp at 09124075977"
    ]

    message = "\r\n".join(lines)
    # Escape double quotes for CSV output if needed
    return message.replace('"', '""')

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

def save_csv(data: List[Dict], filename: str, fieldnames: Optional[List[str]] = None, excel: Optional[bool] = False) -> bool:
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

        if excel:
            df = pd.DataFrame(data, columns=fieldnames)
            df.to_excel(filename, index=False)
            logging.info(f"Saved {len(data)} records to {filename}")
            return True
        
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

def get_data_file_path(business_type: str, area: str, file_type: str, filename: str | None = None, excel: Optional[bool] = False) -> str:
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
        if excel:
            filename = f"{clean_area}_{clean_business_type}_{file_type}.xlsx"
        else:
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