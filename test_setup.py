#!/usr/bin/env python3
"""
Test script to verify the new project structure works correctly
"""
import sys
import os

# Add parent directory to path to import lib modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing imports...")
    
    try:
        from lib.selenium_utils import setup_driver, wait_for_element
        print("✅ lib.selenium_utils imported successfully")
    except Exception as e:
        print(f"❌ Error importing lib.selenium_utils: {e}")
        return False
    
    try:
        from lib.data_utils import save_csv, read_csv, setup_logging
        print("✅ lib.data_utils imported successfully")
    except Exception as e:
        print(f"❌ Error importing lib.data_utils: {e}")
        return False
    
    try:
        from lib.network_utils import check_network_connectivity
        print("✅ lib.network_utils imported successfully")
    except Exception as e:
        print(f"❌ Error importing lib.network_utils: {e}")
        return False
    
    return True

def test_directories():
    """Test that all required directories exist"""
    print("\nTesting directory structure...")
    
    required_dirs = ['scripts', 'lib', 'data', 'data/hotel_data', 'data/whatsapp_data', 'logs']
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            return False
    
    return True

def test_files():
    """Test that all required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        'scripts/scrape_business_list.py',
        'scripts/extract_business_data.py',
        'scripts/verify_whatsapp_numbers.py',
        'scripts/run_scraping_pipeline.py',
        'lib/__init__.py',
        'lib/selenium_utils.py',
        'lib/data_utils.py',
        'lib/network_utils.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Map Scraper Project Structure")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Directory Tests", test_directories),
        ("File Tests", test_files)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Project structure is ready.")
        print("\nYou can now run:")
        print("  python scripts/run_scraping_pipeline.py 'Ikeja, Lagos'")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main() 