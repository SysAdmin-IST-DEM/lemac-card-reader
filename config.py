from dotenv import load_dotenv
import os
from importlib.metadata import version

load_dotenv()

VERSION = "1.1.0"
BASE_API_URL = os.getenv("BASE_API_URL")
API_KEY = os.getenv("API_KEY")
LOG_FILE = os.getenv("LOG_FILE")