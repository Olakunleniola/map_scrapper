#!/usr/bin/env python3
"""
Main Scraping Pipeline Runner
Orchestrates the entire hotel scraping and WhatsApp verification process
"""
import sys
import os
import time
import logging

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data_utils import setup_logging, ensure_data_directory
from lib.network_utils import check_network_connectivity

def run_pipeline(area: str, search_type: str = "hotels", city: str = "Lagos", country: str = "Nigeria", skip_whatsapp: bool = False):
    """
    Run the complete scraping pipeline for a given area
    
    Args:
        area (str): Area to scrape (e.g., 'Ikeja')
        search_type (str): Type of business to search (e.g., 'hotels', 'restaurants')
        city (str): City name (e.g., 'Lagos')
        country (str): Country name (e.g., 'Nigeria')
        skip_whatsapp (bool): Skip WhatsApp verification step
    """
    print(f"🚀 Starting scraping pipeline for: {search_type} near {area}, {city}, {country}")
    print("=" * 50)
    
    # Setup logging
    setup_logging(f'pipeline_{search_type}_{area.replace(" ", "_")}.log')
    
    # Ensure all directories exist
    ensure_data_directory('hotel_data')
    ensure_data_directory('whatsapp_data')
    
    # Step 1: Scrape business list
    print(f"\n📋 Step 1: Scraping {search_type} list...")
    try:
        from scripts.scrape_hotel_list import scrape_hotel_list
        businesses = scrape_hotel_list(search_type, area, city, country)
        if businesses:
            print(f"✅ Found {len(businesses)} {search_type}")
        else:
            print(f"❌ No {search_type} found. Stopping pipeline.")
            return
    except Exception as e:
        print(f"❌ Error in Step 1: {e}")
        return
    
    # Step 2: Extract detailed business data
    print(f"\n🏨 Step 2: Extracting detailed {search_type} data...")
    try:
        from scripts.extract_hotel_data import main as extract_main
        # Temporarily modify sys.argv for the extract script
        original_argv = sys.argv.copy()
        sys.argv = ['extract_hotel_data.py', area]
        extract_main()
        sys.argv = original_argv
        print(f"✅ {search_type.capitalize()} data extraction completed")
    except Exception as e:
        print(f"❌ Error in Step 2: {e}")
        return
    
    # Step 3: Verify WhatsApp numbers (optional)
    if not skip_whatsapp:
        print("\n📱 Step 3: Verifying WhatsApp numbers...")
        
        # Check network connectivity
        if not check_network_connectivity():
            print("❌ Network connectivity check failed. Skipping WhatsApp verification.")
            return
        
        try:
            from scripts.verify_whatsapp_numbers import verify_hotel_whatsapp_numbers
            verified_count, not_verified_count = verify_hotel_whatsapp_numbers(area)
            print(f"✅ WhatsApp verification completed")
            print(f"   - Verified: {verified_count}")
            print(f"   - Not verified: {not_verified_count}")
        except Exception as e:
            print(f"❌ Error in Step 3: {e}")
            return
    
    print("\n🎉 Pipeline completed successfully!")
    print("=" * 50)
    print(f"📁 Data saved in:")
    print(f"   - {search_type.capitalize()} list: data/hotel_data/{area.replace(' ', '_')}_{search_type}_list.csv")
    print(f"   - {search_type.capitalize()} details: data/hotel_data/{area.replace(' ', '_')}_{search_type}_data.csv")
    if not skip_whatsapp:
        print(f"   - WhatsApp verified: data/whatsapp_data/verified_whatsapp_data.csv")
        print(f"   - WhatsApp not verified: data/whatsapp_data/not_verified_whatsapp_data.csv")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python run_scraping_pipeline.py <area> [search_type] [city] [country] [--skip-whatsapp]")
        print("Examples:")
        print("  python run_scraping_pipeline.py 'Ikeja'")
        print("  python run_scraping_pipeline.py 'Ikeja' 'hotels' 'Lagos' 'Nigeria'")
        print("  python run_scraping_pipeline.py 'Victoria Island' 'restaurants' 'Lagos' 'Nigeria' --skip-whatsapp")
        sys.exit(1)
    
    area = sys.argv[1]
    search_type = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "hotels"
    city = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else "Lagos"
    country = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else "Nigeria"
    skip_whatsapp = '--skip-whatsapp' in sys.argv
    
    run_pipeline(area, search_type, city, country, skip_whatsapp)

if __name__ == "__main__":
    main() 