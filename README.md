# Map Scraper - Business Data Collection Tool

A comprehensive Python tool for scraping business data from Google Maps and verifying WhatsApp numbers. The project is organized in a modular structure for better maintainability and scalability. Supports flexible search queries for any business type and location.

## 🏗️ Project Structure

```
Map Scapper/
├── scripts/                    # Main execution scripts
│   ├── scrape_hotel_list.py    # Phase 1: Extract business names and links
│   ├── extract_hotel_data.py   # Phase 2: Extract detailed business information
│   ├── verify_whatsapp_numbers.py  # Phase 3: Verify WhatsApp numbers
│   └── run_scraping_pipeline.py    # Complete pipeline runner
├── lib/                        # Utility libraries
│   ├── selenium_utils.py       # Selenium WebDriver utilities
│   ├── data_utils.py           # Data handling and CSV operations
│   └── network_utils.py        # Network connectivity and WhatsApp verification
├── data/                       # Data storage
│   ├── hotels/                 # Hotel data (default business type)
│   │   ├── ikeja/             # Area-specific folders
│   │   │   ├── ikeja_hotels_list.csv
│   │   │   └── ikeja_hotels_data.csv
│   │   └── alimosho/
│   │       ├── alimosho_hotels_list.csv
│   │       └── alimosho_hotels_data.csv
│   ├── restaurants/            # Restaurant data
│   │   └── ikeja/
│   │       ├── ikeja_restaurants_list.csv
│   │       └── ikeja_restaurants_data.csv
│   └── whatsapp_data/          # WhatsApp verification results
│       └── ikeja/
│           ├── verified_whatsapp_data.csv
│           └── not_verified_whatsapp_data.csv
├── logs/                       # Log files for debugging
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv ourwork_env

# Activate virtual environment
# Windows:
ourwork_env\Scripts\activate
# Linux/Mac:
source ourwork_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Complete Pipeline

```bash
# Run all steps for an area (default: hotels near area, Lagos, Nigeria)
python scripts/run_scraping_pipeline.py "Ikeja"

# Custom business type
python scripts/run_scraping_pipeline.py "Ikeja" "restaurants"

# Full custom search
python scripts/run_scraping_pipeline.py "Victoria Island" "hotels" "Lagos" "Nigeria"

# Skip WhatsApp verification
python scripts/run_scraping_pipeline.py "Ikeja" "hotels" "Lagos" "Nigeria" --skip-whatsapp
```

### 3. Run Individual Steps

```bash
# Step 1: Scrape business list (default: hotels)
python scripts/scrape_hotel_list.py "Ikeja"

# Step 1: Custom business type
python scripts/scrape_hotel_list.py "Ikeja" "restaurants"

# Step 1: Full custom search
python scripts/scrape_hotel_list.py "Victoria Island" "hotels" "Lagos" "Nigeria"

# Step 2: Extract detailed data
python scripts/extract_hotel_data.py "Ikeja"

# Step 3: Verify WhatsApp numbers
python scripts/verify_whatsapp_numbers.py "Ikeja"
```

## 📊 Data Output

### Business List (Phase 1)

- **File**: `data/{business_type}/{area}/{area}_{business_type}_list.csv`
- **Columns**: `name`, `link`, `search_type`, `area`, `city`, `country`

### Business Details (Phase 2)

- **File**: `data/{business_type}/{area}/{area}_{business_type}_data.csv`
- **Columns**: `name`, `area`, `link`, `address`, `phone`, `website`, `email`, `image`

### WhatsApp Verification (Phase 3)

- **Verified**: `data/whatsapp_data/verified_whatsapp_data.csv`
- **Not Verified**: `data/whatsapp_data/not_verified_whatsapp_data.csv`
- **Columns**: `name`, `address`, `phone`, `email`, `website`, `image_url`, `link`, `area` (area is always the last column)
- **Format Example:**

  ```csv
  Masbat De kings Hotel,"km, 1 Itokin Road, Ikorodu, Lagos",08033031048,,,https://lh3.googleusercontent.com/p/AF1QipOULCNvvLUUgLFzU_Jn8MWpy3LKfaiZ17D0whuS=w408-h271-k-no,https://www.google.com/maps/place/Masbat+De+kings+Hotel/... ,ikorodu
  ```

- The same format is used for both verified and not verified WhatsApp data files.
- All results are appended to these files; no area subfolders are created for WhatsApp data.

## 🔧 Features

### ✅ Modular Architecture

- Separated concerns with utility libraries
- Reusable functions across scripts
- Easy to maintain and extend

### ✅ Robust Error Handling

- Network connectivity checks
- Comprehensive logging
- Graceful failure recovery

### ✅ Data Management

- Automatic directory creation
- CSV file management
- Duplicate prevention in WhatsApp verification

### ✅ Flexible Usage

- Run complete pipeline or individual steps
- Command-line arguments for different areas and business types
- Custom search queries: `{search_type} near {area}, {city}, {country}`
- Optional WhatsApp verification

## 🛠️ Technical Details

### Dependencies

- **Selenium**: Web automation and scraping
- **webdriver-manager**: Automatic Chrome driver management
- **Standard libraries**: csv, os, sys, logging, re, socket

### Browser Requirements

- Chrome browser installed
- Automatic driver download via webdriver-manager

### Network Requirements

- Internet connection for Google Maps access
- DNS resolution for wa.me (WhatsApp verification)

## 📝 Usage Examples

### Scrape Multiple Areas and Business Types

```bash
# Hotels in different areas
python scripts/run_scraping_pipeline.py "Ikeja"
python scripts/run_scraping_pipeline.py "Ikorodu"
python scripts/run_scraping_pipeline.py "Victoria Island"

# Different business types in same area
python scripts/run_scraping_pipeline.py "Ikeja" "restaurants"
python scripts/run_scraping_pipeline.py "Ikeja" "banks"
python scripts/run_scraping_pipeline.py "Ikeja" "pharmacies"

# Custom locations
python scripts/run_scraping_pipeline.py "Victoria Island" "hotels" "Lagos" "Nigeria"
```

### Check Logs

```bash
# View recent logs
tail -f logs/pipeline_hotels_Ikeja.log
tail -f logs/pipeline_restaurants_Ikeja.log
```

### Data Analysis

The CSV files can be opened in Excel, Google Sheets, or analyzed with Python pandas for further processing.

## ⚠️ Important Notes

1. **Rate Limiting**: The tool includes delays between requests to be respectful to Google's servers
2. **Network Issues**: If WhatsApp verification fails, check your internet connection and DNS settings
3. **Browser Automation**: Chrome will open automatically during scraping - don't close it
4. **Data Persistence**: WhatsApp verification results are appended, not overwritten

## 🐛 Troubleshooting

### Common Issues

1. **"Search box not found"**

   - Google Maps layout may have changed
   - Check logs for detailed error information

2. **"Network connectivity check failed"**

   - Check internet connection
   - Try different DNS servers
   - Check firewall settings

3. **"Chrome driver not found"**
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

### Debug Mode

Enable detailed logging by modifying the logging level in the scripts:

```python
setup_logging('debug.log', level=logging.DEBUG)
```

## 📄 License

This project is for educational and research purposes. Please respect Google's terms of service and use responsibly.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
 