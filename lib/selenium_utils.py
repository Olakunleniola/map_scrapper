"""
Selenium utility functions for web scraping operations
"""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver(headless=False, maximize=True):
    """
    Setup and configure Chrome WebDriver
    
    Args:
        headless (bool): Run browser in headless mode
        maximize (bool): Maximize browser window
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver
    """
    options = Options()
    
    if headless:
        options.add_argument('--headless')
    
    if maximize:
        options.add_argument('--start-maximized')
    
    # Additional options for stability
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    
    # Set English as default language - comprehensive approach
    options.add_argument('--lang=en-US')
    options.add_argument('--accept-lang=en-US,en;q=0.9')
    options.add_argument('--accept-languages=en-US,en')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-translate-script-url')
    
    # Set language preferences with more comprehensive settings
    prefs = {
        "intl.accept_languages": "en-US,en",
        "profile.default_content_setting_values.notifications": 2,
        "translate": {"enabled": "false"},
        "translate_whitelists": {},
        "translate_blacklists": {},
        "translate_allowlists": {},
        "translate_blocklists": {}
    }
    options.add_experimental_option("prefs", prefs)
    
    # Additional language-related arguments
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Explicitly set language after driver creation
        driver.execute_cdp_cmd('Emulation.setLocaleOverride', {'locale': 'en-US'})
        driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'accuracy': 100
        })
        
        return driver
    except Exception as e:
        logging.error(f"Failed to setup Chrome driver: {e}")
        raise

def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present on the page
    
    Args:
        driver: WebDriver instance
        by: Locator strategy (By.ID, By.CLASS_NAME, etc.)
        value: Locator value
        timeout (int): Maximum time to wait in seconds
    
    Returns:
        WebElement: Found element or None if timeout
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logging.warning(f"Element not found: {by}={value} within {timeout}s")
        return None

def wait_for_element_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable
    
    Args:
        driver: WebDriver instance
        by: Locator strategy
        value: Locator value
        timeout (int): Maximum time to wait in seconds
    
    Returns:
        WebElement: Clickable element or None if timeout
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        logging.warning(f"Element not clickable: {by}={value} within {timeout}s")
        return None

def safe_click(driver, by, value, timeout=10):
    """
    Safely click an element with waiting
    
    Args:
        driver: WebDriver instance
        by: Locator strategy
        value: Locator value
        timeout (int): Maximum time to wait in seconds
    
    Returns:
        bool: True if click successful, False otherwise
    """
    element = wait_for_element_clickable(driver, by, value, timeout)
    if element:
        try:
            element.click()
            return True
        except Exception as e:
            logging.error(f"Failed to click element {by}={value}: {e}")
            return False
    return False

def safe_send_keys(driver, by, value, text, timeout=10):
    """
    Safely send keys to an element with waiting
    
    Args:
        driver: WebDriver instance
        by: Locator strategy
        value: Locator value
        text (str): Text to send
        timeout (int): Maximum time to wait in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    element = wait_for_element(driver, by, value, timeout)
    if element:
        try:
            element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            logging.error(f"Failed to send keys to {by}={value}: {e}")
            return False
    return False

def scroll_to_element(driver, element):
    """
    Scroll to make an element visible
    
    Args:
        driver: WebDriver instance
        element: WebElement to scroll to
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Small delay for scroll to complete
    except Exception as e:
        logging.error(f"Failed to scroll to element: {e}")

def scroll_container(driver, container_selector, scroll_pause=2):
    """
    Scroll a container to load more content
    
    Args:
        driver: WebDriver instance
        container_selector (str): CSS selector for the scrollable container
        scroll_pause (int): Time to wait between scrolls
    
    Returns:
        int: Number of scrolls performed
    """
    scroll_count = 0
    last_height = driver.execute_script(f"return document.querySelector('{container_selector}').scrollHeight")
    
    while True:
        # Scroll down
        driver.execute_script(f"document.querySelector('{container_selector}').scrollTo(0, document.querySelector('{container_selector}').scrollHeight);")
        
        # Wait for new content to load
        time.sleep(scroll_pause)
        
        # Calculate new scroll height
        new_height = driver.execute_script(f"return document.querySelector('{container_selector}').scrollHeight")
        
        # If height is the same, we've reached the bottom
        if new_height == last_height:
            break
            
        last_height = new_height
        scroll_count += 1
        logging.info(f"Scroll {scroll_count}: Loaded more content")
    
    return scroll_count

def handle_cookie_consent(driver, accept_button_selector=None):
    """
    Handle cookie consent popups
    
    Args:
        driver: WebDriver instance
        accept_button_selector (str): CSS selector for accept button
    
    Returns:
        bool: True if handled, False if not found
    """
    # Common cookie consent selectors
    selectors = [
        accept_button_selector,
        'button[aria-label*="Accept"]',
        'button[aria-label*="Accept all"]',
        'button[id*="accept"]',
        'button[class*="accept"]',
        'button:contains("Accept")',
        'button:contains("Accept All")',
        'button:contains("I agree")',
        'button:contains("OK")',
        'button:contains("Got it")'
    ]
    
    for selector in selectors:
        if selector:
            try:
                element = wait_for_element(driver, By.CSS_SELECTOR, selector, timeout=3)
                if element:
                    element.click()
                    logging.info(f"Clicked cookie consent button: {selector}")
                    time.sleep(1)
                    return True
            except Exception as e:
                logging.debug(f"Cookie consent selector {selector} failed: {e}")
                continue
    
    return False 