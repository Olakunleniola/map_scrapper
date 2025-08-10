# Map Scraper - Business Data Collection Tool

A comprehensive Python tool for scraping business data from Google Maps. The project is organized in a modular structure for better maintainability and scalability. Supports flexible search queries for any business type and location.

## 🏗️ Project Structure

```bash
Map Scapper/
├── scripts/                    # Main execution scripts
│   ├── scrape_business_list.py    # Phase 1: Extract business names and links
│   ├── extract_business_data.py   # Phase 2: Extract detailed business information
│   └── run_scraping_pipeline.py    # Pipeline runner (currently covers Phases 1–2)
├── lib/                        # Utility libraries
│   ├── selenium_utils.py       # Selenium WebDriver utilities (forces English UI)
│   ├── data_utils.py           # Data handling and CSV/Excel operations
│   └── network_utils.py        # Network connectivity utilities
├── data/                       # Data storage
│   ├── hotels/                 # Hotel data (default business type)
│   │   ├── ikeja/             # Area-specific folders
│   │   │   ├── ikeja_hotels_list.csv
│   │   │   └── ikeja_hotels_data.csv
│   │   └── alimosho/
│   │       ├── alimosho_hotels_list.csv
│   │       └── alimosho_hotels_data.csv
│   └── restaurants/            # Restaurant data
│       └── ikeja/
│           ├── ikeja_restaurants_list.csv
│           └── ikeja_restaurants_data.csv
├── logs/                       # Log files for debugging
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📥 Get the code

### Option A: Fork on GitHub (recommended)

1. Open the repository page on GitHub
2. Click "Fork" to create your own copy
3. Clone your fork locally:

```bash
git clone https://github.com/Olakunleniola/map_scrapper.git
```

```bash
cd map_scapper
```

### Option B: Download as ZIP

1. Click the green "Code" button on the repository page
2. Choose "Download ZIP"
3. Extract the ZIP and open the folder in your editor

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment (choose any name you like)
python -m venv your_env_name

# Activate virtual environment
# Windows (PowerShell):
./your_env_name/Scripts/Activate.ps1
# or (Command Prompt):
your_env_name\Scripts\activate.bat
# Linux/Mac:
source your_env_name/bin/activate

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
```

### 3. Run Individual Steps

```bash
# Step 1: Scrape business list (default: hotels)
python scripts/scrape_business_list.py "Ikeja"

# Step 1: Custom business type
python scripts/scrape_business_list.py "Ikeja" "restaurants"

# Step 1: Full custom search
python scripts/scrape_business_list.py "Victoria Island" "hotels" "Lagos" "Nigeria"

# Step 2: Extract detailed data
python scripts/extract_business_data.py "Ikeja"            # defaults to hotels
python scripts/extract_business_data.py "Ikeja" restaurants
```

## 📊 Data Output

### Business List (Phase 1)

- **File**: `data/{business_type}/{area}/{area}_{business_type}_list.csv`
- **Columns**: `name`, `link`, `search_type`, `area`, `city`, `country`

### Business Details (Phase 2)

- **File**: `data/{business_type}/{area}/{area}_{business_type}_data.csv`
- **Columns**: `name`, `area`, `link`, `address`, `phone`, `website`, `email`, `image`

<!-- WhatsApp verification phase has been removed from the codebase. -->

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
- CSV and Excel file management

### ✅ Flexible Usage

- Run complete pipeline (Phases 1–2) or individual steps
- Command-line arguments for different areas and business types
- Custom search queries: `{search_type} near {area}, {city}, {country}`

## 🛠️ Technical Details

### Dependencies

- **Selenium**: Web automation and scraping
- **webdriver-manager**: Automatic Chrome driver management
- **Standard libraries**: csv, os, sys, logging, re, socket

### Browser Requirements

- Chrome browser installed
- Automatic driver download via webdriver-manager
- WebDriver forces English (en-US) UI via Chrome options and locale override

### Network Requirements

- Internet connection for Google Maps access

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
2. **Browser Automation**: Chrome will open automatically during scraping - don't close it

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
