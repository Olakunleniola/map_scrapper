"""
Network utility functions for connectivity checks and WhatsApp verification
"""
import socket
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def check_network_connectivity(host: str = 'wa.me', port: int = 80, timeout: int = 5) -> bool:
    """
    Check network connectivity to a specific host
    
    Args:
        host (str): Host to check connectivity to
        port (int): Port to check
        timeout (int): Connection timeout in seconds
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Resolve hostname
        socket.gethostbyname(host)
        
        # Test connection
        s = socket.create_connection((host, port), timeout)
        s.close()
        return True
    except Exception as e:
        logging.error(f"Network connectivity check failed for {host}:{port}: {e}")
        return False

def check_whatsapp_number(driver: webdriver.Chrome, phone_number: str) -> bool:
    """
    Check if a phone number is registered on WhatsApp using wa.me
    
    Args:
        driver: WebDriver instance
        phone_number (str): Phone number to check (should be in 234XXXXXXXXX format)
    
    Returns:
        bool: True if number is on WhatsApp, False otherwise
    """
    url = f"https://wa.me/{phone_number}"
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        page_source = driver.page_source
        
        # Check for error messages indicating invalid number
        error_indicators = [
            "Phone number shared via url is invalid",
            "Invalid phone number",
            "Phone number shared via url is not on WhatsApp",
            "This phone number is not registered on WhatsApp"
        ]
        
        for indicator in error_indicators:
            if indicator in page_source:
                return False
        
        # If no error messages found, assume it's valid
        return True
        
    except Exception as e:
        logging.error(f"Error checking WhatsApp for {phone_number}: {e}")
        return False

def check_multiple_network_hosts(hosts: list | None = None) -> dict:
    """
    Check connectivity to multiple hosts
    
    Args:
        hosts (list): List of hosts to check. Default includes common services
    
    Returns:
        dict: Dictionary with host as key and connectivity status as value
    """
    if hosts is None:
        hosts = [
            ('wa.me', 80),
            ('google.com', 80),
            ('web.whatsapp.com', 443)
        ]
    
    results = {}
    
    for host, port in hosts:
        results[f"{host}:{port}"] = check_network_connectivity(host, port)
    
    return results

def diagnose_network_issues() -> dict:
    """
    Perform basic network diagnostics
    
    Returns:
        dict: Diagnostic results
    """
    diagnostics = {
        'connectivity_tests': check_multiple_network_hosts(),
        'dns_resolution': {},
        'recommendations': []
    }
    
    # Test DNS resolution for key domains
    test_domains = ['wa.me', 'google.com', 'web.whatsapp.com']
    
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            diagnostics['dns_resolution'][domain] = {'success': True, 'ip': ip}
        except Exception as e:
            diagnostics['dns_resolution'][domain] = {'success': False, 'error': str(e)}
    
    # Generate recommendations
    if not diagnostics['connectivity_tests'].get('wa.me:80', False):
        diagnostics['recommendations'].append(
            "Cannot connect to wa.me. Check your internet connection and firewall settings."
        )
    
    if not diagnostics['dns_resolution'].get('wa.me', {}).get('success', False):
        diagnostics['recommendations'].append(
            "Cannot resolve wa.me. Check your DNS settings or try using a different DNS server."
        )
    
    if not any(diagnostics['connectivity_tests'].values()):
        diagnostics['recommendations'].append(
            "No network connectivity detected. Check your internet connection."
        )
    
    return diagnostics 