# Configuration for AI API Test Agent
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration  
BASE_API_URL = "https://jsonplaceholder.typicode.com"
REQUEST_TIMEOUT = 30

# Test Configuration
MAX_RETRIES = 3
USAGE_GUIDE_FILE = "AI_AGENT_USAGE_GUIDE.md"
API_CONTRACTS_FILE = "API_CONTRACTS.md"
