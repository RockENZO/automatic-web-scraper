"""
Configuration file for the Automatic Web Scraper
"""

# Ollama Model Configuration
OLLAMA_MODEL = "gpt-oss:20b"
OLLAMA_TEMPERATURE = 0.1
OLLAMA_NUM_PREDICT = 1000

# Scraping Configuration
DEFAULT_WAIT_TIME = 5
HEADLESS_BROWSER = True
DEFAULT_CHUNK_SIZE = 6000
MAX_CHUNK_SIZE = 10000
MIN_CHUNK_SIZE = 2000

# Streamlit Configuration
PAGE_TITLE = "Automatic Web Scraper"
PAGE_ICON = "🤖"

# Selenium Configuration
CHROME_DRIVER_PATH = "./chromedriver"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Logging Configuration
LOG_LEVEL = "INFO"
