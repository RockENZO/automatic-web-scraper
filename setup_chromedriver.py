#!/usr/bin/env python3
"""
ChromeDriver Setup Utility for Automatic Web Scraper
This script helps diagnose and fix ChromeDriver compatibility issues.
"""

import subprocess
import sys
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_chrome_version():
    """Get the installed Chrome browser version."""
    try:
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        result = subprocess.run([chrome_path, "--version"], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
        return None

def setup_chromedriver():
    """Setup and test ChromeDriver."""
    print("🔧 Setting up ChromeDriver...")
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✅ Chrome version: {chrome_version}")
    else:
        print("❌ Could not detect Chrome version")
        return False
    
    # Download compatible ChromeDriver
    try:
        print("📥 Downloading compatible ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
    except Exception as e:
        print(f"❌ Error downloading ChromeDriver: {e}")
        return False
    
    # Test ChromeDriver
    try:
        print("🧪 Testing ChromeDriver...")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        print("✅ ChromeDriver test successful!")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def main():
    """Main function."""
    print("🤖 ChromeDriver Setup Utility")
    print("=" * 40)
    
    if setup_chromedriver():
        print("\n🎉 ChromeDriver setup completed successfully!")
        print("You can now run the web scraper without ChromeDriver issues.")
    else:
        print("\n💥 ChromeDriver setup failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
