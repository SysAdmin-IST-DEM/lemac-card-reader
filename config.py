from dotenv import load_dotenv
import os

load_dotenv()

LOG_FILE = "/var/log/lemac-card-reader/reader.log"

VERSION = "1.0.0"
BASE_API_URL = os.getenv("BASE_API_URL")
API_KEY = os.getenv("API_KEY")