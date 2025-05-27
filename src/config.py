# Configuration for AI API Test Agent

# Logging Configuration
LOGGING_LEVEL = "WARNING"  # Options: DEBUG, INFO, WARNING, ERROR
VERBOSE_OUTPUT = False     # Set to True for detailed output

# API Configuration  
BASE_API_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT = 30

# AI Configuration
DEFAULT_MODEL = "gpt-4"
TEMPERATURE = 0.1

# Test Configuration
MAX_RETRIES = 3
ENABLE_ALLURE_REPORTING = True
